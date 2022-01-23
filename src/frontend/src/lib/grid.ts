import type { Room, Word } from "./room";

export class Grid {
    rows: string[][];
    placedWords: string[];

    constructor(room: Room) {
        this.rows = [];
        this.placedWords = [];

        for (var y = 0; y < room.height; y++) {
            var row = []
            for (var x = 0; x < room.width; x++) {
                row.push('.'); // '.' means a square where no words go
            }
            this.rows.push(row);
        }

        room.words.forEach(word => {
            this.placeWord(word, true, false);
        });
    }

    setCell(x: number, y: number, value: string) {
        this.rows[y][x] = value;
    }

    placeWord(word: Word, asEmpty: boolean, gaveUp: boolean) {
        if (!asEmpty && !gaveUp) {
            this.placedWords = [...this.placedWords, word.word];
        }

        for (var offset = 0; offset < word.word.length; offset++) {
            if (word.direction == "down") {
                var y = word.y + offset;
                if (gaveUp && this.rows[y][word.x] != " ") {
                    continue
                }
                this.setCell(word.x, y, asEmpty ? " " : (gaveUp ? `|${word.word[offset]}|` : word.word[offset]));
            } else {
                var x = word.x + offset;
                if (gaveUp && this.rows[word.y][x] != " ") {
                    continue
                }
                this.setCell(x, word.y, asEmpty ? " " : (gaveUp ? `|${word.word[offset]}|` : word.word[offset]));
            }
        }
    }
}