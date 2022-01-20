import { writable } from 'svelte/store';
import type { Room } from './room';

export const room_store: import('svelte/store').Writable<Room | null> = writable(null);