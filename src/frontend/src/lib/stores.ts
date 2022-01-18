import { writable } from 'svelte/store';

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
};

export const room_store: import('svelte/store').Writable<Room | null> = writable(null);