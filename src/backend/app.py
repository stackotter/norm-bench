from flask import Flask, request, jsonify
from dataclasses import dataclass
from flask_cors import CORS

from helper import generate_board
from lib import Room

app = Flask(__name__)
CORS(app)

# Global state (don't @ me)

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
    board.print()

    new_room = Room(players, board)
    rooms[room_id] = new_room

    return jsonify({
        "room_id": room_id,
        "width": board.width,
        "height": board.height,
        "words": [{
            "x": word[0],
            "y": word[1],
            "direction": word[2].value,
            "word": word[3]
        } for word in board.words],
        "players": players,
        "letters": board.letters
    })

@app.route("/join_room")
def join_room():
    global rooms

    username = request.args.get("username")
    room_id = request.args.get("room_id")
    
    if username == None or username == "":
        return "Please provide a username", 400
    if room_id == None or not room_id.isdigit():
        return "Please provide a valid room id", 400

    room_id = int(room_id)

    if not room_id in rooms.keys():
        return "Invalid room id (room doesn't exist)", 400

    room = rooms[room_id]

    if username in room.players:
        return "Username is already taken", 400

    room.players.append(username)
    rooms[room_id] = room

    return jsonify({
        "room_id": room_id,
        "width": room.board.width,
        "height": room.board.height,
        "words": [{
            "x": word[0],
            "y": word[1],
            "direction": word[2].value,
            "word": word[3]
        } for word in room.board.words],
        "players": room.players
    })

if __name__ == "__main__":
    app.run("0.0.0.0", port=8081)
