<script lang="ts">
    import { page } from '$app/stores';
    import { onMount, onDestroy } from 'svelte';
    import { playerName } from '$lib/stores';
    import Card from '$lib/components/Card.svelte';
    import { goto } from '$app/navigation';

    // --- Define types matching SERVER response --- 
    interface CardDict { 
        suit: string | null;
        value: number | string | null;
        display?: string;
    }
    // Interface matching the structure from game.py -> get_player_state
    interface ServerGameState {
        is_your_turn: boolean;
        players: string[]; 
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
        available_actions?: any[]; 
    }

    // Remove old interfaces
    // interface CardData { ... }
    // interface PlayerState { ... }
    // interface GameState { ... }

    const gameId = $page.params.gameId;
    let currentGameState: ServerGameState | null = null; // Use new interface
    let error: string | null = null;
    let isLoading: boolean = true;
    let intervalId: any = null;
    let predictionValue: number = 0;
    let myName: string | null = null;

    playerName.subscribe(value => {
        myName = value;
    });

    async function fetchGameState() {
        if (!myName) {
            console.log("Player name not set yet, skipping fetch.");
            return; 
        }

        try {
            const response = await fetch(`http://localhost:8000/game/${gameId}/state?player_name=${encodeURIComponent(myName)}`);
            if (!response.ok) {
                if (response.status === 404) {
                    error = "Game not found or player not in game.";
                    if (intervalId) clearInterval(intervalId);
                    setTimeout(() => goto('/'), 3000);
                } else {
                    const errorData = await response.json().catch(() => ({ detail: `HTTP error! Status: ${response.status}` }));
                    throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
                }
                return; 
            }
            const newState: ServerGameState = await response.json(); // Use new interface
            currentGameState = newState;
            
            // If somehow we land here and game is not started, go back to lobby
            // Use 'phase' here
            if (currentGameState?.phase === 'not_started') {
                console.warn("Game not started, redirecting to lobby...");
                if (intervalId) clearInterval(intervalId);
                goto(`/lobby/${gameId}`);
                return;
            }
            error = null; 
        } catch (e) {
            console.error("Failed to fetch game state:", e);
            error = e instanceof Error ? e.message : "An unknown error occurred while fetching game state.";
        } finally {
            isLoading = false; 
        }
    }

    async function performAction(actionData: Record<string, any>) {
        if (!myName) {
            error = "Cannot perform action: Player name is missing.";
            return;
        }
        // Find current player name from the players list and index if needed
        // Note: Server already validates turn based on player_name sent in action
        // let currentPlayerName = currentGameState?.players[currentGameState?.current_player_index ?? -1];

        isLoading = true;
        error = null;
        try {
            const response = await fetch('http://localhost:8000/game/action', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    game_id: gameId,
                    player_name: myName, // Server uses this name for validation
                    ...actionData,
                }),
            });
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ detail: `Action failed! Status: ${response.status}` }));
                throw new Error(errorData.detail || `Action failed! Status: ${response.status}`);
            }
            await fetchGameState();
        } catch (e) {
            console.error("Action failed:", e);
            error = e instanceof Error ? e.message : "An unknown error occurred during the action.";
        } finally {
             isLoading = false; // Set loading false after action completes
        }
    }

    // --- Action Handlers - Check PHASE --- 
    function handlePredict() {
        // Check phase and if action is available (server sends available_actions only to current player)
        if (currentGameState?.phase === 'prediction' && currentGameState?.available_actions) {
            performAction({ action: 'predict', prediction: predictionValue });
        }
    }

    function handlePlayCard(cardIndex: number) {
        // Check phase and if action is available
        if (currentGameState?.phase === 'playing' && currentGameState?.available_actions) {
             // Find the action data for play_card (server might send options)
             const playCardAction = currentGameState.available_actions.find(a => a.action === 'play_card');
             // Simple check if card index is valid in hand (server does stricter validation)
             if (playCardAction && cardIndex >= 0 && cardIndex < (currentGameState?.hand?.length ?? 0) ) { 
                 performAction({ action: 'play_card', card_index: cardIndex });
             }
        }
    }

     function handleChooseTrump(suitIndex: number) {
         // Check phase and if action is available
        if (currentGameState?.phase === 'choose_trump' && currentGameState?.available_actions) {
            // const suitChoices = ["Red", "Yellow", "Green", "Blue"]; // Server sends options
            performAction({ action: 'choose_trump', suit_choice: suitIndex });
        }
    }

    // --- Lifecycle --- 
    onMount(() => {
        if (!myName) {
            console.warn("Player name not found on mount, redirecting to lobby.");
            goto(`/lobby/${gameId}`); 
            return;
        }
        fetchGameState(); 
        intervalId = setInterval(fetchGameState, 2000); 

        return () => {
            if (intervalId) clearInterval(intervalId);
        };
    });

    onDestroy(() => {
        if (intervalId) clearInterval(intervalId);
    });

    // --- Computed properties / helpers - UPDATED --- 
    // Use is_your_turn directly from server state
    $: isMyTurn = currentGameState?.is_your_turn ?? false;
    
    // Check phase and available_actions existence for enabling UI elements
    $: canPredict = currentGameState?.phase === 'prediction' && isMyTurn && !!currentGameState?.available_actions;
    $: canPlayCard = currentGameState?.phase === 'playing' && isMyTurn && !!currentGameState?.available_actions;
    $: canChooseTrump = currentGameState?.phase === 'choose_trump' && isMyTurn && !!currentGameState?.available_actions;

    // Helper to get player details (score, prediction, tricks) for display
    // Server doesn't send players as objects, so we extract from other fields
    function getPlayerDisplayData(playerName: string) {
        const score = currentGameState?.scores?.[playerName] ?? 0;
        const prediction = currentGameState?.predictions?.[playerName] ?? null;
        const tricks = currentGameState?.tricks_won?.[playerName] ?? 0;
        return { name: playerName, score, prediction, tricks };
    }
    
    // Derive trump suit from trumpf card object if available
    $: actualTrumpSuit = currentGameState?.trumpf?.suit ?? null;
    
    // Suit options for choose_trump (extract from available_actions if present)
    $: trumpSuitOptions = currentGameState?.available_actions?.find(a => a.action === 'choose_trump')?.options ?? [];

    // Function to find current actor (predictor/player) safely
    function getCurrentActorName(): string {
        if (!currentGameState) return 'player';
        if (currentGameState.phase === 'prediction') {
            return currentGameState.players.find(p => currentGameState!.predictions?.[p] === undefined) ?? 'player';
        }
        if (currentGameState.phase === 'playing' || currentGameState.phase === 'choose_trump') {
             // Attempt to find the player marked as their turn by the server state
             // This relies on is_your_turn being correctly set for only one player at a time
             // Fallback needed if server state isn't perfectly indicative
             // This is a guess, might need refinement based on how server sets `is_your_turn` 
             // or by adding `current_player_name` to server state.
             return currentGameState.players.find(p => currentGameState!.scores?.[p] !== undefined) ?? 'player'; 
        }
        return 'player'; // Default fallback
    }

