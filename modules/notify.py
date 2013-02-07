#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
# +------------------------------------------------------------------+
# |             ____ _               _        __  __ _  __           |
# |            / ___| |__   ___  ___| | __   |  \/  | |/ /           |
# |           | |   | '_ \ / _ \/ __| |/ /   | |\/| | ' /            |
# |           | |___| | | |  __/ (__|   <    | |  | | . \            |
# |            \____|_| |_|\___|\___|_|\_\___|_|  |_|_|\_\           |
# |                                                                  |
# | Copyright Mathias Kettner 2013             mk@mathias-kettner.de |
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

# Environment macros are turned of due to Livestatus. So we
# need to go the hard (but efficient) way of using command line
# arguments. Fetching things via Livestatus would be possible
# but might introduce problems (for example race conditions).

# Specify a command that reads a mail body from stdin (an UTF-8
# encoded one) and can use any of the variables contact, email,
# hostname, servicedesc, hoststate, servicestate, output in
# the form %(variable)s

# Default settings
notification_logdir = var_dir + "/notify"
notification_log = notification_logdir + "/notify.log"
notification_logging = 0
notification_log_template = \
    u"$CONTACTNAME$ - $NOTIFICATIONTYPE$ - " \
    u"$HOSTNAME$ $HOSTSTATE$ - " \
    u"$SERVICEDESC$ $SERVICESTATE$ "

notification_mail_command = u"mail -s '$SUBJECT$' '$CONTACTEMAIL$'"
notification_host_subject = u"Check_MK: $HOSTNAME$ - $NOTIFICATIONTYPE$"
notification_service_subject = u"Check_MK: $HOSTNAME$/$SERVICEDESC$ $NOTIFICATIONTYPE$"

notification_common_body = u"""Host:     $HOSTNAME$
Alias:    $HOSTALIAS$
Address:  $HOSTADDRESS$
"""

notification_host_body = u"""State:    $LASTHOSTSTATE$ -> $HOSTSTATE$ ($NOTIFICATIONTYPE$)
Command:  $HOSTCHECKCOMMAND$
Output:   $HOSTOUTPUT$
Perfdata: $HOSTPERFDATA$
$LONGHOSTOUTPUT$
"""

notification_service_body = u"""Service:  $SERVICEDESC$
State:    $LASTSERVICESTATE$ -> $SERVICESTATE$ ($NOTIFICATIONTYPE$)
Command:  $SERVICECHECKCOMMAND$
Output:   $SERVICEOUTPUT$
Perfdata: $SERVICEPERFDATA$
$LONGSERVICEOUTPUT$
"""

