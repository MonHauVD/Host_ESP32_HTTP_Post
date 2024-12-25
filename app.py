from http.server import BaseHTTPRequestHandler, HTTPServer
from http.server import SimpleHTTPRequestHandler
import os
import sys
hostName = "192.168.0.102"
# hostName = "127.0.0.1"
# hostName = "localhost"
serverPort = 8080

class DualStream:
    def __init__(self, terminal, log_file):
        self.terminal = terminal
        self.log_file = log_file

    def write(self, message):
        self.terminal.write(message)
        self.log_file.write(message)

    def flush(self):
        self.terminal.flush()
        self.log_file.flush()

# Open log file
log_file = open('server.log', 'w')
sys.stdout = DualStream(sys.stdout, log_file)

class MyServer(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # if self.path == '/':
        #     return
        if self.path == '/log':
            return
        super().log_message(format, *args)
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open('server.log', 'r') as file:
                log_content = file.read()
            response = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Hello World</title>
                <script>
                    function fetchLog() {{
                        fetch('/log')
                            .then(response => response.text())
                            .then(data => {{
                                document.getElementById('log').innerText = data;
                            }});
                    }}
                    setInterval(fetchLog, 1000); // Refresh every second
                </script>
            </head>
            <body>
                <h1>Hello World</h1>
                <pre id="log">{log_content}</pre>
            </body>
            </html>
            """
            self.wfile.write(bytes(response, "utf-8"))
        elif self.path == '/log':
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            with open('server.log', 'r') as file:
                log_content = file.read()
            self.wfile.write(bytes(log_content, "utf-8"))
        else:
            return SimpleHTTPRequestHandler.do_GET(self)
    def do_POST(self):
        # content_length = 10
        # try:
        content_length = int(self.headers['Content-Length'])
        # except:
        #     pass
        body = self.rfile.read(content_length)
        print("Body: ", body.decode('utf-8'))
        log_file.flush() 
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        message = "-1"
        if(body.decode('utf-8') == "123"):
            message = "Success 1"
        else:
            message = "Failed 1"

        self.wfile.write(bytes(message, "utf-8"))

if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass
    webServer.server_close()
    print("Server stopped.")
    log_file.close()