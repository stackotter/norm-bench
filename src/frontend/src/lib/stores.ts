import { writable } from 'svelte/store';
import type { Room } from './room';
import io from 'socket.io-client';
import { backendURL } from '$lib/env';

export const socket = writable(io(backendURL));

export const room_store: import('svelte/store').Writable<Room | null> = writable(null);
