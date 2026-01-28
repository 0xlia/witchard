from dataclasses import dataclass


# TODO: add enum suit

@dataclass
class Card:
    """Class that represents a Wizard playing card"""
    suit: str
    value: int

    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.value == other.value
    