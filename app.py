from flask import Flask, redirect, render_template, request, session, url_for
from flask_socketio import SocketIO, emit, send, join_room, leave_room
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
    return render_template('home.html')
    if request.method == 'POST':
        print("hello")
        message = session["username"] + ": " + request.form.get("chat_message")
        messages.append(message)
        return render_template('index.html', messages=messages)

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
    send('received chat message: ' + str(data), broadcast=True)

@socketio.on('connect')
def handle_socket_connect():
    send('Somebody connected ' + str(session), broadcast=True)

@socketio.on('disconnect')
def handle_socket_disconnect():
    send('Somebody disconnected ' + str(session), broadcast=True)

if __name__ == '__main__':
    socketio.run(app, port=4200, debug=True)
