class Card:
    def __init__(self, suit: str, value: int):
        self.suit = suit
        self.value = value
        
    def __str__(self):
        if self.suit == "JESTER":
            return "JESTER"
        elif self.suit == "WITCH":
            return "WITCH"
        return f"{self.value} {self.suit}"