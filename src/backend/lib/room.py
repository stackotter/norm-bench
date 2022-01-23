from .board import Board
from dataclasses import dataclass

@dataclass
class Player:
    username: str
    progress: int

@dataclass
class Room:
    players: list[Player]
    board: Board
    seed: str
    has_started: bool