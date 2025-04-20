<script lang="ts">
    import { page } from '$app/stores';
    import { onMount, onDestroy } from 'svelte';
    import { playerName } from '$lib/stores';
    import { goto } from '$app/navigation';

    // --- Define types matching SERVER response --- 
    interface CardDict { // Type for _card_to_dict output
        suit: string | null;
        value: number | string | null;
        display?: string; // Optional display field if added by server
    }

    // Interface matching the structure from game.py -> get_player_state
    interface ServerGameState {
        is_your_turn: boolean;
        players: string[]; // Array of names
        num_players: number;
        game_started: boolean;
        scores: Record<string, number>;
        round: number;
        trumpf: CardDict | null;
        played_cards: CardDict[];
        current_trick: CardDict[];
        hand: CardDict[];
        phase: string; // Key is 'phase'
        predictions: Record<string, number>;
        tricks_won: Record<string, number>;
        available_actions?: any[]; // Optional, structure varies
    }

    const gameId = $page.params.gameId;
    let lobbyState: ServerGameState | null = null; // Use the new interface
    let error: string | null = null;
    let isLoading: boolean = false;
    let intervalId: any = null;
    let myName: string | null = null;
    let enteredName: string = '';
    let isNameSubmitted: boolean = false;

    // Subscribe to store
    playerName.subscribe(value => {
        myName = value;
        if (myName) {
            isNameSubmitted = true;
        }
    });

    async function submitNameAndJoin() {
        if (!enteredName) {
            error = "Please enter a name.";
            return;
        }
        isLoading = true;
        error = null;
        try {
            const res = await fetch('http://localhost:8000/game/join', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ game_id: gameId, player_name: enteredName })
            });
            if (!res.ok) {
                 const errorData = await res.json().catch(() => ({ detail: `Failed to join. Status: ${res.status}` }));
                throw new Error(errorData.detail || `Failed to join. Status: ${res.status}`);
            }
            await res.json(); 
            playerName.set(enteredName); 
            isNameSubmitted = true;
            await fetchLobbyState(); 
            startPolling(); 
        } catch (e) {
            error = e instanceof Error ? e.message : 'Failed to join game';
            playerName.set(null); 
            isNameSubmitted = false;
        } finally {
            isLoading = false;
        }
    }

    async function fetchLobbyState() {
        if (!myName) {
            return; 
        }
        try {
            const response = await fetch(`http://localhost:8000/game/${gameId}/state?player_name=${encodeURIComponent(myName)}`);
            if (!response.ok) {
                if (response.status === 404) {
                    error = "Lobby/Game not found.";
                    stopPolling();
                } else {
                     const errorData = await response.json().catch(() => ({ detail: `Error fetching lobby state. Status: ${response.status}` }));
                    throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
                }
                return; 
            }
            const newState: ServerGameState = await response.json(); // Use correct type
            lobbyState = newState; 
            error = null; 
        } catch (e) {
            console.error("Failed to fetch lobby state:", e);
            error = e instanceof Error ? e.message : "An unknown error occurred fetching lobby state.";
        }
    }
    
    async function handleStartGame() {
        if (!myName || !canStart) return;
        isLoading = true;
        error = null;
        try {
            const response = await fetch('http://localhost:8000/game/start', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ game_id: gameId })
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: `Failed to start. Status: ${response.status}` }));
                throw new Error(errorData.detail || `Failed to start game! Status: ${response.status}`);
            }
            await fetchLobbyState(); 
        } catch (e) {
            console.error("Start game failed:", e);
            error = e instanceof Error ? e.message : "An unknown error occurred starting the game.";
        } finally {
            isLoading = false;
        }
    }

    function startPolling() {
        if (intervalId) return; 
        if (!myName) return; 
        intervalId = setInterval(fetchLobbyState, 3000); 
        fetchLobbyState(); 
    }

    function stopPolling() {
        if (intervalId) {
            clearInterval(intervalId);
            intervalId = null;
        }
    }

    onMount(() => {
        if (isNameSubmitted) {
            startPolling();
        }
        return stopPolling; 
    });

    // --- Computed properties - UPDATED --- 
    $: isGameFull = lobbyState ? lobbyState.players.length === lobbyState.num_players : false;
    // Check PHASE and ensure players array exists
    $: canStart = lobbyState?.players ? 
                   isGameFull && 
                   lobbyState.players[0] === myName && 
                   lobbyState.phase === 'not_started' 
                   : false;

    // Reactive Navigation - UPDATED to check PHASE
    $: {
        if (lobbyState && lobbyState.phase !== 'not_started') {
            console.log(`Lobby phase changed to ${lobbyState.phase}, navigating to game.`);
            stopPolling(); 
            goto(`/game/${gameId}`);
        }
    }

