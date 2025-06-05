class ScoreManager:
    """Manages game scoring and high score"""

    def __init__(self):
        self.current_score = 0
        self.high_score = 0
        self.difficulty_level = 1

    def add_point(self):
        """Add a point when chicken hits wall"""
        self.current_score += 1
        if self.current_score > self.high_score:
            self.high_score = self.current_score

        # Increase difficulty every 5 points
        self.difficulty_level = 1 + (self.current_score // 5)

    def reset_current_score(self):
        """Reset current score on game over"""
        self.current_score = 0
        self.difficulty_level = 1