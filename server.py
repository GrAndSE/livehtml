from tornado import ioloop, web, websocket


class EchoWebSocket(websocket.WebSocketHandler):
    def open(self):
        print("WebSocket opened")

    def on_message(self, message):
        self.write_message("You said: " + message)

    def on_close(self):
        print("WebSocket closed")


class MainHandler(web.RequestHandler):
    def get(self):
        print 'MainHandler get'
        self.write('''<!DOCTYPE html>
<html>
<head>
    <title></title>
</head>
<body>
    <script type="text/javascript">
        var ws = new WebSocket("ws://localhost:8888/_channel/");
        ws.onopen = function() {
           ws.send("Hello, world");
        };
        ws.onmessage = function (evt) {
           alert(evt.data);
        };
    </script>
</body>
</html>''')


if __name__ == '__main__':
    application = web.Application([
        ('/_channel/', EchoWebSocket),
        ('/', MainHandler),
    ])
    application.listen(8888)
    ioloop.IOLoop.instance().start()