</script>

<svelte:head>
    <title>Witchard Lobby: {gameId}</title>
</svelte:head>

<div class="lobby-container">
    <h1>Game Lobby: {gameId}</h1>

    {#if error}
        <p class="error">Error: {error}</p>
    {/if}

    {#if !isNameSubmitted}
        <div class="name-entry">
            <h2>Enter Your Name</h2>
            <form on:submit|preventDefault={submitNameAndJoin}>
                <label for="player-name">Name:</label>
                <input type="text" id="player-name" bind:value={enteredName} required disabled={isLoading} />
                <button type="submit" disabled={isLoading || !enteredName}>
                    {isLoading ? 'Joining...' : 'Join Lobby'}
                </button>
            </form>
        </div>
    {:else}
        <div class="lobby-details">
            <h2>Welcome, {myName}!</h2>
            
            {#if lobbyState}
                <p>Waiting for {lobbyState.num_players} players ({lobbyState.players.length}/{lobbyState.num_players})</p>
                <h3>Players Joined:</h3>
                <ul>
                    {#each lobbyState.players as player (player)}
                        <li>{player} {#if player === myName}(You){/if}</li>
                    {/each}
                </ul>

                {#if canStart}
                    <button on:click={handleStartGame} disabled={isLoading}>
                         {isLoading ? 'Starting...' : 'Start Game'}
                    </button>
                {:else if isGameFull && lobbyState.phase === 'not_started'}
                    <p>Waiting for {lobbyState.players[0] || 'host'} to start the game...</p>
                {:else if lobbyState.phase === 'not_started'}
                     <p>Waiting for more players...</p>
                {:else}
                    <p>Game is starting...</p>
                {/if}
            {:else}
                <p>Loading lobby details...</p>
            {/if}
        </div>
    {/if}
</div>

<style>
    .lobby-container {
        max-width: 600px;
        margin: 2rem auto;
        padding: 2rem;
        border: 1px solid #ccc;
        border-radius: 8px;
        background-color: #f0f0f0; 
        font-family: sans-serif;
        color: #333;
    }
    h1, h2, h3 {
        text-align: center;
        color: #333;
    }
    h2 {
        margin-bottom: 1.5rem;
    }
    h3 {
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        text-align: left;
        border-bottom: 1px solid #ddd;
        padding-bottom: 5px;
    }
    .error {
        color: #d8000c;
        background-color: #ffdddd;
        border: 1px solid #fbc7c7;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin-bottom: 1rem;
    }
    .name-entry form, .lobby-details {
        margin-top: 1rem;
        text-align: center;
    }
    label {
        display: block;
        margin-bottom: 0.5rem;
        font-weight: bold;
        text-align: left;
    }
    input[type="text"] {
        width: calc(100% - 22px);
        padding: 0.75rem;
        margin-bottom: 1rem;
        border: 1px solid #ccc;
        border-radius: 4px;
        font-size: 1rem;
    }
    button {
        padding: 0.75rem 1.5rem;
        border: none;
        border-radius: 4px;
        background-color: #28a745; /* Green */
        color: white;
        font-size: 1rem;
        cursor: pointer;
        transition: background-color 0.2s ease;
    }
    button:hover:not(:disabled) {
        background-color: #218838;
    }
    button:disabled {
        background-color: #ccc;
        cursor: not-allowed;
    }
    ul {
        list-style: none;
        padding: 0;
        margin-top: 0.5rem;
        text-align: left;
    }
    li {
        background-color: #fff;
        padding: 8px 12px;
        border: 1px solid #eee;
        border-radius: 4px;
        margin-bottom: 5px;
    }
    .lobby-details p {
        font-size: 1.1em;
        margin-bottom: 1rem;
    }
</style> 