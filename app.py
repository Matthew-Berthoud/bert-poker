import random
from flask import Flask, redirect, render_template, request, session, url_for
from flask_socketio import SocketIO, emit, send, join_room, leave_room
from werkzeug.middleware.proxy_fix import ProxyFix
from string import ascii_uppercase

from utils import login_required

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


@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    session.pop("room", None)
    if request.method == "POST":
        name = session.get("username")
        code = request.form.get("code")
        join = request.form.get("join", False) # either gives empty string or False, so treat as boolean
        create = request.form.get("create", False)
    
        if not name:
            return redirect(url_for("index"))

        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []}
        elif code not in rooms:
            return render_template("home.html", error="Room does not exist.", room_codes=rooms.keys())

        session["room"] = room
        session["username"] = name
        return redirect(url_for("room"))
        
    return render_template("home.html", room_codes=rooms.keys())

@app.route("/room")
@login_required
def room():
    room = session.get("room")
    if room is None or session.get("username") is None or room not in rooms:
        return redirect(url_for("home"))
    return render_template("room.html", code=room, messages=rooms[room]["messages"])

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return

    content = {
        "name": session.get("username"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("username")
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
    name = session.get("username")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} left room {room}")


if __name__ == '__main__':
    socketio.run(app, port=4200, debug=True)
