#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# +------------------------------------------------------------------+
# |             ____ _               _        __  __ _  __           |
# |            / ___| |__   ___  ___| | __   |  \/  | |/ /           |
# |           | |   | '_ \ / _ \/ __| |/ /   | |\/| | ' /            |
# |           | |___| | | |  __/ (__|   <    | |  | | . \            |
# |            \____|_| |_|\___|\___|_|\_\___|_|  |_|_|\_\           |
# |                                                                  |
# | Copyright Mathias Kettner 2014             mk@mathias-kettner.de |
# +------------------------------------------------------------------+
#
# This file is part of Check_MK.
# The official homepage is at http://mathias-kettner.de/check_mk.
#
# check_mk is free software;  you can redistribute it and/or modify it
# under the  terms of the  GNU General Public License  as published by
# the Free Software Foundation in version 2.  check_mk is  distributed
# in the hope that it will be useful, but WITHOUT ANY WARRANTY;  with-
# out even the implied warranty of  MERCHANTABILITY  or  FITNESS FOR A
# PARTICULAR PURPOSE. See the  GNU General Public License for more de-
# ails.  You should have  received  a copy of the  GNU  General Public
# License along with GNU Make; see the file  COPYING.  If  not,  write
# to the Free Software Foundation, Inc., 51 Franklin St,  Fifth Floor,
# Boston, MA 02110-1301 USA.

# ZUTUN:
# - inventory_max_cachefile_age reparieren, entfernen, was weiß ich
# - obsoleten Code rauswerfen
# - evtl. Funtionen aus check_mk.py umziehen


# Function implementing cmk -I and cmk -II. This is directly
# being called from the main option parsing code. The list
# hostnames is already prepared by the main code. If it is
# empty then we use all hosts and switch to using cache files.
def do_discovery(hostnames, check_types, only_new):
    use_caches = False
    if not hostnames:
        verbose("Discovering services on all hosts:\n")
        hostnames = all_hosts_untagged
        use_caches = True
    else:
        verbose("Discovering services on %s:\n" % ", ".join(hostnames))

    # For clusters add their nodes to the list. Clusters itself
    # cannot be discovered but the user is allowed to specify
    # them and we do discovery on the nodes instead.
    nodes = []
    for h in hostnames:
        nodes = nodes_of(h)
        if nodes:
            hostnames += nodes

    # Then remove clusters and make list unique
    hostnames = list(set([ h for h in hostnames if not is_cluster(h) ]))
    hostnames.sort()

    # Now loop through all hosts
    for hostname in hostnames:
        try:
            verbose(tty_white + tty_bold + hostname + tty_normal + ":\n")
            do_discovery_for(hostname, check_types, only_new, use_caches)
            verbose("\n")
        except Exception, e:
            if opt_debug:
                raise
            verbose(" -> Failed: %s\n" % e)


def do_discovery_for(hostname, check_types, only_new, use_caches):
    new_items = discover_services(hostname, check_types, use_caches, use_caches)
    if not check_types and not only_new:
        old_items = [] # do not even read old file
    else:
        old_items = parse_autochecks_file(hostname)

    # There are three ways of how to merge existing and new discovered checks:
    # 1. -II without --checks=
    #        check_types is empty, only_new is False
    #    --> complete drop old services, only use new ones
    # 2. -II with --checks=
    #    --> drop old services of that types
    #        check_types is not empty, only_new is False
    # 3. -I
    #    --> just add new services
    #        only_new is True

    # Parse old items into a dict (ct, item) -> paramstring
    result = {}
    for check_type, item, paramstring in old_items:
        # Take over old items if -I is selected or if -II
        # is selected with --checks= and the check type is not
        # one of the listed ones
        if only_new or (check_types and check_type not in check_types):
            result[(check_type, item)] = paramstring

    stats = {}
    for check_type, item, paramstring in new_items:
        if (check_type, item) not in result:
            result[(check_type, item)] = paramstring
            stats.setdefault(check_type, 0)
            stats[check_type] += 1

    final_items = []
    for (check_type, item), paramstring in result.items():
        final_items.append((check_type, item, paramstring))
    final_items.sort()
    save_autochecks_file(hostname, final_items)

    found_check_types = stats.keys()
    found_check_types.sort()
    if found_check_types:
        for check_type in found_check_types:
            verbose("  %s%3d%s %s\n" % (tty_green + tty_bold, stats[check_type], tty_normal, check_type))
    else:
        verbose("  nothing%s\n" % (only_new and " new" or ""))


