from flask import Flask, request, send_file, jsonify, render_template, redirect, url_for, session, flash
import threading
import time
import sys
import logging
app = Flask(__name__)
app.secret_key = 'MONHAUVD121'

from datetime import datetime


# Global variables for pin states
pin_den = 0
pin_dieuhoa = 0

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

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if (username == 'vietdung' and password == '123') or (username == 'theanh' and password == '456'):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))
# Serve the main HTML page

@app.route('/log_checking')
def log_checking():
    if 'username' not in session:
        return redirect(url_for('login'))
    with open('server.log', 'r') as file:
        log_content = file.read()
    return render_template('log_checking.html', log_content=log_content)

# @app.route('/log_checking')
# def index():
#     with open('server.log', 'r') as file:
#         log_content = file.read()
#     response = f"""
#     <!DOCTYPE html>
#     <html lang="en">
#     <head>
#         <meta charset="UTF-8">
#         <meta name="viewport" content="width=device-width, initial-scale=1.0">
#         <title>Hello World</title>
#         <script>
#             function fetchLog() {{
#                 fetch('/log')
#                     .then(response => response.text())
#                     .then(data => {{
#                         document.getElementById('log').innerText = data;
#                     }});
#             }}
#             setInterval(fetchLog, 1000); // Refresh every second
#         </script>
#     </head>
#     <body>
#         <h1>Hello World</h1>
#         <pre id="log">{log_content}</pre>
#     </body>
#     </html>
#     """
#     return response

# Serve the log file as plain text
@app.route('/log')
def log():
    return send_file('server.log', mimetype='text/plain')

# Handle POST requests
@app.route('/process', methods=['POST'])
def process():
    # Get current time
    current_time = datetime.now()
    # Print current time
    current_time.strftime("%Y-%m-%d %H:%M:%S")
    body = request.data.decode('utf-8')
    # print("Body: ", body)
    log_file.flush()
    response_message = str(f"den={pin_den}, dieuhoa={pin_dieuhoa}")
    print(current_time, " - Body: ", body, ", response_message = ", response_message)
    try:
        if "nhietdo" in body and "doAm" in body:
            parts = body.split(", ")
            nhietDo = parts[0].split("=")[1]
            doAm = parts[1].split("=")[1]
            coNguoi = parts[2].split("=")[1]
            # Store the values in a global variable or a database for later use
            app.config['nhietDo'] = nhietDo
            app.config['doAm'] = doAm
            app.config['coNguoi'] = coNguoi
    except:
        pass
    return response_message

# Dashboard route to display the values
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html', pin_den=pin_den, pin_dieuhoa=pin_dieuhoa)

# @app.route('/dashboard')
# def dashboard():
#     return render_template('dashboard.html', pin_den=pin_den, pin_dieuhoa=pin_dieuhoa)
    # nhietDo = app.config.get('nhietDo', 'N/A')
    # doAm = app.config.get('doAm', 'N/A')
    # coNguoi = app.config.get('coNguoi', 'N/A')
    # return render_template_string("""

    # """, pin_den=pin_den, pin_dieuhoa=pin_dieuhoa)
# Endpoint to provide the latest data
@app.route('/data')
def data():
    nhietDo = app.config.get('nhietDo', 'N/A')
    doAm = app.config.get('doAm', 'N/A')
    coNguoi = app.config.get('coNguoi', 'N/A')
    return jsonify(nhietDo=nhietDo, doAm=doAm, coNguoi=coNguoi)

# Endpoint to toggle pin states
@app.route('/toggle_pin', methods=['POST'])
def toggle_pin():
    global pin_den, pin_dieuhoa
    data = request.json
    pin = data.get('pin')
    if pin == 'pin_den':
        pin_den = 1 - pin_den
    elif pin == 'pin_dieuhoa':
        pin_dieuhoa = 1 - pin_dieuhoa
    return jsonify({pin: eval(pin)})


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
