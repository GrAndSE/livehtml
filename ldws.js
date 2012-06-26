(function(context) {
    function randomizedUrl(baseUrl) {
        return baseUrl.split('?')[0] + '?t=' + (new Date()).valueOf();
    }
    function cssReload(link) {
        link.setAttribute('href', randomizedUrl(link.getAttribute('href')));
    }
    function cssReloadAll() {
        var links = document.head.getElementsByTagName('link');
        for (var i = 0; i < links.length; i++) {
            cssReload(links[i]);
        }
    }

    context.onload = function() {
        var ws = new WebSocket("ws://localhost:8888/_channel/");
        ws.onopen = function() {
            ws.send(window.location.pathname);
            var links = document.head.getElementsByTagName('link');
            for (var i = 0; i < links.length; i++) {
                console.log(links[i]);
                ws.send(links[i].getAttribute('href'));
            }
        };
        ws.onmessage = function(evt) {
            try {
                var data = JSON.parse(evt.data);
                console.log(data);
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