def save_autochecks_file(hostname, items):
    if not os.path.exists(autochecksdir):
        os.makedirs(autochecksdir)
    filepath = autochecksdir + "/" + hostname + ".mk"
    out = file(filepath, "w")
    out.write("[\n")
    for entry in items:
        out.write("  (%r, %r, %s),\n" % entry)
    out.write("]\n")


def snmp_scan(hostname, ipaddress):
    # Make hostname globally available for scan functions.
    # This is rarely used, but e.g. the scan for if/if64 needs
    # this to evaluate if_disabled_if64_checks.
    global g_hostname
    g_hostname = hostname

    vverbose("  SNMP scan:")
    if not in_binary_hostlist(hostname, snmp_without_sys_descr):
        sys_descr_oid = ".1.3.6.1.2.1.1.1.0"
        sys_descr = get_single_oid(hostname, ipaddress, sys_descr_oid)
        if sys_descr == None:
            raise MKSNMPError("Cannot fetch system description OID %s" % sys_descr_oid)

    found = []
    for check_type, check in check_info.items():
        if check_type in ignored_checktypes:
            continue
        elif not check_uses_snmp(check_type):
            continue
        basename = check_type.split(".")[0]
        # The scan function should be assigned to the basename, because
        # subchecks sharing the same SNMP info of course should have
        # an identical scan function. But some checks do not do this
        # correctly
        scan_function = snmp_scan_functions.get(check_type,
                snmp_scan_functions.get(basename))
        if scan_function:
            try:
                result = scan_function(lambda oid: get_single_oid(hostname, ipaddress, oid))
                if result is not None and type(result) not in [ str, bool ]:
                    verbose("[%s] Scan function returns invalid type (%s).\n" %
                            (check_type, type(result)))
                elif result:
                    found.append(check_type)
                    vverbose(" " + check_type)
            except:
                pass
        else:
            found.append(check_type)
            vverbose(" " + tty_blue + tty_bold + check_type + tty_normal)

    vverbose("\n")
    found.sort()
    return found



# Changes from previous behaviour
#  - Syntax with hostname/ipaddress has been dropped

# Create a table of autodiscovered services of a host. Do not save
# this table anywhere. Do not read any previously discovered
# services. The table has the following columns:
# 1. Check type
# 2. Item
# 3. Parameter string (not evaluated)
# Arguments:
#   check_types: None -> try all check types, list -> omit scan in any case
#   use_caches: True is cached agent data is being used (for -I without hostnames)
#   do_snmp_scan: True if SNMP scan should be done (WATO: Full scan)
# Error situation (unclear what to do):
# - IP address cannot be looked up
#
# This function does not handle:
# - clusters
# - disabled services
#
# This function *does* handle:
# - disabled check typess
#
def discover_services(hostname, check_types, use_caches, do_snmp_scan):
    ipaddress = lookup_ipaddress(hostname)

    # Check types not specified (via --checks=)? Determine automatically
    if not check_types:
        check_types = []
        if is_snmp_host(hostname):

            # May we do an SNMP scan?
            if do_snmp_scan:
                check_types = snmp_scan(hostname, ipaddress)

            # Otherwise use all check types that we already have discovered
            # previously
            else:
                for check_type, item, params in read_autochecks_of(hostname):
                    if check_type not in check_types and check_uses_snmp(check_type):
                        check_types.append(check_type)

        if is_tcp_host(hostname):
            check_types += discoverable_check_types('tcp')

    # Make hostname available as global variable in discovery functions
    # (used e.g. by ps-discovery)
    global g_hostname
    g_hostname = hostname

    discovered_services = []
    try:
        for check_type in check_types:
            for item, paramstring in discover_check_type(hostname, ipaddress, check_type, use_caches):
                discovered_services.append((check_type, item, paramstring))

        return discovered_services
    except KeyboardInterrupt:
        raise MKGeneralException("Interrupted by Ctrl-C.")


