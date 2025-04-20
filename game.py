from card import Card
import random
from typing import List, Tuple, Dict, Any

SUITS = ["🔴", "🟡", "🟢", "🔵"]

class WitchardGame:
    def __init__(self, num_players: int):
        self.num_players = num_players
        self.player_names = []
        self.round_number = 0
        self.scores = {}
        self.deck = self._create_deck()
        self.hands = {}
        self.trumpf_card = None
        self.played_cards = []
        self.current_player = None
        self.current_trick = []
        self.trick_starter = None
        self.game_phase = "not_started"  # not_started, choose_trump, prediction, playing, round_end, game_over
        self.predictions = {}
        self.tricks_won = {}
        self.current_player_index = 0
        self.current_round_order = []
        self.waiting_for_trump_choice = False
        self.trump_chooser = None
           
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
        if player_name in self.player_names:
            return False
        self.player_names.append(player_name)
        self.scores[player_name] = 0
        self.hands[player_name] = []
        return True    
    
    def start_game(self):
        # Initialize scores
        self.scores = {player: 0 for player in self.player_names}
        # Start with round 1
        self._start_new_round()
    
    def _start_new_round(self):
        self.round_number += 1
        self._shuffle_cards()
        self._deal_cards()
        self.tricks_won = {player: 0 for player in self.player_names}
        self.predictions = {}
        self.played_cards = []
        self.current_trick = []
        
        # Determine starter for this round
        starter_index = (self.round_number - 1) % len(self.player_names)
        self.current_round_order = self.player_names[starter_index:] + self.player_names[:starter_index]
        self.current_player = self.current_round_order[0]
        self.current_player_index = 0
        self.trick_starter = self.current_player
        
        # Determine trumpf
        self._determine_trumpf()
        
        # If trumpf needs to be chosen, set the phase accordingly
        if self.waiting_for_trump_choice:
            self.game_phase = "choose_trump"
        else:
            # Otherwise, move to prediction phase
            self.game_phase = "prediction"

    def _deal_cards(self):
        self.hands = {player: [] for player in self.player_names}
        for _ in range(self.round_number):
            for player in self.player_names:
                if len(self.deck) > 0:
                    self.hands[player].append(self.deck.pop())

    def _determine_trumpf(self):
        self.waiting_for_trump_choice = False
        self.trump_chooser = None
        
        if len(self.deck) > 0:
            self.trumpf_card = self.deck.pop()
            
            # If a Jester is revealed, there is no trump suit for this round
            if self.trumpf_card.value == 0:
                return
                
            # If a WITCH is revealed, the last player can choose the trump suit
            if self.trumpf_card.value == 420:
                self.waiting_for_trump_choice = True
                last_player_index = (self.round_number - 1 + self.num_players - 1) % self.num_players
                self.trump_chooser = self.player_names[last_player_index]
                self.current_player = self.trump_chooser
        else:
            self.trumpf_card = None

    def choose_trump(self, player_name: str, suit_choice: int) -> Dict[str, Any]:
        if self.game_phase != "choose_trump":
            return {"success": False, "message": "Not in choose trump phase"}
        
        if player_name != self.trump_chooser:
            return {"success": False, "message": "You are not allowed to choose trump"}
        
        if not 0 <= suit_choice < len(SUITS):
            return {"success": False, "message": "Invalid suit choice"}
        
        chosen_suit = SUITS[suit_choice]
        self.trumpf_card = Card(chosen_suit, 420)  # WITCH with chosen suit
        self.waiting_for_trump_choice = False
        
        # Move to prediction phase
        self.game_phase = "prediction"
        self.current_player = self.current_round_order[0]
        self.current_player_index = 0
        
        return {"success": True}

    def make_prediction(self, player_name: str, prediction: int) -> Dict[str, Any]:
        if self.game_phase != "prediction":
            return {"success": False, "message": "Not in prediction phase"}
        
        if player_name != self.current_player:
            return {"success": False, "message": "Not your turn"}
        
        if prediction < 0 or prediction > self.round_number:
            return {"success": False, "message": "Prediction must be between 0 and the round number"}
        
        # Check if this is the last player and if sum of predictions would equal round number
        is_last_player = self.current_player_index == len(self.player_names) - 1
        current_sum = sum(self.predictions.values())
        
        if is_last_player and (current_sum + prediction) == self.round_number:
            return {"success": False, "message": f"Sum of predictions cannot equal {self.round_number}"}
        
        # Store the prediction
        self.predictions[player_name] = prediction
        
        # Move to the next player
        self.current_player_index = (self.current_player_index + 1) % len(self.player_names)
        
        # If all players have made predictions, start playing
        if len(self.predictions) == len(self.player_names):
            self.game_phase = "playing"
            self.current_player_index = 0
            self.current_player = self.current_round_order[0]
            self.trick_starter = self.current_player
        else:
            self.current_player = self.current_round_order[self.current_player_index]
        
        return {"success": True}

    def play_card(self, player_name: str, card_index: int) -> Dict[str, Any]:
        if self.game_phase != "playing":
            return {"success": False, "message": "Not in playing phase"}
        
        if player_name != self.current_player:
            return {"success": False, "message": "Not your turn"}
        
        player_hand = self.hands[player_name]
        
        if not 0 <= card_index < len(player_hand):
            return {"success": False, "message": "Invalid card index"}
        
        selected_card = player_hand[card_index]
        
        # Check if card play is legal
        if self.current_trick:
            lead_suit = self.current_trick[0].suit
            
            # If the first card is a JESTER, find the first non-JESTER card's suit
            if self.current_trick[0].value == 0 and len(self.current_trick) > 1:
                for card in self.current_trick[1:]:
                    if card.value != 0:
                        lead_suit = card.suit
                        break
            
            # Check if player needs to follow suit (unless playing WITCH or JESTER)
            has_lead_suit = any(card.suit == lead_suit for card in player_hand)
            if has_lead_suit and selected_card.suit != lead_suit and selected_card.value not in [0, 420]:
                return {"success": False, "message": "You must follow suit"}
        
        # Play the card
        played_card = player_hand.pop(card_index)
        self.current_trick.append(played_card)
        self.played_cards.append(played_card)
        
        # Move to the next player
        self.current_player_index = (self.current_player_index + 1) % len(self.player_names)
        self.current_player = self.current_round_order[self.current_player_index]
        
        # If all players have played a card, evaluate the trick
        if len(self.current_trick) == len(self.player_names):
            self._evaluate_trick()
        
        return {"success": True}

    def _evaluate_trick(self):
        # Determine the winner of the trick
        winning_card = self._get_winning_card(self.current_trick)
        
        # Find the player who played the winning card
        winner_index = 0
        for i, card in enumerate(self.current_trick):
            if card == winning_card:
                winner_index = i
                break
        
        # Determine the position relative to trick_starter
        winner_player_index = (self.current_round_order.index(self.trick_starter) + winner_index) % len(self.player_names)
        trick_winner = self.current_round_order[winner_player_index]
        
        # Update tricks won
        self.tricks_won[trick_winner] += 1
        
        # Reset for next trick
        self.current_trick = []
        
        # Next trick is started by the winner
        self.trick_starter = trick_winner
        self.current_player = trick_winner
        self.current_player_index = self.current_round_order.index(trick_winner)
        
        # Check if round is complete
        if sum(self.tricks_won.values()) == self.round_number:
            self._end_round()
    
    def _get_winning_card(self, played_cards: List[Card]) -> Card:
        if not played_cards:
            return None
            
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
    
    def _end_round(self):
        # Calculate scores for the round
        self._update_scores()
        
        # Check if game is over
        if self.round_number >= 60 // self.num_players:
            self.game_phase = "game_over"
        else:
            # Start a new round
            self.game_phase = "round_end"
            self._start_new_round()
    
    def _update_scores(self):
        for player in self.player_names:
            # Predicted and actual tricks won
            predicted = self.predictions[player]
            actual = self.tricks_won[player]
            
            # Calculate points
            if predicted == actual:
                # Bonus of 20 points for correct prediction
                # Plus 10 points per trick won
                points = 20 + (actual * 10)
            else:
                # Minus 10 points per difference between prediction and actual
                difference = abs(predicted - actual)
                points = -10 * difference
                
            # Update score
            self.scores[player] += points

    def _card_to_dict(self, card):
        """Helper method to convert Card to dict or return None if card is None"""
        if card is None:
            return None
        return {
            "suit": card.suit,
            "value": card.value,
            "display": str(card)
        }
    
    def _cards_to_dict(self, cards):
        """Helper method to convert a list of Cards to a list of dicts"""
        return [self._card_to_dict(card) for card in cards]

    def get_player_state(self, player_name: str) -> dict:
        is_current_player = self.current_player == player_name
        
        # Base state information
        state = {
            "is_your_turn": is_current_player,
            "players": self.player_names,
            "num_players": self.num_players,
            "game_started": self.game_phase != "not_started",
            "scores": self.scores,
            "round": self.round_number,
            "trumpf": self._card_to_dict(self.trumpf_card),
            "played_cards": self._cards_to_dict(self.played_cards),
            "current_trick": self._cards_to_dict(self.current_trick),
            "hand": self._cards_to_dict(self.hands.get(player_name, [])),
            "phase": self.game_phase,
            "predictions": self.predictions,
            "tricks_won": self.tricks_won
        }
        
        # Add available actions for current player
        if is_current_player:
            actions = []
            
            if self.game_phase == "choose_trump" and player_name == self.trump_chooser:
                actions.append({
                    "action": "choose_trump",
                    "options": [{"id": i, "suit": suit} for i, suit in enumerate(SUITS)]
                })
                
            elif self.game_phase == "prediction":
                valid_predictions = list(range(self.round_number + 1))
                # If last player, check if any prediction would make sum equal to round_number
                if self.current_player_index == len(self.player_names) - 1:
                    current_sum = sum(self.predictions.values())
                    invalid_prediction = self.round_number - current_sum
                    if 0 <= invalid_prediction <= self.round_number:
                        valid_predictions.remove(invalid_prediction)
                        
                actions.append({
                    "action": "predict",
                    "options": valid_predictions
                })
                
            elif self.game_phase == "playing":
                player_hand = self.hands.get(player_name, [])
                valid_cards = []
                
                # If not first card in trick, check suit following
                if self.current_trick:
                    lead_suit = self.current_trick[0].suit
                    
                    # If first card is JESTER, find first non-JESTER
                    if self.current_trick[0].value == 0 and len(self.current_trick) > 1:
                        for card in self.current_trick[1:]:
                            if card.value != 0:
                                lead_suit = card.suit
                                break
                    
                    has_lead_suit = any(card.suit == lead_suit for card in player_hand)
                    
                    # If player has lead suit, they must follow
                    if has_lead_suit:
                        for i, card in enumerate(player_hand):
                            if card.suit == lead_suit or card.value in [0, 420]:  # Can always play WITCH or JESTER
                                valid_cards.append({"index": i, "card": self._card_to_dict(card)})
                    else:
                        # Can play any card
                        valid_cards = [{"index": i, "card": self._card_to_dict(card)} for i, card in enumerate(player_hand)]
                else:
                    # First to play, can play any card
                    valid_cards = [{"index": i, "card": self._card_to_dict(card)} for i, card in enumerate(player_hand)]
                
                actions.append({
                    "action": "play_card",
                    "options": valid_cards
                })
            
            state["available_actions"] = actions
        
        return state