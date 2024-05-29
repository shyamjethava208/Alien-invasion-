from pathlib import Path
class GameStats:
    """Track statistics for Alien Invasion."""
    def __init__(self,ai_game):
        self.settings = ai_game.settings
        path = Path("high_score.txt")
        self.high_score=int(path.read_text())
        self.reset_stats()

    def reset_stats(self):
        """Initialize statistics that can change during the game."""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1