def discover_check_type(hostname, ipaddress, check_type, use_caches):
    # Skip this check type if is ignored for that host
    if service_ignored(hostname, check_type, None):
        return []

    # Skip SNMP checks on non-SNMP hosts
    if check_uses_snmp(check_type) and not is_snmp_host(hostname):
        return []

    try:
        discovery_function = check_info[check_type]["inventory_function"]
        if discovery_function == None:
            discovery_function = no_discovery_possible
    except KeyError:
        raise MKGeneralException("No such check type '%s'" % check_type)

    section_name = check_type.split('.')[0]    # make e.g. 'lsi' from 'lsi.arrays'

    try:
        info = None
        info = get_realhost_info(hostname, ipaddress, section_name,
               use_caches and inventory_max_cachefile_age or 0, ignore_check_interval=True)

    except MKAgentError, e:
        if str(e):
            raise

    except MKSNMPError, e:
        if str(e):
            raise

    if info == None: # No data for this check type
        return []

    # Add information about nodes if check wants this
    if check_info[check_type]["node_info"]:
        if clusters_of(hostname):
            add_host = hostname
        else:
            add_host = None
        info = [ [add_host] + line for line in info ]

    # Now do the actual inventory
    try:
        # Convert with parse function if available
        if section_name in check_info: # parse function must be define for base check
            parse_function = check_info[section_name]["parse_function"]
            if parse_function:
                info = check_info[section_name]["parse_function"](info)

        # Check number of arguments of discovery function. Note: This
        # check for the legacy API will be removed after 1.2.6.
        if len(inspect.getargspec(discovery_function)[0]) == 2:
            discovered_items = discovery_function(check_type, info) # discovery is a list of pairs (item, current_value)
        else:
            # New preferred style since 1.1.11i3: only one argument: info
            discovered_items = discovery_function(info)

        # tolerate function not explicitely returning []
        if discovered_items == None:
            discovered_items = []

        # New yield based api style
        elif type(discovered_items) != list:
            discovered_items = list(discovered_items)

        result = []
        for entry in discovered_items:
            if not isinstance(entry, tuple):
                sys.stderr.write("%s: Check %s returned invalid discovery data (entry not a tuple): %r\n" %
                                                                     (hostname, check_type, repr(entry)))
                continue

            if len(entry) == 2: # comment is now obsolete
                item, paramstring = entry
            else:
                try:
                    item, comment, paramstring = entry
                except ValueError:
                    sys.stderr.write("%s: Check %s returned invalid discovery data (not 2 or 3 elements): %r\n" %
                                                                           (hostname, check_type, repr(entry)))
                    continue

            description = service_description(check_type, item)
            # make sanity check
            if len(description) == 0:
                sys.stderr.write("%s: Check %s returned empty service description - ignoring it.\n" %
                                                (hostname, check_type))
                continue

            result.append((item, paramstring))

    except Exception, e:
        if opt_debug:
            sys.stderr.write("Exception in discovery function of check type %s\n" % check_type)
            raise
        if opt_verbose:
            sys.stderr.write("%s: Invalid output from agent or invalid configuration: %s\n" % (hostname, e))
        return []

    return result



def discoverable_check_types(what): # snmp, tcp, all
    check_types = [ k for k in check_info.keys()
                   if check_info[k]["inventory_function"] != None
                   and (what == "all"
                        or check_uses_snmp(k) == (what == "snmp"))
                 ]
    check_types.sort()
    return check_types

