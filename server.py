import fcntl
import json
import os
import signal

from tornado import ioloop, web, websocket


class Notifier(object):
    '''Class that sends notifications
    '''
    def __init__(self):
        self.handlers = {}
        self.running = False

    def append(self, handler, file_name):
        self.handlers[file_name] = (os.stat(file_name).st_mtime, handler)

    def __call__(self, signum, frame):
        if self.running:
            return
        self.running = True
        for file_name in self.handlers:
            last_modified, handler = self.handlers[file_name]
            modified = os.stat(file_name).st_mtime
            if last_modified < modified:
                print file_name, 'modified', modified, last_modified
                self.handlers[file_name] = (modified, handler)
                with open(file_name) as file_data:
                    result = {'head': [], 'body': []}
                    part = None
                    for line in file_data:
                        lower_line = line.lower()
                        if not part:
                            if '<head>' in lower_line:
                                part = 'head'
                                _, line = lower_line.split('<head>')
                            elif '<body>' in lower_line:
                                part = 'body'
                                _, line = lower_line.split('<body>')
                        else:
                            if ('</head>' in lower_line or
                                    '</body>' in lower_line):
                                line, _ = lower_line.split('</%s>' %
                                                                 part)
                                result[part].append(line)
                                part = None
                        if part:
                            result[part].append(line);
                    buffer = {name: ''.join(result[name]) for name in result}
                    handler.write_message(json.dumps(buffer))
        self.running = False

handler = Notifier()
signal.signal(signal.SIGIO, handler)
root_path = os.path.realpath('.')
rfd = os.open(root_path, os.O_RDONLY)
fcntl.fcntl(rfd, fcntl.F_SETSIG, 0)
fcntl.fcntl(rfd, fcntl.F_NOTIFY,
            fcntl.DN_MODIFY | fcntl.DN_CREATE | fcntl.DN_MULTISHOT)
for path in os.listdir(root_path):
    if os.path.isdir(path):
        fd = os.open(path, os.O_RDONLY)
        fcntl.fcntl(fd, fcntl.F_SETSIG, 0)
        fcntl.fcntl(fd, fcntl.F_NOTIFY,
                    fcntl.DN_MODIFY | fcntl.DN_CREATE | fcntl.DN_MULTISHOT)


class ChangeWebSocket(websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        '''Create a file change handler
        '''
        print 'Append to handler', message
        handler.append(self, os.path.realpath('./' + message))

    def on_close(self):
        print("WebSocket closed")


SCRIPT = '<script type="text/javascript" src="/ldws.js"></script>'

class HTMLHandler(web.RequestHandler):
    '''Handle html static context
    '''

    def get(self, path):
        real_path = os.path.realpath('./' + path)
        with open(real_path) as html_file:
            for line in html_file:
                if '</head>' not in line:
                    self.write(line)
                else:
                    in_body, after_body = line.split('</head>')
                    self.write(in_body)
                    self.write(SCRIPT)
                    self.write('</head>')
                    self.write(after_body)


if __name__ == '__main__':
    application = web.Application([
        ('/_channel/', ChangeWebSocket),
        ('/(.+\.html)', HTMLHandler),
        ('/(.*)', web.StaticFileHandler, {"path": root_path}),
    ], template_path='.')
    application.listen(8888)
    ioloop.IOLoop.instance().start()
