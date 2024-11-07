from card import Card
import random
from typing import List, Tuple

class WitchardGame:
    def __init__(self, num_players: int):
        self.num_players = num_players
        self.player_names = []
        self.scores = {}
        self.deck = self._create_deck()
        
    def _create_deck(self) -> List[Card]:
        suits = ["RED", "YELLOW", "GREEN", "BLUE"]
        deck = []
        
        # Normal cards (1-13 in four suits)
        for suit in suits:
            for value in range(1, 14):
                deck.append(Card(suit, value))
                
        # JESTERs (4)
        for _ in range(4):
            deck.append(Card("JESTER", 0))
            
        # WITCHes (4)
        for _ in range(4):
            deck.append(Card("WITCH", 14))
            
        return deck
    
    def _shuffle_cards(self):
        random.shuffle(self.deck)
        
    def start_game(self):
        print("Welcome to Witchard!")
        
        # Enter player names
        for i in range(self.num_players):
            name = input(f"Name for Player {i+1}: ")
            self.player_names.append(name)
            self.scores[name] = 0
            
        # Main game loop
        rounds = 60 // self.num_players
        for round_num in range(1, rounds + 1):
            print(f"\n=== Round {round_num} ===")
            self._play_round(round_num)
            
        self._show_final_score()

    def _play_round(self, round_num: int):
        self._shuffle_cards()
        hands = self._deal_cards(round_num)
        trumpf_card = self._determine_trumpf(round_num)
        
        # Bestimme den Startspieler für diese Runde
        start_player_index = (round_num - 1) % len(self.player_names)
        # Erstelle die Spielerreihenfolge für die gesamte Runde
        current_player_order = self.player_names[start_player_index:] + self.player_names[:start_player_index]
        
        print(f"\n=== Runde {round_num} ===")
        print(f"Startspieler: {current_player_order[0]}")
        print(f"Trumpf: {trumpf_card}")
        
        predictions = self._get_predictions(hands, current_player_order)
        tricks_won = self._play_tricks(round_num, hands, trumpf_card, current_player_order)
        self._update_scores(predictions, tricks_won)

    def _deal_cards(self, round_num: int) -> dict:
        hands = {player: [] for player in self.player_names}
        for _ in range(round_num):
            for player in self.player_names:
                hands[player].append(self.deck.pop())
        return hands

    def _determine_trumpf(self, round_num: int) -> Card:
        if round_num < len(self.deck):
            return self.deck.pop()
        return None

    def _get_predictions(self, hands: dict, player_order: list) -> dict:
        predictions = {}
        print("\n=== Vorhersagen ===")
        
        for player in player_order:
            print(f"\n{player}'s Karten:")
            for card in hands[player]:
                print(card)
            while True:
                try:
                    pred = int(input(f"{player}, wie viele Stiche wirst du gewinnen? "))
                    predictions[player] = pred
                    break
                except ValueError:
                    print("Bitte gib eine gültige Zahl ein!")
        
        return predictions
    
    def _play_tricks(self, round_num: int, hands: dict, trumpf_card: Card, player_order: list) -> dict:
        tricks_won = {player: 0 for player in self.player_names}
        
        for trick in range(round_num):
            print(f"\n=== Stich {trick + 1} ===")
            played_cards = []
            played_by = {}
            
            # Jeder Spieler spielt eine Karte in der festgelegten Reihenfolge
            for player in player_order:
                print(f"\n{player}'s Karten:")
                for i, card in enumerate(hands[player]):
                    print(f"{i}: {card}")
                
                # Bestimme die zu bedienende Farbe (erste gespielte Karte des Stichs)
                lead_suit = played_cards[0].suit if played_cards else None
                
                while True:
                    try:
                        choice = int(input(f"{player}, wähle eine Karte (0-{len(hands[player])-1}): "))
                        if 0 <= choice < len(hands[player]):
                            selected_card = hands[player][choice]
                            
                            # Prüfe, ob die Kartenwahl legal ist
                            if lead_suit and lead_suit not in ["WITCH", "JESTER"]:
                                # Prüfe, ob der Spieler die Farbe bedienen kann
                                has_lead_suit = any(card.suit == lead_suit for card in hands[player])
                                
                                # Wenn der Spieler bedienen kann, muss er bedienen
                                # Ausnahme: WITCH und JESTER dürfen immer gespielt werden
                                if has_lead_suit and selected_card.suit != lead_suit and \
                                   selected_card.suit not in ["WITCH", "JESTER"]:
                                    print(f"Du musst {lead_suit} bedienen!")
                                    continue
                            
                            # Wenn die Wahl legal ist, spiele die Karte
                            played_card = hands[player].pop(choice)
                            played_cards.append(played_card)
                            played_by[played_card] = player
                            print(f"{player} spielt {played_card}")
                            break
                        else:
                            print("Ungültige Kartennummer!")
                    except ValueError:
                        print("Bitte gib eine gültige Zahl ein!")
            
            # Ermittle die Gewinnerkarte
            winning_card = played_cards[0]
            lead_suit = played_cards[0].suit
            
            for card in played_cards[1:]:
                # Wenn eine WITCH gespielt wurde
                if card.suit == "WITCH":
                    winning_card = card
                # Wenn die erste Karte keine WITCH ist
                elif winning_card.suit != "WITCH":
                    # Wenn Trumpf gespielt wurde und die Gewinnerkarte kein Trumpf ist
                    if card.suit == trumpf_card.suit and winning_card.suit != trumpf_card.suit:
                        winning_card = card
                    # Wenn die gleiche Farbe gespielt wurde und der Wert höher ist
                    elif card.suit == lead_suit and card.value > winning_card.value:
                        winning_card = card
            
            # Gewinner des Stichs ermitteln
            trick_winner = played_by[winning_card]
            tricks_won[trick_winner] += 1
            print(f"\n{trick_winner} gewinnt den Stich mit {winning_card}!")
            
        return tricks_won

    def _update_scores(self, predictions: dict, tricks_won: dict):
        for player in self.player_names:
            # Vorhersage und tatsächlich gewonnene Stiche
            predicted = predictions[player]
            actual = tricks_won[player]
            
            # Punkteberechnung
            if predicted == actual:
                # Bonus von 20 Punkten für korrekte Vorhersage
                # Plus 10 Punkte pro gewonnenem Stich
                points = 20 + (actual * 10)
            else:
                # Minus 10 Punkte pro falsch vorhergesagtem Stich
                difference = abs(predicted - actual)
                points = -10 * difference
                
            # Aktualisiere den Spielstand
            self.scores[player] += points
            
            # Zeige die Rundenauswertung
            print(f"\n{player}:")
            print(f"Vorhergesagt: {predicted}, Gewonnen: {actual}")
            print(f"Punkte diese Runde: {points}")
            print(f"Gesamtpunktzahl: {self.scores[player]}")
