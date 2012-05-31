import pmxbot.pmxbot as pmxbot
import threading
import json
import logging
import requests
import socket
import select
import datetime

log = logging.getLogger(__name__)
config = pmxbot.config
userkeys = {}
url = getattr(config, 'redmine_url', 'Config redmine_url')
eventport = getattr(config, 'redmine_event_port',0)
eventchannel = getattr(config, 'redmine_event_channel','')
redmine_help = {
    'API':'To find your API key, click on "My Account", then click "Show" under the "API Access key" option on the right of the screen',
    'SEARCH':'!rm [search,find,s,f] <issue #>\nAsk pmxbot to lookup an issue for you',
    'REGISTER':'!rm [register,reg,r] <apikey>\nTell pmxbot your API key (private window please!)',
    }

class Redmine(threading.Thread):
    def __init__(self):
        super(Redmine, self).__init__()
        self.daemon = True
        self.events = []
        self.start()

    def find_issue(user, issue_number):
        if user not in userkeys:
            raise AttributeError('Not registered')
        headers = {'X-Redmine-API-Key':userkeys[user]}
        r = requests.get('%s/issues/%d.json' % (url, issue_number), headers=headers)
        if r.status_code == 200:
            return json.JSONDecoder().decode(r.text)
        if r.status_code == 401:
            raise ValueError('Access Denied')
        if r.status_code == 404:
            raise AttributeError('Issue not found')
        else:
            log.warning('Find issue failed with %d' % r.status_code)
            return None

    def register(user, key):
        userkeys[user] = key
        return True

    @classmethod
    def entry(cls):
        config = pmxbot.config
        cls.eventchannel = getattr(config, 'redmine_event_channel','')
        cls.url = getattr(config, 'redmine_url', 'Config redmine_url')
        cls.eventport = getattr(config, 'redmine_event_port',0)

        listener = cls()
        cls.instance = listener
        pmxbot.botbase.execdelay(
                name='redmine',
                channel='#%s' % cls.eventchannel,
                howlong=2,
                doc='Check for new messages from Redmine',
                repeat=True)(listener.handle_messages)

    def handle_messages(self, client, event):
        while self.events:
            event = self.events.pop(0)
            yield "%s %s issue %s(%s): %s" % (event['author'], event['action'], event['id'], event['status'], event['notes'])
            
    def run(self):
        if self.eventport == 0:
            return

        try:
            server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_sock.bind(("", self.eventport))
            server_sock.listen(3)
        except IOError, e:
            log.warning('Failed to start socket: %s' % e)
            return

        sockets = [server_sock]
        while True:
            inp, outp, err = select.select(sockets,[],[])
            for sock in inp:
                if sock == server_sock:
                    csock, address = sock.accept()
                    sockets.append(csock)

                else:
                    receiving = True
                    event = ''
                    while receiving:
                        event += sock.recv(1024)
                        if event:
                            log.info(event)
                            try:
                                obj = json.JSONDecoder().decode(event)
                                self.events.append(obj)
                                receiving = False
                            except ValueError, e:
                                # Didn't receive the full json string yet
                                pass
                            except Exception, e:
                                log.warning(e)
                                receiving = False
                        else:
                            sock.close()
                            sockets.remove(sock)

        sock.close()
        log.warning("Event socket died")
        return