# Creates a table of all services that a host has or could have according
# to service discovery. The result is a dictionary of the form
# (check_type, item) -> (check_source, paramstring)
# check_source is the reason/state/source of the service:
#    "new"           : Check is discovered but currently not yet monitored
#    "old"           : Check is discovered and already monitored (most common)
#    "vanished"      : Check had been discovered previously, but item has vanished
#    "legacy"        : Check is defined via legacy_checks
#    "active"        : Check is defined via active_checks
#    "custom"        : Check is defined via custom_checks
#    "manual"        : Check is a manual Check_MK check without service discovery
#    "ignored"       : discovered or static, but disabled via ignored_services
#    "obsolete"      : Discovered by vanished check is meanwhile ignored via ignored_services
#    "clustered_new" : New service found on a node that belongs to a cluster
#    "clustered_old" : Old service found on a node that belongs to a cluster
# This function is cluster-aware
def get_host_services(hostname, use_caches, do_snmp_scan):
    if is_cluster(hostname):
        return get_cluster_services(hostname, use_caches, do_snmp_scan)
    else:
        return get_node_services(hostname, use_caches, do_snmp_scan)

# Part of get_node_services that deals with discovered services
def get_discovered_services(hostname, use_caches, do_snmp_scan):
    # Create a dict from check_type/item to check_source/paramstring
    services = {}

    # Handle discovered services -> "new"
    new_items = discover_services(hostname, None, use_caches, do_snmp_scan)
    for check_type, item, paramstring in new_items:
       services[(check_type, item)] = ("new", paramstring)

    # Match with existing items -> "old" and "vanished"
    old_items = parse_autochecks_file(hostname)
    for check_type, item, paramstring in old_items:
        if (check_type, item) not in services:
            services[(check_type, item)] = ("vanished", paramstring)
        else:
            services[(check_type, item)] = ("old", paramstring)

    return services

# Do the actual work for a non-cluster host or node
def get_node_services(hostname, use_caches, do_snmp_scan):
    services = get_discovered_services(hostname, use_caches, do_snmp_scan)

    # Identify clustered services
    for (check_type, item), (check_source, paramstring) in services.items():
        descr = service_description(check_type, item)
        if hostname != host_of_clustered_service(hostname, descr):
            if check_source == "vanished":
                del services[(check_type, item)] # do not show vanished clustered services here
            else:
                services[(check_type, item)] = ("clustered_" + check_source, paramstring)

    merge_manual_services(services, hostname)
    return services

# To a list of discovered services add/replace manual and active
# checks and handle ignoration
def merge_manual_services(services, hostname):
    # Find manual checks. These can override discovered checks -> "manual"
    manual_items = get_check_table(hostname, skip_autochecks=True)
    for (check_type, item), (params, descr, deps) in manual_items.items():
        services[(check_type, item)] = ('manual', repr(params) )

    # Add legacy checks -> "legacy"
    legchecks = host_extra_conf(hostname, legacy_checks)
    for cmd, descr, perf in legchecks:
        services[('legacy', descr)] = ('legacy', 'None')

    # Add custom checks -> "custom"
    custchecks = host_extra_conf(hostname, custom_checks)
    for entry in custchecks:
        services[('custom', entry['service_description'])] = ('custom', 'None')

    # Similar for 'active_checks', but here we have parameters
    for acttype, rules in active_checks.items():
        act_info = active_check_info[acttype]
        entries = host_extra_conf(hostname, rules)
        for params in entries:
            descr = act_info["service_description"](params)
            services[(acttype, descr)] = ('active', repr(params))

    # Handle disabled services -> "obsolete" and "ignored"
    for (check_type, item), (check_source, paramstring) in services.items():
        descr = service_description(check_type, item)
        if service_ignored(hostname, check_type, descr):
            if check_source == "vanished":
                new_source = "obsolete"
            else:
                new_source = "ignored"
            services[(check_type, item)] = (new_source, paramstring)

    return services