</script>

<svelte:head>
    <title>Witchard Game: {gameId}</title>
</svelte:head>

<div class="game-container">
    {#if !myName}
        <p>Loading player info...</p> 
    {:else if isLoading && !currentGameState}
        <p>Loading game state...</p>
    {:else if error}
        <p class="error">Error: {error}</p>
    {:else if currentGameState}
        <h1>Witchard Game: {gameId} (Round {currentGameState.round ?? '-'})</h1>
        <!-- Use PHASE -->
        <p>Status: <strong>{currentGameState.phase}</strong></p>

        <!-- Winner display - Add null check -->
        {#if currentGameState.phase === 'game_over'}
             <h2 class="winner-message">Game Over! Winner: {currentGameState.scores ? Object.entries(currentGameState.scores).sort(([,a],[,b]) => b-a)[0]?.[0] : 'Unknown'}</h2>
        {/if}

        <div class="game-layout">
            <!-- Scores - UPDATED to use helper -->
            <div class="scores-area">
                <h2>Scores</h2>
                <ul>
                    {#each currentGameState.players as name (name)}
                        {@const player = getPlayerDisplayData(name)}
                        <!-- Highlight based on is_your_turn for the current player -->
                        <li class:current-player={name === myName && isMyTurn}>
                            {player.name}: {player.score} points
                            {#if currentGameState.phase !== 'not_started' && currentGameState.phase !== 'game_over'}
                                (Predicted: {player.prediction ?? '?'}, Won: {player.tricks})
                            {/if}
                        </li>
                    {/each}
                </ul>
            </div>

            <!-- Game Area (Trump, Trick) - UPDATED -->
            <div class="game-area">
                <!-- Use trumpf field -->
                {#if currentGameState.trumpf}
                    <div class="trump-section">
                        <h3>Trump</h3>
                        <!-- Pass fields from trumpf object -->
                        <Card suit={currentGameState.trumpf.suit} value={currentGameState.trumpf.value} isTrump={true}/>
                        <!-- Actual trump suit derived earlier -->
                        {#if actualTrumpSuit && actualTrumpSuit !== currentGameState.trumpf.suit}
                            <span>Chosen Suit: {actualTrumpSuit}</span>
                        {/if}
                    </div>
                {/if}

                <!-- Use phase -->
                 {#if currentGameState.phase === 'choose_trump'}
                    <div class="action-prompt">
                        <h3>Choose Trump Suit</h3>
                        {#if canChooseTrump}
                            <p>Your turn! Click a suit:</p>
                             <!-- Use options from available_actions -->
                             {#each trumpSuitOptions as suitOption (suitOption.id)}
                                <button class="suit-choice" on:click={() => handleChooseTrump(suitOption.id)} disabled={isLoading}> {suitOption.suit} </button>
                             {/each}
                        {:else}
                             <!-- Use helper function -->
                             <p>Waiting for {getCurrentActorName()} to choose the trump suit...</p>
                        {/if}
                    </div>
                {/if}

                <div class="trick-section">
                    <h3>Current Trick</h3>
                    <!-- Use current_trick field -->
                    {#if currentGameState.current_trick.length > 0}
                        <div class="cards-display">
                        <!-- Need player info associated with card -->
                        <!-- Server state currently doesn't provide player with card in current_trick -->
                        <!-- Displaying cards without player for now -->
                        <!-- Corrected key for loop -->
                        {#each currentGameState.current_trick as card, i (i)} 
                            <div>
                                <Card suit={card.suit} value={card.value} isTrump={card.suit === actualTrumpSuit}/>
                                <!-- <span>{play.player}</span> -->
                            </div>
                        {/each}
                        </div>
                    {:else if currentGameState.phase !== 'game_over' && currentGameState.phase !== 'not_started'}
                        <p>Trick starting soon...</p>
                    {/if}
                </div>
            </div>

            <!-- Player Hand and Actions - UPDATED -->
            <div class="player-area">
                <h2>Your Hand ({myName})</h2>
                <!-- Use hand field -->
                 {#if currentGameState.hand.length > 0}
                    <div class="cards-display hand">
                        <!-- Iterate hand -->
                        {#each currentGameState.hand as card, index (index)} 
                            <button class="card-button" on:click={() => handlePlayCard(index)} disabled={!canPlayCard || isLoading}>
                                <Card suit={card.suit} value={card.value} isTrump={card.suit === actualTrumpSuit}/>
                            </button>
                        {/each}
                    </div>
                 {:else if currentGameState.phase !== 'game_over' && currentGameState.phase !== 'not_started'}
                    <p>Waiting for next round/game start...</p>
                 {/if}

                <!-- Use phase -->
                {#if currentGameState.phase === 'prediction'}
                    <div class="action-prompt">
                        <h3>Make Prediction</h3>
                        {#if canPredict}
                            <p>Your turn! Predict how many tricks you will win:</p>
                            <!-- Extract prediction options -->
                            {@const predictionOptions = currentGameState.available_actions?.find(a => a.action === 'predict')?.options ?? []}
                             <select bind:value={predictionValue} disabled={isLoading}>
                                {#each predictionOptions as option (option)}
                                    <option value={option}>{option}</option>
                                {/each}
                            </select>
                            <!-- <input type="number" bind:value={predictionValue} min="0" max={currentGameState.round ?? 0} disabled={isLoading}/> -->
                            <button on:click={handlePredict} disabled={isLoading}>Submit Prediction</button>
                        {:else}
                            <!-- Use helper function -->
                            <p>Waiting for {getCurrentActorName()} to predict...</p>
                        {/if}
                    </div>
                {/if}

                <!-- Use phase -->
                {#if currentGameState.phase === 'playing'}
                     <div class="action-prompt">
                        {#if canPlayCard}
                            <p>Your turn! Click a card to play.</p>
                        {:else if isMyTurn}
                            <!-- Should not happen if isMyTurn=true and phase=playing, indicates issue -->
                            <p>Waiting for action options...</p> 
                        {:else}
                             <!-- Use helper function -->
                            <p>Waiting for {getCurrentActorName()} to play...</p>
                        {/if}
                    </div>
                {/if}
            </div>
        </div>

    {:else}
        <p>Something went wrong, game state could not be loaded.</p>
    {/if}
</div>

<style>
    .game-container {
        padding: 20px;
        font-family: sans-serif;
        background-color: #282c34; /* Dark background */
        color: #fff;
        min-height: 100vh;
    }

    h1, h2, h3 {
        color: #61dafb; /* Light blue accent */
        text-align: center;
    }
    h3 {
        margin-bottom: 0.5em;
        text-align: left;
    }

    .error {
        color: #ff6b6b; /* Red for errors */
        border: 1px solid #ff6b6b;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .winner-message {
        color: #98c379; /* Green for winner */
        font-size: 1.5em;
        text-align: center;
        margin: 1rem 0;
    }

    .game-layout {
        display: grid;
        grid-template-areas:
            "scores game"
            "player player";
        grid-template-columns: 1fr 2fr;
        gap: 20px;
        margin-top: 20px;
    }

    .scores-area {
        grid-area: scores;
        background-color: #3a3f4a;
        padding: 15px;
        border-radius: 8px;
    }
    .scores-area ul {
        list-style: none;
        padding: 0;
    }
    .scores-area li {
        margin-bottom: 5px;
        padding: 3px;
        border-radius: 3px;
    }
    .scores-area li.current-player {
        font-weight: bold;
        background-color: #4a505c;
    }

    .game-area {
        grid-area: game;
        background-color: #3a3f4a;
        padding: 15px;
        border-radius: 8px;
    }
    
    .trump-section, .trick-section {
        margin-bottom: 20px;
    }
    .trump-section span {
        margin-left: 10px;
        font-style: italic;
    }

    .player-area {
        grid-area: player;
        background-color: #3a3f4a;
        padding: 15px;
        border-radius: 8px;
    }

    .cards-display {
        display: flex;
        flex-wrap: wrap;
        gap: 5px; /* Gap between items */
        margin-bottom: 10px;
    }
    .cards-display.hand {
        min-height: 80px; /* Ensure hand area has some height */
    }
    
    .trick-section .cards-display > div {
        text-align: center;
    }
    .trick-section .cards-display span {
        display: block;
        font-size: 0.8em;
        margin-top: 2px;
        color: #ccc;
    }

    .card-button {
        background: none;
        border: none;
        padding: 0;
        margin: 0;
        cursor: pointer;
        display: inline-block; /* Allows it to sit with other cards */
    }
    .card-button:disabled {
        cursor: not-allowed;
        opacity: 0.6;
    }
    .card-button:not(:disabled):hover > :global(.card) {
        transform: translateY(-5px); /* Lift card on hover */
        box-shadow: 0 5px 15px rgba(0,0,0,0.4);
    }
     :global(.card) { /* Target the Card component globally for transitions */
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
     }

    .action-prompt {
        margin-top: 15px;
        padding: 10px;
        background-color: #4a505c;
        border-radius: 5px;
        text-align: center;
    }
     .action-prompt p {
         margin: 0 0 10px 0;
     }
     .action-prompt input[type="number"],
     .action-prompt select {
        padding: 8px;
        margin-right: 10px;
        border: 1px solid #ccc;
        border-radius: 4px;
        background-color: #eee;
        color: #333;
     }
     .action-prompt button, button {
        padding: 8px 15px;
        border: none;
        border-radius: 4px;
        background-color: #61dafb;
        color: #282c34;
        font-size: 1rem;
        cursor: pointer;
        transition: background-color 0.2s ease;
        margin: 5px;
     }
      .action-prompt button.suit-choice {
          font-size: 1.5em;
          padding: 5px 10px;
      }
     .action-prompt button:hover:not(:disabled), button:hover:not(:disabled) {
        background-color: #21a1f1;
     }
     .action-prompt button:disabled, button:disabled {
         background-color: #555;
         color: #999;
         cursor: not-allowed;
     }

    /* Responsive adjustments if needed */
    @media (max-width: 768px) {
        .game-layout {
            grid-template-areas:
                "scores"
                "game"
                "player";
            grid-template-columns: 1fr;
        }
    }
</style> 