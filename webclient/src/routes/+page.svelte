<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount, onDestroy } from 'svelte';

	let numPlayers: number = 3;
	let gameIdToJoin: string = '';
	let isLoadingCreate: boolean = false;
	let isLoadingLobbies: boolean = true;
	let error: string | null = null;
	let lobbiesError: string | null = null;
	let lobbyListInterval: any = null;

	interface LobbyInfo {
		game_id: string;
		num_players_required: number;
		current_player_count: number;
		players: string[];
	}
	let openLobbies: LobbyInfo[] = [];

	async function fetchOpenLobbies() {
		lobbiesError = null;
		try {
			const res = await fetch('http://localhost:8000/games/lobbies');
			if (!res.ok) {
				const errorData = await res.json().catch(() => ({ detail: `Error fetching lobbies. Status: ${res.status}` }));
				throw new Error(errorData.detail || `HTTP error! Status: ${res.status}`);
			}
			openLobbies = await res.json();
		} catch (e) {
			console.error("Failed to fetch lobbies:", e);
			lobbiesError = e instanceof Error ? e.message : "Could not load open games.";
			openLobbies = [];
		} finally {
			isLoadingLobbies = false;
		}
	}

	async function createGame() {
		isLoadingCreate = true;
		error = null;
		try {
			const res = await fetch('http://localhost:8000/game/create', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ num_players: numPlayers })
			});
			if (!res.ok) {
				const errorData = await res.json().catch(() => ({ detail: `HTTP error! status: ${res.status}` }));
				throw new Error(errorData.detail || `HTTP error! status: ${res.status}`);
			}
			const data = await res.json();
			const gameId = data.game_id;
			goto(`/lobby/${gameId}`);
			await fetchOpenLobbies();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Failed to create game';
		} finally {
			isLoadingCreate = false;
		}
	}

	function handleJoinSubmit() {
		if (gameIdToJoin) {
			goto(`/lobby/${gameIdToJoin}`);
		}
	}

	function joinLobbyById(id: string) {
		goto(`/lobby/${id}`);
	}

	onMount(() => {
		fetchOpenLobbies();
		lobbyListInterval = setInterval(fetchOpenLobbies, 5000);
	});

	onDestroy(() => {
		if (lobbyListInterval) {
			clearInterval(lobbyListInterval);
		}
	});
</script>

<svelte:head>
	<title>Witchard - Game Lobby</title>
</svelte:head>