# Do the work for a cluster
def get_cluster_services(hostname, use_caches, with_snmp_scan):
    nodes = nodes_of(hostname)

    # Get services of the nodes. We are only interested in "old", "new" and "vanished"
    # From the states and parameters of these we construct the final state per service.
    cluster_items = {}
    for node in nodes:
        services = get_discovered_services(node, use_caches, with_snmp_scan)
        for (check_type, item), (check_source, paramstring) in services.items():
            descr = service_description(check_type, item)
            if hostname == host_of_clustered_service(node, descr):
                if (check_type, item) not in cluster_items:
                    cluster_items[(check_type, item)] = (check_source, paramstring)
                else:
                    first_check_source, first_paramstring = cluster_items[(check_type, item)]
                    if first_check_source == "old":
                        pass
                    elif check_source == "old":
                        cluster_items[(check_type, item)] = (check_source, paramstring)
                    elif first_check_source == "vanished" and check_source == "new":
                        cluster_items[(check_type, item)] = ("old", first_paramstring)
                    elif check_source == "vanished" and first_check_source == "new":
                        cluster_items[(check_type, item)] = ("old", paramstring)
                    # In all other cases either both must be "new" or "vanished" -> let it be

    # Now add manual and active serivce and handle ignored services
    merge_manual_services(cluster_items, hostname)
    return cluster_items


# Get the list of service of a host or cluster and guess the current state of
# all services if possible
def get_check_preview(hostname, use_caches, do_snmp_scan):
    services = get_host_services(hostname, use_caches, do_snmp_scan)
    if is_cluster(hostname):
        ipaddress = None
    else:
        ipaddress = lookup_ipaddress(hostname)

    leave_no_tcp = True # FIXME TODO

    table = []
    for (check_type, item), (check_source, paramstring) in services.items():
        params = None
        if check_source not in [ 'legacy', 'active', 'custom' ]:
            # apply check_parameters
            try:
                if type(paramstring) == str:
                    params = eval(paramstring)
                else:
                    params = paramstring
            except:
                raise MKGeneralException("Invalid check parameter string '%s'" % paramstring)

            descr = service_description(check_type, item)
            global g_service_description
            g_service_description = descr
            infotype = check_type.split('.')[0]

            # Sorry. The whole caching stuff is the most horrible hack in
            # whole Check_MK. Nobody dares to clean it up, YET. But that
            # day is getting nearer...
            global opt_use_cachefile
            old_opt_use_cachefile = opt_use_cachefile
            opt_use_cachefile = True
	    if not leave_no_tcp:
	        opt_no_tcp = True
            opt_dont_submit = True

            if check_type not in check_info:
                continue # Skip not existing check silently

            try:
                exitcode = None
                perfdata = []
                info = get_host_info(hostname, ipaddress, infotype)
            # Handle cases where agent does not output data
            except MKAgentError, e:
                exitcode = 3
                output = "Error getting data from agent"
                if str(e):
                    output += ": %s" % e
                tcp_error = output

            except MKSNMPError, e:
                exitcode = 3
                output = "Error getting data from agent for %s via SNMP" % infotype
                if str(e):
                    output += ": %s" % e
                snmp_error = output

            except Exception, e:
                exitcode = 3
                output = "Error getting data for %s: %s" % (infotype, e)
                if check_uses_snmp(check_type):
                    snmp_error = output
                else:
                    tcp_error = output

            opt_use_cachefile = old_opt_use_cachefile

            if exitcode == None:
                check_function = check_info[check_type]["check_function"]
                if check_source != 'manual':
                    params = compute_check_parameters(hostname, check_type, item, params)

                try:
                    reset_wrapped_counters()
                    result = convert_check_result(check_function(item, params, info), check_uses_snmp(check_type))
                    if last_counter_wrap():
                        raise last_counter_wrap()
                except MKCounterWrapped, e:
                    result = (None, "WAITING - Counter based check, cannot be done offline")
                except Exception, e:
                    if opt_debug:
                        raise
                    result = (3, "UNKNOWN - invalid output from agent or error in check implementation")
                if len(result) == 2:
                    result = (result[0], result[1], [])
                exitcode, output, perfdata = result
        else:
            descr = item
            exitcode = None
            output = "WAITING - %s check, cannot be done offline" % check_source.title()
            perfdata = []

        if check_source == "active":
            params = eval(paramstring)

        if check_source in [ "legacy", "active", "custom" ]:
            checkgroup = None
            if service_ignored(hostname, None, descr):
                check_source = "ignored"
        else:
            checkgroup = check_info[check_type]["group"]

        table.append((check_source, check_type, checkgroup, item, paramstring, params, descr, exitcode, output, perfdata))

    return table



