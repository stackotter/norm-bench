import io from 'socket.io-client';
import { backendURL } from '$lib/env';
import { room_store, socket } from './stores';
import { goto } from '$app/navigation';

export const isInRoom = () => {
    var isRoomNull;
    room_store.update(room => {
        isRoomNull = room == null || room == undefined;
        return room
    })
    return !isRoomNull
}

const joinRoom = json => {
    room_store.set(json)
    if (json.hasStarted) {
        goto("/play")
    } else {
        goto("/lobby")
    }
}

export const createSocket = () => {
    var socket = io(backendURL);

    socket.on("new_player", player => {
        if (!isInRoom()) { return }
        room_store.update(room => {
            room.players.push(player);
            return room
        });
    });

    socket.on("progress_update", updated_player => {
        if (!isInRoom()) { return }
        room_store.update(room => {
            for (var i = 0; i < room.players.length; i++) {
                if (room.players[i].username == updated_player.username) {
                    room.players[i].progress = updated_player.progress;
                    break
                }
            }

            if (room.isCollaborative) {
                room.placedWords.push(updated_player.word);
            }

            room.players.sort((firstPlayer, secondPlayer) => { return firstPlayer.progress > secondPlayer.progress ? -1 : 1 });

            return room
        })
    });

    socket.on("start_game", () => {
        if (!isInRoom()) { return }
        room_store.update(room => {
            if (!room.hasStarted) {
                room.hasStarted = true;
                goto("/play");
            }
            return room
        });
    });

    socket.on("game_won", data => {
        if (!isInRoom()) { return }
        room_store.update(room => {
            room.winner = data.winner;
            return room
        })
    })

    socket.on("joined_room", joinRoom);

    socket.on("room_created", joinRoom);
    
    return socket
}

export const emitProgressUpdate = (progress: number, username: string, roomId: number, word: number) => {
    socket.update(socket => {
        socket.emit("update_progress", {
            "username": username,
            "room_id": roomId,
            "progress": progress,
            "word": word,
        });
        return socket;
    });
}