test_vars = {
  'host': {
    'NOTIFY_CONTACTEMAIL': 'lm@mathias-kettner.de',
    'NOTIFY_CONTACTNAME': 'lm',
    'NOTIFY_CONTACTPAGER': '',
    'NOTIFY_DATE': '2013-01-17',
    'NOTIFY_HOSTADDRESS': '127.0.0.1',
    'NOTIFY_HOSTALIAS': 'localhost',
    'NOTIFY_HOSTCHECKCOMMAND': 'check-mk-ping',
    'NOTIFY_HOSTDOWNTIME': '0',
    'NOTIFY_HOSTNAME': 'localhost',
    'NOTIFY_HOSTNOTIFICATIONNUMBER': '1',
    'NOTIFY_HOSTOUTPUT': 'Manually set to Down by lm',
    'NOTIFY_HOSTPERFDATA': '',
    'NOTIFY_HOSTPROBLEMID': '136',
    'NOTIFY_HOSTSTATE': 'DOWN',
    'NOTIFY_HOSTSTATEID': '1',
    'NOTIFY_HOSTTAGS': 'cmk-agent prod lan tcp wato /wato/',
    'NOTIFY_LASTHOSTSTATE': 'UP',
    'NOTIFY_LASTHOSTSTATECHANGE': '1358761208',
    'NOTIFY_LASTHOSTSTATECHANGE_REL': '0d 00:11:38',
    'NOTIFY_LOGDIR': '/omd/sites/event/var/check_mk/notify',
    'NOTIFY_LONGDATETIME': 'Thu Jan 17 15:28:13 CET 2013',
    'NOTIFY_LONGHOSTOUTPUT': '',
    'NOTIFY_NOTIFICATIONTYPE': 'PROBLEM',
    'NOTIFY_PARAMETERS': '',
    'NOTIFY_SHORTDATETIME': '2013-01-17 15:28:13',
    'NOTIFY_WHAT': 'HOST',
    'NOTIFY_OMD_ROOT': '/omd/sites/event',
    'NOTIFY_OMD_SITE': 'event',
    'NOTIFY_MAIL_COMMAND': 'mail -s \'$SUBJECT$\' \'$CONTACTEMAIL$\'',
  },
  'service': {
    'NOTIFY_CONTACTEMAIL': 'lm@mathias-kettner.de',
    'NOTIFY_CONTACTNAME': 'lm',
    'NOTIFY_CONTACTPAGER': '',
    'NOTIFY_DATE': '2013-01-17',
    'NOTIFY_HOSTADDRESS': '127.0.0.1',
    'NOTIFY_HOSTALIAS': 'localhost',
    'NOTIFY_HOSTCHECKCOMMAND': 'check-mk-ping',
    'NOTIFY_HOSTDOWNTIME': '0',
    'NOTIFY_HOSTNAME': 'localhost',
    'NOTIFY_HOSTNOTIFICATIONNUMBER': '0',
    'NOTIFY_HOSTOUTPUT': 'OK - 127.0.0.1: rta 0.028ms, lost 0%',
    'NOTIFY_HOSTPERFDATA': 'rta=0.028ms;200.000;500.000;0; pl=0%;40;80;; rtmax=0.052ms;;;; rtmin=0.021ms;;;;',
    'NOTIFY_HOSTPROBLEMID': '0',
    'NOTIFY_HOSTSTATE': 'UP',
    'NOTIFY_HOSTSTATEID': '0',
    'NOTIFY_HOSTTAGS': 'cmk-agent prod lan tcp wato /wato/',
    'NOTIFY_LASTHOSTSTATE': 'UP',
    'NOTIFY_LASTHOSTSTATECHANGE': '1358761208',
    'NOTIFY_LASTHOSTSTATECHANGE_REL': '0d 00:11:38',
    'NOTIFY_LASTSERVICESTATE': 'OK',
    'NOTIFY_LASTSERVICESTATECHANGE': '1358761208',
    'NOTIFY_LASTSERVICESTATECHANGE_REL': '0d 00:00:01',
    'NOTIFY_LOGDIR': '/omd/sites/event/var/check_mk/notify',
    'NOTIFY_LONGDATETIME': 'Thu Jan 17 15:31:46 CET 2013',
    'NOTIFY_LONGHOSTOUTPUT': '',
    'NOTIFY_LONGSERVICEOUTPUT': '',
    'NOTIFY_NOTIFICATIONTYPE': 'PROBLEM',
    'NOTIFY_PARAMETERS': '',
    'NOTIFY_SERVICECHECKCOMMAND': 'check_mk-cpu.loads',
    'NOTIFY_SERVICEDESC': 'CPU load',
    'NOTIFY_SERVICENOTIFICATIONNUMBER': '1',
    'NOTIFY_SERVICEOUTPUT': 'CRIT - 15min load 1.29 at 2 CPUs (critical at 0.00)',
    'NOTIFY_SERVICEPERFDATA': 'load1=1.35;0;0;0;2 load5=1.33;0;0;0;2 load15=1.29;0;0;0;2',
    'NOTIFY_SERVICEPROBLEMID': '137',
    'NOTIFY_SERVICESTATE': 'CRITICAL',
    'NOTIFY_SERVICESTATEID': '2',
    'NOTIFY_SHORTDATETIME': '2013-01-17 15:31:46',
    'NOTIFY_WHAT': 'SERVICE',
    'NOTIFY_OMD_ROOT': '/omd/sites/event',
    'NOTIFY_OMD_SITE': 'event',
    'NOTIFY_MAIL_COMMAND': 'mail -s \'$SUBJECT$\' \'$CONTACTEMAIL$\'',
  },
}

g_interactive = False