<div class="lobby-container">
	<h1>Witchard Game</h1>

	{#if error}
		<p class="error">Error: {error}</p>
	{/if}

	<div class="manual-actions">
		<div class="action-section">
			<h2>Create New Game</h2>
			<label for="num-players">Number of Players (3-6):</label>
			<input type="number" id="num-players" bind:value={numPlayers} min="3" max="6" />
			<button on:click={createGame} disabled={isLoadingCreate}>
				{isLoadingCreate ? 'Creating...' : 'Create Game'}
			</button>
		</div>

		<div class="action-section">
			<h2>Join Existing Game by ID</h2>
			<form on:submit|preventDefault={handleJoinSubmit}>
				<label for="game-id">Game ID:</label>
				<input type="text" id="game-id" bind:value={gameIdToJoin} required />
				<button type="submit" disabled={!gameIdToJoin}>
					Join Game
				</button>
			</form>
		</div>
	</div>

	<div class="open-lobbies-section">
		<h2>Open Lobbies</h2>
		{#if isLoadingLobbies}
			<p>Loading open games...</p>
		{:else if lobbiesError}
			<p class="error">{lobbiesError}</p>
		{:else if openLobbies.length === 0}
			<p>No open games found. Why not create one?</p>
		{:else}
			<ul class="lobby-list">
				{#each openLobbies as lobby (lobby.game_id)}
					<li>
						<div class="lobby-info">
							<span class="game-id">ID: {lobby.game_id}</span>
							<span class="player-count">Players: {lobby.current_player_count} / {lobby.num_players_required}</span>
						</div>
						<button 
							on:click={() => joinLobbyById(lobby.game_id)} 
							disabled={lobby.current_player_count >= lobby.num_players_required}
						>
							{lobby.current_player_count >= lobby.num_players_required ? 'Full' : 'Join'}
						</button>
					</li>
				{/each}
			</ul>
		{/if}
	</div>
</div>

<style>
	.lobby-container {
		max-width: 800px;
		margin: 2rem auto;
		padding: 2rem;
		border: 1px solid #ccc;
		border-radius: 8px;
		background-color: #f9f9f9;
		font-family: sans-serif;
	}

	h1 {
		text-align: center;
		color: #333;
		margin-bottom: 2rem;
	}

	.manual-actions {
		display: flex;
		gap: 2rem;
		margin-bottom: 2rem;
		justify-content: space-around;
	}

	.manual-actions .action-section {
		flex: 1;
		margin-bottom: 0;
	}

	.action-section {
		margin-bottom: 2rem;
		padding: 1rem;
		border: 1px solid #eee;
		border-radius: 4px;
		background-color: #fff;
	}

	h2 {
		margin-top: 0;
		color: #555;
		text-align: center;
		margin-bottom: 1rem;
		border-bottom: 1px solid #eee;
		padding-bottom: 0.5rem;
	}

	label {
		display: block;
		margin-bottom: 0.5rem;
		font-weight: bold;
	}

	input[type="number"],
	input[type="text"] {
		width: calc(100% - 22px);
		padding: 0.5rem;
		margin-bottom: 1rem;
		border: 1px solid #ccc;
		border-radius: 4px;
	}

	button {
		padding: 0.75rem 1.5rem;
		border: none;
		border-radius: 4px;
		background-color: #007bff;
		color: white;
		font-size: 1rem;
		cursor: pointer;
		transition: background-color 0.2s ease;
		display: block;
		width: 100%;
		box-sizing: border-box;
	}

	button:hover:not(:disabled) {
		background-color: #0056b3;
	}

	button:disabled {
		background-color: #ccc;
		cursor: not-allowed;
	}

	.error {
		color: red;
		margin-bottom: 1rem;
		text-align: center;
		font-weight: bold;
		background-color: #ffebeb;
		padding: 0.5rem;
		border: 1px solid red;
		border-radius: 4px;
	}

	.open-lobbies-section {
		margin-top: 2rem;
		padding: 1.5rem;
		border: 1px solid #eee;
		border-radius: 8px;
		background-color: #fff;
	}

	.lobby-list {
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.lobby-list li {
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding: 0.75rem 1rem;
		border-bottom: 1px solid #f0f0f0;
		margin-bottom: 0.5rem;
		background-color: #fdfdfd;
		border-radius: 4px;
	}

	.lobby-list li:last-child {
		border-bottom: none;
	}

	.lobby-info {
		display: flex;
		flex-direction: column;
	}

	.game-id {
		font-weight: bold;
		font-family: monospace;
		font-size: 0.9em;
		color: #333;
		margin-bottom: 0.25rem;
	}

	.player-count {
		font-size: 0.9em;
		color: #666;
	}

	.lobby-list button {
		width: auto;
		padding: 0.5rem 1rem;
		font-size: 0.9rem;
		margin-left: 1rem;
		background-color: #28a745;
		display: inline-block;
	}

	.lobby-list button:disabled {
		background-color: #aaa;
	}

	.lobby-list button:hover:not(:disabled) {
		background-color: #218838;
	}

	@media (max-width: 600px) {
		.manual-actions {
			flex-direction: column;
		}
		.lobby-list li {
			flex-direction: column;
			align-items: flex-start;
		}
		.lobby-list button {
			margin-top: 0.5rem;
			width: 100%;
			margin-left: 0;
		}
	}
</style>
