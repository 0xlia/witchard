from urllib import request, error, parse
import json
import time
import os
import sys

class WitchardClient:
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.game_id = None
        self.player_name = None

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def create_game(self):
        num_players = 0
        while not (3 <= num_players <= 6):
            try:
                num_players = int(input("Anzahl der Spieler (3-6): "))
            except ValueError:
                print("Bitte geben Sie eine Zahl ein!")

        try:
            data = json.dumps({"num_players": num_players}).encode('utf-8')
            req = request.Request(
                f"{self.server_url}/game/create",
                data=data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with request.urlopen(req) as response:
                self.game_id = json.loads(response.read().decode('utf-8'))["game_id"]
                print(f"\nSpiel erstellt! Game ID: {self.game_id}")
                self.join_game(self.game_id)
        except error.URLError as e:
            print(f"Fehler beim Erstellen des Spiels: {e}")
            sys.exit(1)

    def join_game(self, game_id=None):
        if not game_id:
            self.game_id = input("Game ID eingeben: ").strip()
        
        try:
            data = json.dumps({
                "game_id": self.game_id,
                "player_name": self.player_name
            }).encode('utf-8')
            req = request.Request(
                f"{self.server_url}/game/join",
                data=data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with request.urlopen(req) as response:
                print(f"\nErfolgreich dem Spiel beigetreten!")
        except error.URLError as e:
            print(f"Fehler beim Beitreten: {e}")
            sys.exit(1)

    def get_game_state(self):
        try:
            params = parse.urlencode({'player_name': self.player_name})
            url = f"{self.server_url}/game/{self.game_id}/state?{params}"
            with request.urlopen(url) as response:
                return json.loads(response.read().decode('utf-8'))
        except error.URLError as e:
            print(f"Fehler beim Abrufen des Spielstatus: {e}")
            return None

    def start_game(self):
        try:
            data = json.dumps({"game_id": self.game_id}).encode('utf-8')
            req = request.Request(
                f"{self.server_url}/game/start",
                data=data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            with request.urlopen(req) as response:
                print("\nSpiel wird gestartet...")
        except error.URLError as e:
            print(f"Fehler beim Starten des Spiels: {e}")
            sys.exit(1)

    def wait_for_players(self):
        print("\nWarte auf andere Spieler...")
        while True:
            game_state = self.get_game_state()
            if not game_state:
                continue
            
            current_players = len(game_state.get('players', []))
            required_players = game_state.get('required_players', 3)
            
            self.clear_screen()
            print("Game ID:", self.game_id)
            print(f"Spieler im Spiel: {current_players}/{required_players}")
            print("\nAktuelle Spieler:")
            for player in game_state.get('players', []):
                print(f"👤 {player}")
            
            if current_players >= required_players:
                print("\nAlle Spieler sind da! Spiel startet...")
                self.start_game()
                time.sleep(2)
                return
            
            time.sleep(2)

    def display_game_state(self, state):
        if not state:
            return

        print(f"\nRunde: {state['round']}")
        print(f"Trumpf: {state['trumpf']}")
        print("\nPunkte:")
        for player, score in state['scores'].items():
            print(f"{player}: {score}")
        
        print("\nDeine Karten:")
        for card in state['hand']:
            print(card)
        
        if state['played_cards']:
            print("\nGespielte Karten:")
            for card in state['played_cards']:
                print(card)

    def start(self):
        self.clear_screen()
        print("✨ Willkommen beim Witchard Client! ✨\n")
        self.player_name = input("Dein Name: ").strip()
        
        while True:
            choice = input("\n(N)eues Spiel erstellen oder (B)eitreten? ").lower()
            if choice in ['n', 'b']:
                break
            print("Ungültige Eingabe!")

        if choice == 'n':
            self.create_game()
        else:
            self.join_game()
            
        self.game_loop()

    def game_loop(self):
        # Warte auf alle Spieler bevor das Spiel startet
        self.wait_for_players()
        self.start_game()
        
        while True:
            self.clear_screen()
            game_state = self.get_game_state()
            #self.display_game_state(game_state)
            print(game_state)

            if game_state["is_your_turn"]:
                print("\n🎲 Du bist am Zug!")
            else:
                print("\nWarte auf andere Spieler...")
            
            time.sleep(2)

if __name__ == "__main__":
    client = WitchardClient()
    try:
        client.start()
    except KeyboardInterrupt:
        print("\nSpiel beendet!") 