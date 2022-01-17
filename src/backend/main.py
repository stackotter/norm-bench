from flask import Flask, request, jsonify
from dataclasses import dataclass

from helper import generate_board
from lib import Room

app = Flask(__name__)

# Global state 😬

free_room_ids: list[int] = []
next_room_id = 0

rooms: dict[int,Room] = {}

# API routes

@app.route("/create_room")
def create_room():
    global free_room_ids
    global next_room_id
    global rooms

    username = request.args.get("username")
    if username == None:
        return "Please provide a username", 400
    
    room_id = None
    if len(free_room_ids) != 0:
        room_id = free_room_ids.pop()
    else:
        room_id = next_room_id
        next_room_id += 1

    players = [username]
    board = generate_board()

    new_room = Room(players, board)
    rooms[room_id] = new_room

    return jsonify({
        "room_id": room_id,
        "words": [{
            "x": word[0],
            "y": word[1],
            "direction": word[2].value,
            "word": word[3]
        } for word in board.words]
    })

@app.route("/join_room")
def join_room():
    global rooms

    username = request.args.get("username")
    room_id = request.args.get("room_id")
    
    if username == None:
        return "Please provide a username", 400
    if room_id == None or not room_id.isdigit():
        return "Please provide a valid room_id", 400

    room_id = int(room_id)

    if not room_id in rooms.keys():
        return "Invalid room_id (room doesn't exist)", 400

    room = rooms[room_id]

    return jsonify({
        "room_id": room_id,
        "words": [{
            "x": word[0],
            "y": word[1],
            "direction": word[2].value,
            "word": word[3]
        } for word in room.board.words],
        "players": room.players
    })

app.run("0.0.0.0", port=8080)