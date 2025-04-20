import { writable } from 'svelte/store';

// Store to hold the current player's name
export const playerName = writable<string | null>(null); 