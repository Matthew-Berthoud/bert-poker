import random
from flask import Flask, redirect, render_template, request, session, url_for
from flask_socketio import SocketIO, emit, send, join_room, leave_room
from werkzeug.middleware.proxy_fix import ProxyFix
from string import ascii_uppercase

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
socketio = SocketIO(app)

# Set the secret key to some random bytes. Keep this really secret!
# Store the oneline file as app.secret, in this same directory
with open('app.secret', 'r') as f:
    app.secret_key = f.readline()

rooms = {}

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            break
    return code

@app.route("/", methods=["GET", "POST"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False) # either gives empty string or False, so treat as boolean
        create = request.form.get("create", False)
    
        if not name:
            return render_template("home.html", error="Please enter a name.", code=code, name=name)

        if join != False and not code:
            return render_template("home.html", error="Please enter a room code.", code=code, name=name)

        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []}
        elif code not in rooms:
            return render_template("home.html", error="Room does not exist.", code=code, name=name)

        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))
        
    return render_template("home.html")

@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))
    return render_template("room.html", code=room, messages=rooms[room]["messages"])

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return

    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} left room {room}")


# @app.route('/', methods=['GET', 'POST'])
# def index():
#     return render_template('home.html')
#     if request.method == 'POST':
#         print("hello")
#         message = session["username"] + ": " + request.form.get("chat_message")
#         messages.append(message)
#         return render_template('index.html', messages=messages)

#     if 'username' in session:
#         return render_template('index.html', messages=messages)
#     return redirect(url_for('login'))

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         session['username'] = request.form['username']
#         return redirect(url_for('index'))
#     return render_template('login.html')

# @app.route('/logout', methods=['GET', 'POST'])
# def logout():
#     session.pop('username', None)
#     return redirect(url_for('index'))

# @socketio.on('message')
# def chat_message(data):
#     send('received chat message: ' + str(data), broadcast=True)

# @socketio.on('connect')
# def handle_socket_connect():
#     send('Somebody connected ' + str(session), broadcast=True)

# @socketio.on('disconnect')
# def handle_socket_disconnect():
#     send('Somebody disconnected ' + str(session), broadcast=True)

if __name__ == '__main__':
    socketio.run(app, port=4200, debug=True)
