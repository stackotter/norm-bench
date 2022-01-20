export type Word = {
    x: number,
    y: number,
    direction: string,
    word: string,
}

export type Room = {
    username: string,
    players: string[],
    roomId: number,
    words: Word[],
    width: number,
    height: number,
    letters: string[],
    seed: string,
};