def set_fake_env(ty, context):
    os.environ.update(test_vars[ty])
    context.update(dict([(k[7:], v) for (k, v) in test_vars[ty].items()]))

def substitute_context(template, context):
    # First replace all known variables
    for varname, value in context.items():
        template = template.replace('$'+varname+'$', value)

    # Remove the rest of the variables and make them empty
    template = re.sub("\$[A-Z]+\$", "", template)
    return template

def notify_log(message):
    if g_interactive or notification_logging >= 1:
        formatted = (u"[%d] " % int(time.time())) + message + "\n"
        if g_interactive:
            sys.stdout.write(formatted.encode("utf-8"))
        else:
            file(notification_log, "a").write(formatted.encode("utf-8"))

def notify_usage():
    sys.stderr.write("""Usage: check_mk --notify
       check_mk --notify fake-service <plugin>
       check_mk --notify fake-host <plugin>

Normally the notify module is called without arguments to send real
notification. But there are situations where this module is called with
COMMANDS to e.g. support development of notification plugins.

Available commands:
    fake-service <plugin> ... Calls the given notification plugin with fake
                              notification data of a service notification.
    fake-host <plugin>    ... Calls the given notification plugin with fake
                              notification data of a host notification.
""")

def get_readable_rel_date(timestamp):
    try:
        change = int(timestamp)
    except:
        change = 0
    rel_time = time.time() - change
    seconds = rel_time % 60
    rem = rel_time / 60
    minutes = rem % 60
    hours = (rem % 1440) / 60
    days = rem / 1440
    return '%dd %02d:%02d:%02d' % (days, hours, minutes, seconds)

def do_notify(args):
    try:
        mode = 'notify'
        if args:
            if len(args) != 2 or args[0] not in ['fake-service', 'fake-host']:
                sys.stderr.write("ERROR: Invalid call to check_mk --notify.\n\n")
                notify_usage()
                sys.exit(1)

            mode, plugin = args
            global g_interactive
            g_interactive = True

        if not os.path.exists(notification_logdir):
            os.makedirs(notification_logdir)

        # Hier müssen wir erstmal rausfinden, an wen die Notifikation gehen soll.
        # Das sollte hoffentlich als Env-Variable da sein. Wenn nicht in check_mk_templates.cfg
        # einbauen. Dann können wir in den Kontaktdefinitionen nachschauen. Diese sollten
        # ja in main.mk/conf.d vorhanden sein. Die neue Notifikationstabelle muss auf jeden
        # fall da rein. Für den Benutzer rufen also diese Tabelle auf. Wenn es die
        # nicht gibt (garkein Eintrag), verfahren wir nach dem alten Verfahren und
        # senden direkt eine Email. Wenn es die Tabelle aber gibt, werten wir
        # Zeile für Zeile aus:
        # - Bestimmen, ob die Zeile aktiv ist. Dazu ist evtl. eine Livestatus-Rückanfrage
        #   notwendig. Das ist nicht optimal, aber zumindest wegen der Timeperiods notwendig.
        # - Wenn aktiv, dann rufen wir das Plugin dazu auf. Dieses hat sich mit einer
        #   Python-Funktion registriert. Wo werden diese definiert? Im precompiled-Fall
        #   brauchen wir das *nicht*. Man könnte die Plugins also einfach nur bei --notify
        #   einlesen. Zeitkritisch ist das nicht sehr, denn Notifikationen sind selten.

        # Information about notification is excpected in the
        # environment in variables with the prefix NOTIFY_
        context = dict([
            (var[7:], value.decode("utf-8"))
            for (var, value)
            in os.environ.items()
            if var.startswith("NOTIFY_")
                and not re.match('^\$[A-Z]+\$$', value)])

        # Add a few further helper variables
        import socket
        context["MONITORING_HOST"] = socket.gethostname()
        if omd_root:
            context["OMD_ROOT"] = omd_root
            context["OMD_SITE"] = os.getenv("OMD_SITE", "")

        context["WHAT"] = "SERVICEDESC" in context and "SERVICE" or "HOST"
        context["MAIL_COMMAND"] = notification_mail_command

        # Handle interactive calls
        if mode == 'fake-service':
            set_fake_env('service', context)
            sys.exit(call_notification_script(plugin, [], context))

        elif mode == 'fake-host':
            set_fake_env('host', context)
            sys.exit(call_notification_script(plugin, [], context))

        context['LASTHOSTSTATECHANGE_REL'] = get_readable_rel_date(context['LASTHOSTSTATECHANGE'])
        if context['WHAT'] != 'HOST':
            context['LASTSERVICESTATECHANGE_REL'] = get_readable_rel_date(context['LASTSERVICESTATECHANGE'])

        if notification_logging >= 2:
            notify_log("Notification context:\n"
                       + "\n".join(["%s=%s" % v for v in sorted(context.items())]))

        if not context:
            sys.stderr.write("check_mk --notify expects context data in environment variables "
                             "that are prefixed with NOTIFY_\n")
            sys.exit(1)

        # Get notification settings for the contact in question - if available.
        method = "email"
        contact = contacts.get(context["CONTACTNAME"])

        try:
            if contact:
                method = contact.get("notification_method")
            else:
                method = 'email'
            if type(method) == tuple and method[0] == 'flexible':
                notify_flexible(contact, context, method[1])
            else:
                notify_via_email(context)

        except Exception, e:
            notify_log("ERROR: %s\n%s" % (e, format_exception()))
            sys.stderr.write("ERROR: %s\n" % e)
            if notification_log:
                sys.stderr.write("Details have been logged to %s.\n" % notification_log)
            sys.exit(1)

    except Exception, e:
        if g_interactive:
            raise
        crash_dir = var_dir + "/notify"
        if not os.path.exists(crash_dir):
            os.makedirs(crash_dir)
        file(crash_dir + "/crash.log", "a").write("CRASH:\n%s\n\n" % format_exception())


