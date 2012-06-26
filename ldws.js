(function(context) {
    context.onload = function() {
        var ws = new WebSocket("ws://localhost:8888/_channel/");
        ws.onopen = function() { ws.send(window.location.pathname); };
        ws.onmessage = function(evt) {
            try {
                var data = JSON.parse(evt.data);
                if (data.head && data.head.length > 0) {
                    document.head.innerHTML = data.head;
                }
                if (data.body && data.body.length > 0) {
                    document.body.innerHTML = data.body;
                }
            } catch(e) {
                console.log("Parsing:\\n", evt.data);
                console.error(e);
            }
        };
    };
})(window);
