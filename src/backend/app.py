import json
import uuid
import os

from flask import Flask, request, jsonify
from dataclasses import dataclass
from flask_cors import CORS
from flask_socketio import SocketIO, send, emit, join_room, leave_room

from helper import generate_board
from lib import Room
from lib.word_list import WordList
from lib.room import Player

app = Flask(__name__)
app.config['SECRET_KEY'] = uuid.uuid4().hex
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*")

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
    global free_room_ids
    global next_room_id
    global rooms

    if not "username" in data.keys():
        emit("error", "Please supply all fields")
        return

    username = data["username"]
    if username == None:
        emit("error", "Please provide a username")
        return

    # Default values
    seed = uuid.uuid4().hex
    letter_count = 7
    minimum_word_length = 3

    # If values were provided, replace the default values
    if "seed" in data.keys() and data["seed"] != "":
        seed = data["seed"]
    if "letter_count" in data.keys():
        letter_count = data["letter_count"]
    if "minimum_word_length" in data.keys():
        minimum_word_length = data["minimum_word_length"]

    # Generate the board
    board = generate_board(seed, word_list, letter_count, minimum_word_length)
    
    # Create the room
    new_room = Room([Player(username)], board, seed, letter_count=letter_count, minimum_word_length=minimum_word_length)
    room_id = get_next_room_id()
    rooms[room_id] = new_room

    # Join the room
    join_room("%d" % room_id)

    # Notify the client
    emit("room_created", new_room.to_json(room_id, username))

@socketio.on("join_room")
def join_room_handler(data):
    global rooms

    if not "username" in data.keys() or not "room_id" in data.keys():
        emit("error", "Please supply all fields")
        return

    username = data["username"]
    room_id = data["room_id"]
    
    if username == None or username == "":
        emit("error", "Please provide a username")
        return
    if not isinstance(room_id, int):
        emit("error", "Please provide a valid room id")
        return

    if not room_id in rooms.keys():
        emit("error", "Invalid room id (room doesn't exist)")
        return

    room = rooms[room_id]

    if username in map(lambda player: player.username, room.players):
        emit("error", "Username is already taken")
        return

    room.players.append(Player(username, 0))
    rooms[room_id] = room

    socketio.emit("new_player", {
        "username": username,
        "progress": 0
    }, to="%d" % room_id)

    join_room("%d" % room_id)

    emit("joined_room", room.to_json(room_id, username))

# TODO: Use session storage instead of relying on the user to tell the truth

@socketio.on("update_progress")
def update_progress_handler(data):
    global rooms

    room_id = data["room_id"]
    username = data["username"]
    progress = data["progress"]

    for (i, player) in enumerate(rooms[room_id].players):
        if player.username == username:
            rooms[room_id].players[i].progress = progress

    emit("progress_update", {
        "username": username,
        "progress": progress
    }, to="%d" % room_id)

    if progress == len(rooms[room_id].board.words):
        emit("game_won", {
            "winner": username
        }, to="%d" % room_id)

@socketio.on("start_game")
def start_game_handler(data):
    global rooms

    room_id = data["room_id"]
    rooms[room_id].has_started = True

    emit("start_game", {}, to="%d" % room_id)

@socketio.on("join_next_room")
def join_next_room_handler(data):
    global rooms
    global word_list

    room_id = data["room_id"]
    username = data["username"]

    leave_room("%d" % room_id)

    if rooms[room_id].next_room != None:
        new_room_id = rooms[room_id].next_room
        rooms[new_room_id].players.append(Player(username))

        socketio.emit("new_player", {
            "username": username,
            "progress": 0
        }, to="%d" % new_room_id)

        join_room("%d" % new_room_id)

        emit("joined_room", rooms[new_room_id].to_json(new_room_id, username))
    else:
        seed = uuid.uuid4().hex
        letter_count = rooms[room_id].letter_count
        minimum_word_length = rooms[room_id].minimum_word_length

        board = generate_board(seed, word_list, letter_count, minimum_word_length)
        new_room = Room([Player(username)], board, seed, letter_count=letter_count, minimum_word_length=minimum_word_length)

        new_room_id = get_next_room_id()
        rooms[new_room_id] = new_room
        rooms[room_id].next_room = new_room_id

        join_room("%d" % new_room_id)

        emit("room_created", new_room.to_json(new_room_id, username))

    # If everyone has moved to the next room, mark the room id to be reused
    rooms[room_id].ghost_players.append(username)
    if len(rooms[room_id].ghost_players) == len(rooms[room_id].players):
        rooms.pop(room_id)
        free_room_ids.append(room_id)

if __name__ == "__main__":
    socketio.run(app, "0.0.0.0", port=int(os.getenv("BACKEND_PORT", "8081")), debug=True, keyfile=os.getenv("BACKEND_KEYFILE", None), certfile=os.getenv("BACKEND_CERTFILE", None))
