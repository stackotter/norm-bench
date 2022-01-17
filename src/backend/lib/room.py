from .board import Board
from dataclasses import dataclass

@dataclass
class Room:
    players: list[str]
    board: Board