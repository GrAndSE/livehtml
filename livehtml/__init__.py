'''Simple server for live html editing.
'''
import fcntl
import json
import mimetypes
import os
import signal

from tornado import ioloop, web, websocket

mimetypes.init()


class Notifier(object):
    '''Class that sends notifications
    '''
    def __init__(self):
        self.handlers = {}
        self.running = False

    def append(self, handler, file_name):
        '''Add handler that listern for changes in file named file_name
        '''
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
                    _, file_extension = os.path.splitext(file_name)
                    result = {'head': [], 'body': [],
                              'type': mimetypes.types_map[file_extension]}
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
                            result[part].append(line)
                    buff = {name: ''.join(result[name]) for name in result}
                    handler.write_message(json.dumps(buff))
        self.running = False


def init_handler(root_path):
    '''Init file changes handler
    '''
    handler = Notifier()
    signal.signal(signal.SIGIO, handler)
    rfd = os.open(root_path, os.O_RDONLY)
    fcntl.fcntl(rfd, fcntl.F_SETSIG, 0)
    fcntl.fcntl(rfd, fcntl.F_NOTIFY,
                fcntl.DN_MODIFY | fcntl.DN_CREATE | fcntl.DN_MULTISHOT)
    for path in os.listdir(root_path):
        if os.path.isdir(path):
            tfd = os.open(path, os.O_RDONLY)
            fcntl.fcntl(tfd, fcntl.F_SETSIG, 0)
            fcntl.fcntl(tfd, fcntl.F_NOTIFY,
                        fcntl.DN_MODIFY | fcntl.DN_CREATE | fcntl.DN_MULTISHOT)
    return handler


class ChangeWebSocket(websocket.WebSocketHandler):
    '''Web socket that sends the changes
    '''
    def initialize(self, handler):
        '''Init with a file change handler
        '''
        self.handler = handler

    def open(self):
        '''On socket opening
        '''
        print("WebSocket opened")

    def on_message(self, message):
        '''Create a file change handler
        '''
        print('Append to handler', message)
        self.handler.append(self, os.path.realpath('./' + message))

    def on_close(self):
        '''On socket closing
        '''
        print("WebSocket closed")


SCRIPT = '<script type="text/javascript" src="/_scripts/ldws.js"></script>'


class HTMLHandler(web.RequestHandler):
    '''Handle html static context
    '''

    def initialize(self, path):
        '''Set root path
        '''
        self.root_path = path

    def get(self, path):
        '''Get response
        '''
        real_path = os.path.realpath(os.path.join(self.root_path, path))
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


class ScriptHandler(web.RequestHandler):
    '''Handle scripts included
    '''

    def get(self):
        '''Get js response
        '''
        self.set_header('Content-Type', 'text/javascript')
        real_path = os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                  'ldws.js'))
        with open(real_path) as js_file:
            for line in js_file:
                self.write(line)


def start_server(root_path, template_path=None, port=None):
    '''Run the development server
    '''
    handler = init_handler(root_path)
    application = web.Application([
        ('/_channel/', ChangeWebSocket, {'handler': handler}),
        ('/_scripts/jdws.jg', ScriptHandler),
        ('/(.+\.html)', HTMLHandler, {'path': root_path}),
        ('/(.*)', web.StaticFileHandler, {'path': root_path}),
    ], template_path=template_path or root_path)
    application.listen(port or 8888)
    ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    # start server on current path
    start_server(os.path.realpath('.'))
