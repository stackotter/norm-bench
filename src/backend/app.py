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

    # Optional
    seed = uuid.uuid4().hex
    if "seed" in data.keys() and data["seed"] != "":
        seed = data["seed"]
    
    room_id = None
    if len(free_room_ids) != 0:
        room_id = free_room_ids.pop()
    else:
        room_id = next_room_id
        next_room_id += 1

    players = [Player(username, 0)]
    board = generate_board(seed, word_list)

    new_room = Room(players, board, seed, False)
    rooms[room_id] = new_room

    join_room("%d" % room_id)

    emit("room_created", {
        "roomId": room_id,
        "username": username,
        "width": board.width,
        "height": board.height,
        "hasStarted": new_room.has_started,
        "words": [{
            "x": word[0],
            "y": word[1],
            "direction": word[2].value,
            "word": word[3]
        } for word in board.words],
        "players": [{
            "username": player.username,
            "progress": player.progress
        } for player in players],
        "letters": board.letters,
        "seed": seed
    })

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

    emit("joined_room", {
        "roomId": room_id,
        "username": username,
        "width": room.board.width,
        "height": room.board.height,
        "hasStarted": room.has_started,
        "words": [{
            "x": word[0],
            "y": word[1],
            "direction": word[2].value,
            "word": word[3]
        } for word in room.board.words],
        "players": [{
            "username": player.username,
            "progress": player.progress
        } for player in room.players],
        "letters": room.board.letters,
        "seed": room.seed
    })

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

if __name__ == "__main__":
    socketio.run(app, "0.0.0.0", port=int(os.getenv("BACKEND_PORT", "8080")), debug=True)
