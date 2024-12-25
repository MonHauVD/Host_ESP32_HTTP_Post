from flask import Flask, request, send_file, jsonify
import threading
import time
import sys
import logging
app = Flask(__name__)

class DualStream:
    def __init__(self, terminal, log_file):
        self.terminal = terminal
        self.log_file = log_file
        # self.suppress_terminal = False

    def write(self, message):
        self.terminal.write(message)
        self.log_file.write(message)

    def flush(self):
        self.terminal.flush()
        self.log_file.flush()

# Open log file
log_file = open('server.log', 'w')
dual_stream = DualStream(sys.stdout, log_file)
sys.stdout = dual_stream
sys.stderr = dual_stream

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app.logger.setLevel(logging.ERROR)

@app.before_request
def before_request():
    if request.path == '/log':
        dual_stream.suppress_terminal = True
        

@app.after_request
def after_request(response):
    dual_stream.suppress_terminal = False
    return response

# Serve the main HTML page
@app.route('/')
def index():
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
    return response

# Serve the log file as plain text
@app.route('/log')
def log():
    return send_file('server.log', mimetype='text/plain')

# Handle POST requests
@app.route('/process', methods=['POST'])
def process():
    body = request.data.decode('utf-8')
    print("Body: ", body)
    log_file.flush()
    response_message = "Failed 1"
    if body == "123":
        response_message = "Success 1"
    return response_message

# Background logging thread
# def log_writer():
#     with open('server.log', 'w') as log_file:
#         while True:
#             log_file.write(f"Server running at {time.ctime()}\n")
#             log_file.flush()
#             time.sleep(1)

if __name__ == "__main__":
    # Start a logging thread
    # logging_thread = threading.Thread(target=log_writer, daemon=True)
    # logging_thread.start()

    # Run the Flask server
    app.run(host='192.168.0.102', port=8080)
