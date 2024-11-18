from card import Card
import random
from typing import List, Tuple

SUITS = ["🔴", "🟡", "🟢", "🔵"]

class WitchardGame:
    def __init__(self, num_players: int):
        self.num_players = num_players
        self.player_names = []
        self.round_number = 0
        self.scores = {}
        self.deck = self._create_deck()
        self.hands = {player: [] for player in self.player_names}
        self.trumpf_card = None
        self.played_cards = []
        self.current_player = None
           
    def _create_deck(self) -> List[Card]:
        deck = []
        
        # Normal cards (1-13 in four suits)
        for suit in SUITS:
            # Add one JESTER (value 0) per suit
            deck.append(Card(suit, 0))
            
            # Normal cards (1-13)
            for value in range(1, 14):
                deck.append(Card(suit, value))
                
            # Add one WITCH (value 420) per suit
            deck.append(Card(suit, 420))
        
        return deck
    
    def _shuffle_cards(self):
        random.shuffle(self.deck)
    
    def add_player(self, player_name: str) -> bool:
        if len(self.player_names) >= self.num_players:
            return False
        self.player_names.append(player_name)
        self.scores[player_name] = 0
        return True    
    
    def start_game(self):
        print("✨ Welcome to Witchard! ✨\n")
        
        # Enter player names
        self.scores = {player: 0 for player in self.player_names}
            
        # Main game loop
        rounds = 60 // self.num_players
        for round_num in range(1, rounds + 1):
            self.round_number += 1
            print(f"\n▪️▪️▪️▪️▪️▪️ ROUND {self.round_number} ▪️▪️▪️▪️▪️▪️")
            self._play_round()
            
        self._show_final_score()

    def _play_round(self):
        self._shuffle_cards()
        self._deal_cards()
        self._determine_trumpf()
        
        # Determine the starting player for this round
        start_player_index = (self.round_number - 1) % len(self.player_names)
        # Create the player order for the entire round
        current_player_order = self.player_names[start_player_index:] + self.player_names[:start_player_index]
        self.current_player = current_player_order[0]

        print(f"\nStarting player: {current_player_order[0]}")
        print(f"Trumpf: {self.trumpf_card}")
        
        predictions = self._get_predictions(current_player_order)
        tricks_won = self._play_tricks(self.trumpf_card, current_player_order)
        self._update_scores(predictions, tricks_won)

    def _deal_cards(self):
        hands = {player: [] for player in self.player_names}
        for _ in range(self.round_number):
            for player in self.player_names:
                hands[player].append(self.deck.pop())
        self.hands = hands

    def _determine_trumpf(self):
        if len(self.deck) > 0:
            trumpf_card = self.deck.pop()
            
            # If a Jester is revealed, there is no trump suit for this round
            if trumpf_card.value == 0:
                print("A 💀 Jester was revealed - No trump suit this round!")
                return None
                
            # If a WITCH is revealed, the last player can choose the trump suit
            if trumpf_card.value == 420:
                last_player = self.player_names[(self.round_number - 1 + self.num_players - 1) % self.num_players]
                print(f"A 🧙 Witch was revealed! {last_player} can choose the trump suit.")

                if self.round_number == 1:
                    # print all cards of other players than last player
                    print("\nCards of other players:")
                    for player in self.player_names:
                        if player != last_player:
                            print(f"\n{player}'s cards:")
                            for card in self.hands[player]:
                                print(card)
                
                while True:
                    try:
                        choice = int(input(f"{last_player}, Choose a suit: (0: RED, 1: YELLOW, 2: GREEN, 3: BLUE): "))
                        if 0 <= choice < len(SUITS):
                            chosen_suit = SUITS[choice]
                            return Card(chosen_suit, 420)  # Return WITCH with chosen suit
                        else:
                            print("Invalid choice!")
                    except ValueError:
                        print("Invalid input!")
                
            self.trumpf_card = trumpf_card
        self.trumpf_card = None

    def _get_predictions(self, player_order: list) -> dict:
        predictions = {}
        total_predictions = 0
        print("\n▪️▪️▪️ Predictions ▪️▪️▪️")
        
        for i, player in enumerate(player_order):
            # Round 1: Show other players' cards
            if self.round_number == 1:
                print(f"\nCards of other players:")
                for other_player in player_order:
                    if other_player != player:
                        print(f"\n{other_player}'s cards:")
                        for card in self.hands[other_player]:
                            print(card)
            else:
                # Normal game: Show own cards
                print(f"\n{player}'s cards:")
                for card in self.hands[player]:
                    print(card)
                
            # For the last player, check if prediction would equal round number
            is_last_player = i == len(player_order) - 1
            
            while True:
                try:
                    pred = int(input(f"\n{player}, how many tricks will you win? "))
                    if pred < 0 or pred > self.round_number:
                        print("Prediction must be between 0 and the round number!")
                        continue
                        
                    if is_last_player and (total_predictions + pred) == self.round_number:
                        print(f"Sum of predictions cannot equal {self.round_number}! Please choose another number.")
                        continue
                        
                    predictions[player] = pred
                    total_predictions += pred
                    break
                except ValueError:
                    print("Invalid input!")
            print("\n▪️▪️▪️▪️▪️▪️")
        
        # Show total predictions vs round number
        print(f"\nTotal predictions: {total_predictions}/{self.round_number}")
        
        return predictions
    
    def _play_tricks(self, player_order: list) -> dict:
        tricks_won = {player: 0 for player in self.player_names}
        
        for trick in range(self.round_number):
            print(f"\n▪️▪️▪️  Trick {trick + 1} ▪️▪️▪️ ")
            played_by = {}
           
            for player in player_order:
                # If only one card is left, play it automatically
                if len(self.hands[player]) == 1:
                    played_card = self.hands[player].pop(0)
                    self.played_cards.append(played_card)
                    played_by[played_card] = player
                    print(f"\n{player} plays {played_card}")
                    print("\n▪️▪️▪️▪️▪️▪️")
                    continue

                # Show player's cards
                print(f"\n{player}'s cards:")
                for i, card in enumerate(self.hands[player]):
                    print(f"{i}: {card}")      

                # Determine the leading suit (first card played in the trick)
                lead_suit = self.played_cards[0].suit if self.played_cards else None
                
                # If the first card is a JESTER and there are more cards,
                # set the leading suit to the first non-JESTER card
                if self.played_cards and self.played_cards[0].value == 0 and len(self.played_cards) > 1:
                    for card in self.played_cards[1:]:
                        if card.value != 0:
                            lead_suit = card.suit
                            break
                
                while True:
                    try:
                        choice = int(input(f"\n{player}, pick a card (0-{len(self.hands[player])-1}): "))
                        if 0 <= choice < len(self.hands[player]):
                            selected_card = self.hands[player][choice]
                            
                            # Check if the card choice is legal
                            # If the first card is a WITCH, suit doesn't need to be followed
                            if lead_suit and not any(c.value == 420 for c in played_cards):
                                # Check if player can follow suit
                                has_lead_suit = any(card.suit == lead_suit for card in self.hands[player])
                                
                                # If player can follow suit, they must do so
                                # Exception: WITCH and JESTER can always be played
                                if has_lead_suit and selected_card.suit != lead_suit and \
                                   selected_card.value not in [0, 420]:
                                    print(f"You must follow suit!")
                                    continue
                            
                            # If the choice is legal, play the card
                            played_card = self.hands[player].pop(choice)
                            played_cards.append(played_card)
                            played_by[played_card] = player
                            print(f"\n{player} plays {played_card}")
                            break
                        else:
                            print("Invalid card number!")
                    except ValueError:
                        print("Invalid input!")
                print("\n▪️▪️▪️▪️▪️▪️")
            
            winning_card = self._get_winning_card(played_cards)
            
            # Determine trick winner and update scores
            trick_winner = played_by[winning_card]
            tricks_won[trick_winner] += 1
            print(f"\n{trick_winner} wins the trick with {winning_card}!")
            
        return tricks_won
    
    def _get_winning_card(self, played_cards: list) -> Card:
        # Determine the winning card
        winning_card = played_cards[0]
        lead_suit = played_cards[0].suit

        # If the first card is a JESTER, the next non-JESTER card is the winning card
        if winning_card.value == 0:
            for card in played_cards[1:]:
                if card.value != 0:
                    winning_card = card
                    lead_suit = card.suit
                    break
        
        for card in played_cards:
            # If a WITCH was played
            if card.value == 420:
                winning_card = card
                break
            # If no WITCH has been played yet
            elif winning_card.value != 420:
                # If trump was played and winning card is not trump
                if self.trumpf_card and card.suit == self.trumpf_card.suit and winning_card.suit != self.trumpf_card.suit:
                    winning_card = card
                # If same suit was played and value is higher
                elif card.suit == lead_suit and card.value > winning_card.value:
                    winning_card = card
        
        return winning_card
    
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

    def get_player_state(self, player_name: str) -> dict:
        return {
            "is_your_turn": self.current_player == player_name,
            "players": self.player_names,
            "num_players": self.num_players,
            "game_started": len(self.player_names) >= self.num_players,
            "scores": self.scores,
            "round": self.round_number,
            "trumpf": self.trumpf_card,
            "played_cards": self.played_cards,
            "hand": self.hands.get(player_name, [])        
        }