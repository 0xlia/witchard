class Card:
    def __init__(self, suit: str, value: int):
        self.suit = suit  # 🔴, 🟡, 🟢, 🔵
        self.value = value  # 0 (JESTER), 1-13 (normal), 420 (WITCH)
        
    def __str__(self) -> str:
        if self.value == 0:
            return f"💀 {self.suit} JESTER"
        elif self.value == 420:
            return f"🧙 {self.suit} WITCH"
        else:
            # For normal cards, show the value and suit
            return f"{self.suit} {self.value}"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.value == other.value
    
    def to_dict(self) -> dict:
        """Convert the card to a dictionary representation for API responses"""
        return {
            "suit": self.suit,
            "value": self.value,
            "display": str(self)
        }