def automation_try_discovery_node(hostname, clustername, leave_no_tcp=False, with_snmp_scan=False):

    global opt_use_cachefile, opt_no_tcp, opt_dont_submit

    try:
        ipaddress = lookup_ipaddress(hostname)
    except:
        raise MKAutomationError("Cannot lookup IP address of host %s" % hostname)

    found_services = []

    dual_host = is_snmp_host(hostname) and is_tcp_host(hostname)

    # if we are using cache files, then we restrict us to existing
    # check types. SNMP scan is only done without the --cache option
    snmp_error = None
    if is_snmp_host(hostname):
        try:
            if not with_snmp_scan:
                existing_checks = set([ cn for (cn, item) in get_check_table(hostname) ])
                for cn in inventorable_checktypes("snmp"):
                    if cn in existing_checks:
                        found_services += make_inventory(cn, [hostname], check_only=True, include_state=True)
            else:
                if not in_binary_hostlist(hostname, snmp_without_sys_descr):
                    sys_descr = get_single_oid(hostname, ipaddress, ".1.3.6.1.2.1.1.1.0")
                    if sys_descr == None:
                        raise MKSNMPError("Cannot get system description via SNMP. "
                                          "SNMP agent is not responding. Probably wrong "
                                          "community or wrong SNMP version. IP address is %s" %
                                           ipaddress)

                found_services = do_snmp_scan([hostname], True, True)

        except Exception, e:
            if not dual_host:
                raise
            snmp_error = str(e)

    tcp_error = None

    # Honor piggy_back data, even if host is not declared as TCP host
    if is_tcp_host(hostname) or \
           get_piggyback_info(hostname) or get_piggyback_info(ipaddress):
        try:
            for cn in inventorable_checktypes("tcp"):
                found_services += make_inventory(cn, [hostname], check_only=True, include_state=True)
        except Exception, e:
            if not dual_host:
                raise
            tcp_error = str(e)

    if dual_host and snmp_error and tcp_error:
        raise MKAutomationError("Error using TCP (%s)\nand SNMP (%s)" %
                (tcp_error, snmp_error))

    found = {}
    for hn, ct, item, paramstring, state_type in found_services:
       found[(ct, item)] = (state_type, paramstring)

    # Check if already in autochecks (but not found anymore)
    if hostname == clustername: # no cluster situation
        for ct, item, params in read_autochecks_of(hostname):
            if (ct, item) not in found:
                found[(ct, item)] = ('vanished', repr(params) ) # This is not the real paramstring!

    # Find manual checks
    existing = get_check_table(clustername, skip_autochecks = hostname != clustername)
    for (ct, item), (params, descr, deps) in existing.items():
        if (ct, item) not in found:
            found[(ct, item)] = ('manual', repr(params) )

    # Add legacy checks and active checks with artificial type 'legacy'
    legchecks = host_extra_conf(clustername, legacy_checks)
    for cmd, descr, perf in legchecks:
        found[('legacy', descr)] = ('legacy', 'None')

    # Add custom checks and active checks with artificial type 'custom'
    custchecks = host_extra_conf(clustername, custom_checks)
    for entry in custchecks:
        found[('custom', entry['service_description'])] = ('custom', 'None')

    # Similar for 'active_checks', but here we have parameters
    for acttype, rules in active_checks.items():
        act_info = active_check_info[acttype]
        entries = host_extra_conf(clustername, rules)
        for params in entries:
            descr = act_info["service_description"](params)
            found[(acttype, descr)] = ( 'active', repr(params) )


    if not table and (tcp_error or snmp_error):
        error = ""
        if snmp_error:
            error = "Error getting data via SNMP: %s" % snmp_error
        if tcp_error:
            if error:
                error += ", "
            error += "Error getting data from Check_MK agent: %s" % tcp_error
        raise MKAutomationError(error)

    return table

