from tornado import ioloop, web, websocket


class EchoWebSocket(websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        self.write_message("You said: " + message)

    def on_close(self):
        print("WebSocket closed")


SCRIPT = '''
    <script type="text/javascript">
        var ws = new WebSocket("ws://localhost:8888/_channel/");
        ws.onopen = function() {
           ws.send("Hello, world");
        };
        ws.onmessage = function (evt) {
           alert(evt.data);
        };
    </script>
'''

class MainHandler(web.RequestHandler):
    def get(self, path):
        print self.request.path
        with open('.' + self.request.path) as html_file:
            for line in html_file:
                if '</body>' not in line:
                    self.write(line)
                else:
                    in_body, after_body = line.split('</body>')
                    self.write(in_body)
                    self.write(SCRIPT)
                    self.write('</body>')
                    self.write(after_body)


if __name__ == '__main__':
    application = web.Application([
        ('/_channel/', EchoWebSocket),
        ('/(.+\.html)', MainHandler),
    ], template_path='.')
    application.listen(8888)
    ioloop.IOLoop.instance().start()
