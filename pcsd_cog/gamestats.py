from dataclasses import dataclass

@dataclass
class GameStats:
    gameMode: str
    gameTime: float
    mapName: str
    mapNumber: int
    mapTerrain: str
