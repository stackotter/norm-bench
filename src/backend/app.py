import json
import uuid
import os

from flask import Flask, request, jsonify, session
from dataclasses import dataclass
from flask_cors import CORS
from flask_socketio import SocketIO, send, emit, join_room, leave_room
from flask_session import Session

from helper import generate_board
from lib import Room
from lib.word_list import WordList
from lib.room import Player

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = uuid.uuid4().hex
CORS(app)
Session(app)
socketio = SocketIO(app, cors_allowed_origins="*", manage_session=True)

# Global state (don't @ me)

free_room_ids: list[int] = []
next_room_id = 0

rooms: dict[int,Room] = {}

word_list = WordList.from_file("word_lists/norm_bench.txt")

# Helper

def get_next_room_id() -> int:
    global free_room_ids
    global next_room_id

    room_id = None
    if len(free_room_ids) != 0:
        room_id = free_room_ids.pop()
    else:
        room_id = next_room_id
        next_room_id += 1
    return room_id

# API routes

@socketio.on("create_room")
def create_room_handler(data):
    global rooms

    """Parse request data"""

    letter_count = data.get("letter_count", 7)
    minimum_word_length = data.get("minimum_word_length", 3)
    is_collaborative = data.get("is_collaborative", False)

    if not "username" in data.keys():
        emit("error", "Please supply all fields")
        return

    username = data["username"]
    if username == None or username == "":
        emit("error", "Please provide a username")
        return

    # If values were provided, replace the default values
    seed = uuid.uuid4().hex
    if "seed" in data.keys() and data["seed"] != "":
        seed = data["seed"]

    """Create room"""

    # Generate the board
    board = generate_board(seed, word_list, letter_count, minimum_word_length)
    
    # Create the room
    new_room = Room([Player(username)], board, seed, letter_count=letter_count, minimum_word_length=minimum_word_length, is_collaborative=is_collaborative)
    room_id = get_next_room_id()
    rooms[room_id] = new_room

    # Create the session
    session["username"] = username
    session["room_id"] = room_id

    # Join the room
    join_room("%d" % room_id)
    emit("join_room", new_room.to_json(room_id, username))

@socketio.on("join_room")
def join_room_handler(data):
    global rooms

    """Parse request data"""

    username = data["username"]
    room_id = data["room_id"]
    
    if username == "":
        emit("error", "Please provide a username")
        return
    if not isinstance(room_id, int):
        emit("error", "Please provide a valid room id")
        return

    """Join room"""

    # Check that room
    room = rooms.get(room_id, None)
    if room == None:
        emit("error", "Invalid room id (room doesn't exist)")
        return

    # Check that username isn't taken
    if username in map(lambda player: player.username, room.players):
        emit("error", "Username is already taken")
        return

    # Notify room of the new player
    socketio.emit("new_player", {
        "username": username,
        "progress": 0
    }, to="%d" % room_id)

    # Add player to room
    session["username"] = username
    session["room_id"] = room_id

    room.players.append(Player(username, 0))
    rooms[room_id] = room

    # Join the room
    join_room("%d" % room_id)
    emit("join_room", room.to_json(room_id, username))

@socketio.on("place_word")
def update_progress_handler(data):
    global rooms

    room_id = session["room_id"]
    username = session["username"]

    """Parse request data"""

    word = data["word"]

    # Add the word to the collaborative board
    if rooms[room_id].is_collaborative and not word in rooms[room_id].placed_words:
        rooms[room_id].placed_words.append(word)

    # Increment the player's progress by 1
    progress = 0
    for (i, player) in enumerate(rooms[room_id].players):
        if player.username == username:
            rooms[room_id].players[i].progress += 1
            progress = rooms[room_id].players[i].progress
            break

    # Notify all players of the progress
    emit("progress_update", {
        "username": username,
        "progress": progress,
    }, to="%d" % room_id)

    # Notify collaborative players of the newly found word
    if rooms[room_id].is_collaborative:
        emit("word_placed", {
            "word": word
        }, to="%d" % room_id)

    # If the player has won, notify everyone
    word_count = len(rooms[room_id].board.words)
    if progress == word_count or len(rooms[room_id].placed_words) == word_count:
        emit("game_won", {
            "winner": username
        }, to="%d" % room_id)

@socketio.on("start_game")
def start_game_handler(data):
    global rooms

    room_id = session["room_id"]

    rooms[room_id].has_started = True
    rooms[room_id].start_time = data["time"]

    emit("start_game", {
        "startTime": data["time"]
    }, to="%d" % room_id)

@socketio.on("join_next_room")
def join_next_room_handler(data):
    global rooms
    global word_list
    global free_room_ids

    room_id = session["room_id"]
    username = session["username"]

    # Leave the current room
    leave_room("%d" % room_id)

    # If we're not the first player join the existing next room
    if rooms[room_id].next_room != None:
        new_room_id = rooms[room_id].next_room
        session["room_id"] = new_room_id
        rooms[new_room_id].players.append(Player(username))

        socketio.emit("new_player", {
            "username": username,
            "progress": 0
        }, to="%d" % new_room_id)

        join_room("%d" % new_room_id)

        emit("join_room", rooms[new_room_id].to_json(new_room_id, username))
    # If we're the first player create a new room
    else:
        seed = uuid.uuid4().hex
        letter_count = rooms[room_id].letter_count
        minimum_word_length = rooms[room_id].minimum_word_length
        is_collaborative = rooms[room_id].is_collaborative

        board = generate_board(seed, word_list, letter_count, minimum_word_length)
        new_room = Room([Player(username)], board, seed, letter_count=letter_count, minimum_word_length=minimum_word_length, is_collaborative=is_collaborative)

        new_room_id = get_next_room_id()
        session["room_id"] = new_room_id
        rooms[new_room_id] = new_room
        rooms[room_id].next_room = new_room_id

        join_room("%d" % new_room_id)

        emit("join_room", new_room.to_json(new_room_id, username))

    # If everyone has moved to the next room, mark the room id to be reused
    rooms[room_id].ghost_players.append(username)
    if len(rooms[room_id].ghost_players) == len(rooms[room_id].players):
        rooms.pop(room_id)
        free_room_ids.append(room_id)

if __name__ == "__main__":
    socketio.run(app, "0.0.0.0", port=int(os.getenv("BACKEND_PORT", "8081")), debug=True, keyfile=os.getenv("BACKEND_KEYFILE", None), certfile=os.getenv("BACKEND_CERTFILE", None))
