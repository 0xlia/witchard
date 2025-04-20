<script lang="ts">
	// Use CardDict from lobby or define here
	interface CardDict {
		suit: string | null;
		value: number | string | null;
		display?: string;
	}
	// Use CardDict
	export let suit: string | null;
	export let value: number | string | null;
	export let isTrump: boolean = false;

	function getSuitSymbol(s: string | null): string {
		// console.log(`Card Component: getSuitSymbol called with suit: '${s}', value: ${value}`);
		if (!s) {
			// console.log("Card Component: Suit is null/empty, returning empty string.");
			return ''; 
		}
		switch (s) {
			case '🔴': // Check for direct emoji if server sends it
			case 'Red': 
				return '🔴';
			case '🟡':
			case 'Yellow':
				return '🟡';
			case '🟢':
			case 'Green':
				return '🟢';
			case '🔵':
			case 'Blue':
				return '🔵';
			default:
				// console.log(`Card Component: Unknown suit '${s}', returning empty string.`);
				return ''; 
		}
	}

	// Use CardDict value type
	function getDisplayValue(v: number | string | null): string {
		if (v === null) return '?'; // Handle null value
		if (v === 420) return 'W'; // Witch
		if (v === 0) return 'J'; // Jester
		return String(v);
	}
</script>

<div class="card" class:is-trump={isTrump} class:jester={value === 0} class:witch={value === 420}>
	<span class="value">{getDisplayValue(value)}</span>
	<span class="suit">{getSuitSymbol(suit)}</span>
</div>

<style>
	.card {
		display: inline-flex;
        flex-direction: column;
        justify-content: space-between;
		border: 1px solid #555;
		border-radius: 5px;
		padding: 5px 8px;
		margin: 3px;
		min-width: 40px;
        height: 60px;
		text-align: center;
		background-color: #333;
		color: white;
        font-family: sans-serif;
        font-weight: bold;
        position: relative;
        box-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        cursor: default;
        user-select: none;
	}

    .card.is-trump {
        border: 2px solid gold;
        box-shadow: 0 0 8px gold;
    }

    .value {
        font-size: 1.2em;
        align-self: center;
        margin-top: 5px;
    }

    .suit {
        font-size: 1.4em;
        align-self: center;
        margin-bottom: 2px;
    }

    .jester {
        background-color: #5e2d79; /* Purple */
    }

    .witch {
        background-color: #e11a1a; /* Dark Red */
    }

    /* Add hover effect for playable cards if needed */
    /* .card:hover { ... } */
</style> 