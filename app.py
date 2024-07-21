from flask import Flask, redirect, render_template, request, session, url_for
from flask_socketio import SocketIO, emit, send
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
socketio = SocketIO(app)

# Set the secret key to some random bytes. Keep this really secret!
# Store the oneline file as app.secret, in this same directory
with open('app.secret', 'r') as f:
    app.secret_key = f.readline()

messages = []

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        form_value = request.form.get("submit_button")
        if form_value == "Log out":
            return redirect(url_for('logout'))
        elif form_value == "Chat":
            message = session["username"] + ": " + request.form.get("chat_message")
            messages.append(message)
            return redirect(url_for('index'))
    if 'username' in session:
        return render_template('index.html', messages=messages)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@socketio.on('message')
def chat_message(data):
    print('received chat message: ' + str(data))

@socketio.on('json')
def handle_chat_json(data):
    print('received chat json: ' + data)

@socketio.on('connect')
def handle_socket_connect():
    send('Somebody else connected ' + str(session), broadcast=True)

if __name__ == '__main__':
    socketio.run(app, port=4200, debug=True)
