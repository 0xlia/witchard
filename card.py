class Card:
    def __init__(self, suit: str, value: int):
        self.suit = suit
        self.value = value
        
    def __str__(self):
        if self.value == 0:
            return f"[💀 {self.suit}]"
        elif self.value == 420:
            return f"[🧙 {self.suit}]"
        return f"[{self.value} {self.suit}]"