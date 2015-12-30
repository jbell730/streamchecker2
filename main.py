#!/usr/bin/python

from datetime import datetime as dt
from sys import stdout
from requests import get
from time import sleep
from dbus import SessionBus
from multiprocessing import Process, Queue

notification_time = 10# notification display time, in seconds
wait_interval = 360# time between stream checks, in seconds
user_list = [
    'seamlessr',
    'guude',
    'coestar',
    'docm77live',
    'supermcgamer',
    'millbee',
    'anderzel',
    'vintagebeef',
    'mc_arkas',
    'aureylian',
    'pauseunpause',
    'pyropuncher',
    'w92baj'
]
users = {u: [0, ''] for u in user_list}

def send_notification(title, text, display_time):
    knotify = SessionBus().get_object("org.kde.knotify", "/Notify")
    notif = knotify.event("warning", "kde", [], title, u"%s" % text, [], [], 0, 0, dbus_interface="org.kde.KNotify")
    sleep(display_time)
    knotify.closeNotification(notif)
    knotify = None

def check_stream(u, q):
    #print('[%s] Checking %s...' % (dt.now().strftime('%I:%M:%p'), u))
    user_request = get('https://api.twitch.tv/kraken/streams/%s' % u, headers={'Client-ID': 'streamchecker-linux.py'})
    if not user_request.status_code == 200:
        return 'Unable to get page (err: %s)' % user_request.status_code
    user_info = user_request.json()
    if users[u][0] == 1 and user_info['stream'] and not users[u][1] == user_info['stream']['created_at']:
        q.put({u: [0, '']})
    if users[u][0] == 0 and user_info['stream']:
        user_display = get('http://api.twitch.tv/channels/%s' % u).json()['display_name']
        send_notification('User Streaming', '%s is streaming!' % user_display, notification_time)
        print('[%s] %s is streaming!' % (dt.now().strftime('%I:%M %p'), user_display))
        q.put({u: [1, user_info['stream']['created_at']]})

if __name__ == '__main__':
    while True:
        try:
            q = Queue()
            procs = []
            for u in user_list:
                p = Process(target=check_stream, args=(u, q,))
                procs.append(p)
                p.start()
            sleep(wait_interval)
            while not q.empty():
                users.update(q.get())
            for p in procs:
                p.terminate()
        except KeyboardInterrupt:
            print('Received KeyboardInterrupt...')
            sleep(0.5)
            break
