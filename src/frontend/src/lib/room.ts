import { room_store } from "./stores";

export type Word = {
    x: number,
    y: number,
    direction: string,
    word: string,
}

export type Player = {
    username: string,
    progress: number,
}

export type Room = {
    username: string,
    players: Player[],
    roomId: number,
    words: Word[],
    width: number,
    height: number,
    letters: string[],
    seed: string,
    hasStarted: boolean,
    letterCount: number,
    minimumWordLength: number,
    winner?: string,
};

export const shuffleLetters = () => {
    room_store.update(room => {
        while (true) {
            let currentIndex = room.letters.length, randomIndex;

            while (currentIndex != 0) {
                randomIndex = Math.floor(Math.random() * currentIndex);
                currentIndex--;

                [room.letters[currentIndex], room.letters[randomIndex]] = [
                room.letters[randomIndex], room.letters[currentIndex]];
            }

            // Make sure that we don't show them the 7 letter word.
            let isWord = false;
            let shownWord = room.letters.join();
            for (const word of room.words) {
                if (shownWord == word.word) {
                    isWord = true;
                    break
                }
            }

            if (!isWord) {
                break
            }
        }

        return room
    })
}