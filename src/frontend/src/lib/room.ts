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
};