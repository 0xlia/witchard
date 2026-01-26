# Witchard Game Server Documentation

## Overview

Witchard is a trick-taking card game implemented as a RESTful API server. Players can create games, join existing games, make predictions, and play cards through API endpoints. The game is fully playable via HTTP requests (e.g., using curl).

## Game Mechanics

### Cards
- **Suits**: 🔴 Red, 🟡 Yellow, 🟢 Green, 🔵 Blue
- **Special Cards**:
  - **Jester (value 0)**: Lowest card, always loses a trick
  - **Witch (value 420)**: Highest card, always wins a trick
  - **Regular Cards**: Values 1-13 in each suit

### Game Flow
1. At the start of each round, players are dealt cards (number of cards equals the round number)
2. A trump card is revealed (which makes that suit stronger)
3. Players make predictions about how many tricks they'll win
4. Players take turns playing cards, following suit if possible
5. Scores are calculated based on prediction accuracy

### Scoring
- Correct prediction: 20 points + (10 points × tricks won)
- Incorrect prediction: -10 points × the difference between predicted and actual tricks

### Game Phases
- `not_started`: Game created but not yet started
- `choose_trump`: Waiting for a player to choose trump (if a Witch was revealed)
- `prediction`: Players are making predictions
- `playing`: Players are playing cards
- `round_end`: End of a round, calculating scores
- `game_over`: Game has concluded

## API Endpoints

### Game Creation and Management

#### Create Game
```
POST /game/create
{
  "num_players": 3-6
}
```
Response:
```
{
  "game_id": "<unique_id>"
}
```

#### Join Game
```
POST /game/join
{
  "game_id": "<game_id>",
  "player_name": "<name>"
}
```
Response:
```
{
  "status": "joined"
}
```

#### Start Game
```
POST /game/start
{
  "game_id": "<game_id>"
}
```
Response:
```
{
  "status": "started"
}
```

### Game State and Actions

#### Get Game State
```
GET /game/{game_id}/state?player_name={player_name}
```
Response includes:
- Current game state
- Player's hand
- Current trick
- Scores
- Available actions for the player

#### Perform Action
```
POST /game/action
{
  "game_id": "<game_id>",
  "player_name": "<name>",
  "action": "<action_type>",
  ...additional parameters
}
```

The `action` field can be one of:

1. **predict**
```
{
  "game_id": "<game_id>",
  "player_name": "<name>",
  "action": "predict",
  "prediction": <number>
}
```

2. **play_card**
```
{
  "game_id": "<game_id>",
  "player_name": "<name>",
  "action": "play_card",
  "card_index": <index>
}
```

3. **choose_trump**
```
{
  "game_id": "<game_id>",
  "player_name": "<name>",
  "action": "choose_trump",
  "suit_choice": <0-3>
}
```

## Playing the Game with curl

### Example Game Flow

1. Create a game:
```
curl -X POST -H "Content-Type: application/json" -d '{"num_players": 3}' http://localhost:8000/game/create
```

2. Join with players:
```
curl -X POST -H "Content-Type: application/json" -d '{"game_id": "<game_id>", "player_name": "Player1"}' http://localhost:8000/game/join
```

3. Start the game:
```
curl -X POST -H "Content-Type: application/json" -d '{"game_id": "<game_id>"}' http://localhost:8000/game/start
```

4. Check game state:
```
curl "http://localhost:8000/game/<game_id>/state?player_name=Player1"
```

5. Make prediction:
```
curl -X POST -H "Content-Type: application/json" -d '{"game_id": "<game_id>", "player_name": "Player1", "action": "predict", "prediction": 1}' http://localhost:8000/game/action
```

6. Play a card:
```
curl -X POST -H "Content-Type: application/json" -d '{"game_id": "<game_id>", "player_name": "Player1", "action": "play_card", "card_index": 0}' http://localhost:8000/game/action
```

## Tips for Implementation

- Always check the game state before performing an action to see the available options
- The `available_actions` field in the game state provides information about valid actions for the current player
- The game enforces rules such as following suit and valid prediction values
- Players are identified solely by their name, with no authentication (for simplicity)