def notify_via_email(context):
    notify_log(substitute_context(notification_log_template, context))

    if "SERVICEDESC" in context:
        subject_t = notification_service_subject
        body_t = notification_service_body
    else:
        subject_t = notification_host_subject
        body_t = notification_host_body

    subject = substitute_context(subject_t, context)
    context["SUBJECT"] = subject
    body = substitute_context(notification_common_body + body_t, context)
    command = substitute_context(notification_mail_command, context)
    command_utf8 = command.encode("utf-8")
    if notification_logging >= 2:
        notify_log("Executing command: %s" % command)
    notify_log(body)
    # Make sure that mail(x) is using UTF-8. More then
    # setting the locale cannot be done here. We hope that
    # C.UTF-8 is always available. Please check the output
    # of 'locale -a' on your system if you are curious.
    os.putenv("LANG", "C.UTF-8")
    if notification_logging >= 2:
        file(var_dir + "/notify/body.log", "w").write(body.encode("utf-8"))
    os.popen(command_utf8, "w").write(body.encode("utf-8"))


def notify_flexible(contact, context, notification_table):
    notify_log("Flexible notification for %s" % context["CONTACTNAME"])
    for entry in notification_table:
        plugin = entry["plugin"]
        notify_log("Plugin: %s" % plugin)

        # Check disabling
        if entry.get("disabled"):
            notify_log("- Skipping: it is disabled for this user")
            continue

        # Check host, if configured
        if entry.get("only_hosts"):
            hostname = context.get("HOSTNAME")
            if hostname not in entry["only_hosts"]:
                notify_log(" - Skipping: host '%s' matches non of %s" % (hostname, ", ".join(entry["only_hosts"])))
                continue

        # Check service, if configured
        if entry.get("only_services"):
            servicedesc = context.get("SERVICEDESC")
            if not servicedesc:
                notify_log(" - Skipping: limited to certain services, but this is a host notification")
            for s in entry["only_services"]:
                if re.match(s, servicedesc):
                    break
            else:
                notify_log(" - Skipping: service '%s' matches non of %s" % (
                    servicedesc, ", ".join(entry["only_services"])))
                continue

        # Check notification type
        event, allowed_events = check_notification_type(context, entry["host_events"], entry["service_events"])
        if event not in allowed_events:
            notification_type = context.get("NOTIFICATIONTYPE","")
            notify_log(" - Skipping: wrong notification type %s (%s), only %s are allowed" % 
                (event, notification_type, ",".join(allowed_events)) )
            continue

        # Check notification number (in case of repeated notifications/escalations)
        if "escalation" in entry:
            from_number, to_number = entry["escalation"]
            if context["WHAT"] == "HOST":
                notification_number = int(context.get("HOSTNOTIFICATIONNUMBER", 1))
            else:
                notification_number = int(context.get("SERVICENOTIFICATIONNUMBER", 1))
            if notification_number < from_number or notification_number > to_number:
                notify_log(" - Skipping: notification number %d does not lie in range %d ... %d" %
                    (notification_number, from_number, to_number))
                continue

        if "timeperiod" in entry:
            timeperiod = entry["timeperiod"]
            if timeperiod and timeperiod != "24X7":
                if not check_timeperiod(timeperiod):
                    notify_log(" - Skipping: time period %s is currently not active" % timeperiod)
                    continue

        if plugin is None:
            notify_via_email(context)
        else:
            call_notification_script(plugin, entry.get("parameters", []), context)


