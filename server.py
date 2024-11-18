from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from game import WitchardGame
import uvicorn
import secrets

app = FastAPI()
games = {}

class GameCreate(BaseModel):
    num_players: int

class PlayerJoin(BaseModel):
    player_name: str
    game_id: str

class GameAction(BaseModel):
    game_id: str
    player_name: str
    action: str
    value: int = None

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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 