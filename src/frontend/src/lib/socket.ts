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

            room.players.sort((firstPlayer, secondPlayer) => { return firstPlayer.progress > secondPlayer.progress ? -1 : 1 });

            return room
        })
    });

    socket.on("start_game", data => {
        if (!isInRoom()) { return }
        room_store.update(room => {
            room.startTime = data.startTime;
            if (!room.hasStarted) {
                room.hasStarted = true;
                goto("/play");
            }
            return room;
        });
    });

    socket.on("game_won", data => {
        if (!isInRoom()) { return }
        room_store.update(room => {
            room.winner = data.winner;
            return room;
        });
    });

    socket.on("word_placed", data => {
        if (!isInRoom()) { return }
        var word = data.word;
        room_store.update(room => {
            room.placedWords.push(word);
            return room;
        });
    })

    socket.on("join_room", json => {
        room_store.set(json);
        if (json.hasStarted) {
            goto("/play");
        } else {
            goto("/lobby");
        }
    });
    
    return socket
}

export const emitProgressUpdate = (word: number) => {
    socket.update(socket => {
        socket.emit("place_word", {
            "word": word,
        });
        return socket;
    });
}