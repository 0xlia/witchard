import asyncio
import json
from uuid import UUID
from websockets.asyncio.server import serve

from game import WitchardGame

global game

# init new game, add player, return id
def create_new_game(playername, playernumber) -> str:
    game = WitchardGame(int(playernumber))
    game.add_player(playername)
    return str(game.id)

def join_game(playername, gameid):
    pass



async def handler(websocket):
    async for message in websocket:
        data = json.loads(message)
        print(data)

        playername = data[0][1]
        d2 = data[1][1]


        if data[0][0] == 'playername_create':
            #create new game
            game_id = create_new_game(playername, d2)
            event = {
                "type": "new_game",
                "game_id": game_id,
            }
            print(event)
            await websocket.send(json.dumps(event))

        if data[0][0] == "playername_join":
            # join game
            join_game(playername, d2)

async def main():
    async with serve(handler, "localhost", 8765) as server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())