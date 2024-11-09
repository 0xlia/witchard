from card import Card
import random
from typing import List, Tuple

class WitchardGame:
    def __init__(self, num_players: int):
        self.num_players = num_players
        self.player_names = []
        self.round_number = 0
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
            self.round_number += 1
            print(f"\n=== Round {self.round_number} ===")
            self._play_round()
            
        self._show_final_score()

    def _play_round(self):
        self._shuffle_cards()
        hands = self._deal_cards()
        trumpf_card = self._determine_trumpf()
        
        # Determine the starting player for this round
        start_player_index = (self.round_number - 1) % len(self.player_names)
        # Create the player order for the entire round
        current_player_order = self.player_names[start_player_index:] + self.player_names[:start_player_index]
        
        print(f"Starting player: {current_player_order[0]}")
        print(f"Trumpf: {trumpf_card}")
        
        predictions = self._get_predictions(hands, current_player_order)
        tricks_won = self._play_tricks(self.round_number, hands, trumpf_card, current_player_order)
        self._update_scores(predictions, tricks_won)

    def _deal_cards(self) -> dict:
        hands = {player: [] for player in self.player_names}
        for _ in range(self.round_number):
            for player in self.player_names:
                hands[player].append(self.deck.pop())
        return hands

    def _determine_trumpf(self) -> Card:
        if len(self.deck) > 0:
            trumpf_card = self.deck.pop()
            
            # If a Jester is revealed, there is no trump suit for this round
            if trumpf_card.suit == "JESTER":
                print("A Jester was revealed - No trump suit this round!")
                return None
                
            return trumpf_card
        return None

    def _get_predictions(self, hands: dict, player_order: list) -> dict:
        predictions = {}
        total_predictions = 0
        print("\n=== Predictions ===")
        
        for i, player in enumerate(player_order):
            print(f"\n{player}'s cards:")
            for card in hands[player]:
                print(card)
                
            # For the last player, check if prediction would equal round number
            is_last_player = i == len(player_order) - 1
            round_num = len(hands[player])
            
            while True:
                try:
                    pred = int(input(f"{player}, how many tricks will you win? "))
                    if pred < 0 or pred > round_num:
                        print("Prediction must be between 0 and the round number!")
                        continue
                        
                    if is_last_player and (total_predictions + pred) == round_num:
                        print(f"Sum of predictions cannot equal {round_num}! Please choose another number.")
                        continue
                        
                    predictions[player] = pred
                    total_predictions += pred
                    break
                except ValueError:
                    print("Invalid input!")
        
        # Show total predictions vs round number
        print(f"\nTotal predictions: {total_predictions}/{round_num}")
        
        return predictions
    
    def _play_tricks(self, round_num: int, hands: dict, trumpf_card: Card, player_order: list) -> dict:
        tricks_won = {player: 0 for player in self.player_names}
        
        for trick in range(round_num):
            print(f"\n=== Trick {trick + 1} ===")
            played_cards = []
            played_by = {}
           
            for player in player_order:
                print(f"\n{player}'s Cards:")
                for i, card in enumerate(hands[player]):
                    print(f"{i}: {card}")      

                # Determine the leading suit (first card played in the trick)
                lead_suit = played_cards[0].suit if played_cards else None         
                
                while True:
                    try:
                        choice = int(input(f"{player}, pick a card (0-{len(hands[player])-1}): "))
                        if 0 <= choice < len(hands[player]):
                            selected_card = hands[player][choice]
                            
                            # Check if the card choice is legal
                            if lead_suit and lead_suit not in ["WITCH", "JESTER"]:
                                # Check if player can follow suit
                                has_lead_suit = any(card.suit == lead_suit for card in hands[player])
                                
                                # If player can follow suit, they must do so
                                # Exception: WITCH and Jester can always be played
                                if has_lead_suit and selected_card.suit != lead_suit and \
                                   selected_card.suit not in ["WITCH", "JESTER"]:
                                    print(f"You must follow suit!")
                                    continue
                            
                            # If the choice is legal, play the card
                            played_card = hands[player].pop(choice)
                            played_cards.append(played_card)
                            played_by[played_card] = player
                            print(f"{player} plays {played_card}")
                            break
                        else:
                            print("Invalid card number!")
                    except ValueError:
                        print("Invalid input!")
            
            # Determine the winning card
            winning_card = played_cards[0]
            lead_suit = played_cards[0].suit
            
            for card in played_cards[1:]:
                # If a WITCH was played
                if card.suit == "WITCH":
                    winning_card = card
                # If the first card is not a WITCH
                elif winning_card.suit != "WITCH":
                    # If trump was played and winning card is not trump
                    if trumpf_card and card.suit == trumpf_card.suit and winning_card.suit != trumpf_card.suit:
                        winning_card = card
                    # If same suit was played and value is higher
                    elif card.suit == lead_suit and card.value > winning_card.value:
                        winning_card = card
            
            # Determine trick winner and update scores
            trick_winner = played_by[winning_card]
            tricks_won[trick_winner] += 1
            print(f"\n{trick_winner} wins the trick with {winning_card}!")
            
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
            print(f"Predicted: {predicted}, Won: {actual}")
            print(f"Points this round: {points}")
            print(f"Total score: {self.scores[player]}")