def call_notification_script(plugin, parameters, context):
    # Prepare environment
    os.putenv("NOTIFY_PARAMETERS", " ".join(parameters))
    for nr, value in enumerate(parameters):
        os.putenv("NOTIFY_PARAMETER_%d" % (nr + 1), value)
    os.putenv("NOTIFY_LOGDIR", notification_logdir)

    for key in [ 'WHAT', 'OMD_ROOT', 'OMD_SITE',
                 'MAIL_COMMAND', 'LASTHOSTSTATECHANGE_REL' ]:
        if key in context:
            os.putenv('NOTIFY_' + key, context[key])

    # Remove service macros for host notifications
    if context['WHAT'] == 'HOST':
        for key in context.keys():
            if 'SERVICE' in key:
                os.unsetenv('NOTIFY_%s' % key)

    # Remove exceeding arguments from previous plugin calls
    for nr in range(len(parameters)+1, 101):
        name = "NOTIFY_PARAMETER_%d" % nr
        if name in os.environ:
            os.putenv(name, "")

    # Call actual script without any arguments
    if local_notifications_dir:
        path = local_notifications_dir + "/" + plugin
        if not os.path.exists(path):
            path = notifications_dir + "/" + plugin
    else:
        path = notifications_dir + "/" + plugin

    if not os.path.exists(path):
        notify_log("Notification plugin '%s' not found" % plugin)
        notify_log("  not in %s" % notifications_dir)
        if local_notifications_dir:
            notify_log("  and not in %s" % local_notifications_dir)
        return

    notify_log("Executing %s" % path)
    out = os.popen(path + " 2>&1 </dev/null")
    for line in out:
        notify_log("Output: %s" % line.rstrip())
    exitcode = out.close()
    if exitcode: 
        notify_log("Plugin exited with code %d" % (exitcode >> 8))
        return exitcode
    return 0


def check_notification_type(context, host_events, service_events):
    notification_type = context["NOTIFICATIONTYPE"]
    if context["WHAT"] == "HOST":
        allowed_events = host_events
        state = context["HOSTSTATE"]
        events = { "UP" : 'u', "DOWN" : 'd' }
    else:
        allowed_events = service_events
        state = context["SERVICESTATE"]
        events = { "WARNING" : 'w', "CRITICAL" : 'c', "UNKNOWN" : 'u' }

    if notification_type == "PROBLEM":
        event = events[state]
    elif notification_type == "RECOVERY":
        event = 'r'
    elif notification_type in [ "FLAPPINGSTART", "FLAPPINGSTOP", "FLAPPINGDISABLED" ]: 
        event = 'f'
    elif notification_type in [ "DOWNTIMESTART", "DOWNTIMEEND", "DOWNTIMECANCELLED"]:
        event = 's'
    elif notification_type == "ACKNOWLEDGEMENT":
        event = 'x'
    else:
        event = '?'

    return event, allowed_events

def format_exception():
    import traceback, StringIO, sys
    txt = StringIO.StringIO()
    t, v, tb = sys.exc_info()
    traceback.print_exception(t, v, tb, None, txt)
    return txt.getvalue()
