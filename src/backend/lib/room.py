from dataclasses import dataclass, field
from typing import Optional

from .board import Board

@dataclass
class Player:
    username: str
    progress: int = 0

@dataclass
class Room:
    players: list[Player]
    board: Board
    seed: str
    has_started: bool = False
    next_room: Optional[int] = None
    letter_count: int = 7
    minimum_word_length: int = 3
    ghost_players: list[str] = field(default_factory=list) # Players that have left the room but are still stored for the leaderboard

    def to_json(self, room_id, username):
        return {
            "roomId": room_id,
            "username": username,
            "width": self.board.width,
            "height": self.board.height,
            "hasStarted": self.has_started,
            "words": [{
                "x": word[0],
                "y": word[1],
                "direction": word[2].value,
                "word": word[3]
            } for word in self.board.words],
            "players": [{
                "username": player.username,
                "progress": player.progress
            } for player in self.players],
            "letters": self.board.letters,
            "seed": self.seed,
            "letterCount": self.letter_count,
            "minimumWordLength": self.minimum_word_length
        }