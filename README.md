# Witchard

Wizard but online and with witches

## 🎮 Features

### Schon implementiert
- Grundlegendes [Spielsystem)](https://blog.amigo-spiele.de/content/ap/rule/06900-GB-AmigoRule.pdf)

### Gewünschte Features
- Lobby erstellen und teilen
- Lobby beitreten
- Beobachter Mode um im STream eigene Karten nicht zu leaken
- Chatfunktion
- verschiedene Modi
- Matchmaking

## Flow

1. Create Game 
> curl -X POST http://localhost:8000/game/create \
     -H "Content-Type: application/json" \
     -d '{"num_players": 4}'

2. Join your own game (with the returned game_id)
> curl -X POST http://localhost:8000/game/join \
     -H "Content-Type: application/json" \
     -d '{"game_id": "your_game_id", "player_name": "your_name"}'

3. Start the game
> curl -X POST http://localhost:8000/game/start \
     -H "Content-Type: application/json" \
     -d '{"game_id": "your_game_id"}'

4. Play the game

5. ????

6. Profit