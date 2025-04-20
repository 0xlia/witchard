from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from game import WitchardGame
import uvicorn
import secrets

app = FastAPI()
games = {}

# CORS configuration
origins = [
    "http://localhost:5173", # SvelteKit dev server
    "http://localhost:4173", # SvelteKit preview server
    # Add any other origins if necessary (e.g., your deployed frontend URL)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"], # Allow all headers
)

class GameCreate(BaseModel):
    num_players: int

class PlayerJoin(BaseModel):
    player_name: str
    game_id: str

class GameAction(BaseModel):
    game_id: str
    player_name: str
    action: str
    card_index: int = None
    suit_choice: int = None
    prediction: int = None

class GameStart(BaseModel):
    game_id: str

@app.post("/game/create")
async def create_game(game_data: GameCreate):
    if not 3 <= game_data.num_players <= 6:
        raise HTTPException(status_code=400, detail="Spieleranzahl muss zwischen 3 und 6 liegen")
    
    game_id = secrets.token_urlsafe(8)
    games[game_id] = WitchardGame(game_data.num_players)
    
    return {"game_id": game_id}

@app.post("/game/join")
async def join_game(player_data: PlayerJoin):
    if player_data.game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    game = games[player_data.game_id]
    if not game.add_player(player_data.player_name):
        raise HTTPException(status_code=400, detail="Game is already full")
    return {"status": "joined"}

@app.get("/game/{game_id}/state")
async def get_game_state(game_id: str, player_name: str):
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[game_id]
    return game.get_player_state(player_name) 

@app.post("/game/start")
async def start_game(game_data: GameStart):
    if game_data.game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[game_data.game_id]
    if game.num_players != len(game.player_names):
        raise HTTPException(status_code=400, detail="Nicht genügend Spieler um das Spiel zu starten")
    
    game.start_game()
    return {"status": "started"}

@app.post("/game/action")
async def perform_action(action_data: GameAction):
    if action_data.game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[action_data.game_id]
    
    # Check if it's this player's turn
    if game.current_player != action_data.player_name:
        raise HTTPException(status_code=400, detail="Not your turn")
    
    # Process different actions
    if action_data.action == "predict":
        if game.game_phase != "prediction":
            raise HTTPException(status_code=400, detail="Not in prediction phase")
        if action_data.prediction is None:
            raise HTTPException(status_code=400, detail="Prediction value required")
        result = game.make_prediction(action_data.player_name, action_data.prediction)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return {"status": "prediction_made"}
    
    elif action_data.action == "play_card":
        if game.game_phase != "playing":
            raise HTTPException(status_code=400, detail="Not in playing phase")
        if action_data.card_index is None:
            raise HTTPException(status_code=400, detail="Card index required")
        result = game.play_card(action_data.player_name, action_data.card_index)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return {"status": "card_played"}
    
    elif action_data.action == "choose_trump":
        if game.game_phase != "choose_trump":
            raise HTTPException(status_code=400, detail="Not in choose trump phase")
        if action_data.suit_choice is None:
            raise HTTPException(status_code=400, detail="Suit choice required")
        result = game.choose_trump(action_data.player_name, action_data.suit_choice)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        return {"status": "trump_chosen"}
    
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

# --- NEW ENDPOINT for Lobbies --- 
@app.get("/games/lobbies")
async def list_lobbies():
    open_lobbies = []
    for game_id, game in games.items():
        if game.game_phase == "not_started":
            open_lobbies.append({
                "game_id": game_id,
                "num_players_required": game.num_players,
                "current_player_count": len(game.player_names),
                "players": game.player_names # Optional: send player names too
            })
    return open_lobbies
# --- End of New Endpoint ---

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 