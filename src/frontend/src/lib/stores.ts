import { writable } from 'svelte/store';
import type { Room } from './room';
import { createSocket } from './socket';

export const socket = writable(createSocket());

export const room_store: import('svelte/store').Writable<Room | null> = writable(null);