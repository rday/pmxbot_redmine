import threading
from pmxbot.botbase import command, contains
from . import redmine


@contains("#")
def issue(client, event, channel, nick, rest):
    pass

@command("rm")
def rm(client, event, channel, nick, rest):
    action = rest.split(' ')
    verb = None
    if action[0] in ['search','find','s','f']:
        verb = 'search'
    elif action[0] in ['update','u']:
        verb = 'update'
    elif action[0] in ['register','reg','r']:
        verb = 'register'
    elif action[0] in ['help','h']:
        verb = 'help'

    if verb == 'search':
        try:
            issue = redmine.find_issue(nick, int(action[1]))
            if issue is not None:
                return '%s' % issue
        except ValueError, e:
            return '%s: %s' % (e, redmine.redmine_help['API'])
        except AttributeError, e:
            return e
        except Exception, e:
            return 'Unknown error: %s' % e
    elif verb == 'register':
        try:
            if redmine.register(nick, action[1]) is True:
                return "Thanks %s, you're registered" % nick
            else:
                return "Well %s, this really can't ever happen" % nick
        except Exception, e:
            return 'Unknown error: %s' % e
    elif verb == 'help':
        if len(action) > 1:
            if action[1] in redmine.redmine_help:
                return redmine.redmine_help[action[1]]
            else:
                return 'No help for %s' % action[1]
        else:
            return redmine.redmine_help


def init(bot):
    events = threading.Thread(target=redmine.receive_events, args=(bot,))
    events.start()
