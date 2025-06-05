class Spike:
    """Obstacle spike that can kill the chicken"""

    def __init__(self, x, y, width=50, height=25, pointing_right=True):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.pointing_right = pointing_right

    def get_collision_rect(self):
        """Get collision rectangle for spike"""
        return (self.x, self.y, self.width, self.height)

    def get_triangle_points(self):
        """Get triangle points for proper triangle rendering"""
        if self.pointing_right:
            # Left wall spikes pointing right
            return [
                self.x,
                self.y,  # Bottom left
                self.x,
                self.y + self.height,  # Top left
                self.x + self.width,
                self.y + self.height / 2,  # Right center
            ]
        else:
            # Right wall spikes pointing left
            return [
                self.x + self.width,
                self.y,  # Bottom right
                self.x + self.width,
                self.y + self.height,  # Top right
                self.x,
                self.y + self.height / 2,  # Left center
            ]

    def check_collision(self, chicken_rect):
        """Check if chicken collides with this spike"""
        cx, cy, cw, ch = chicken_rect
        sx, sy, sw, sh = self.get_collision_rect()

        return cx < sx + sw and cx + cw > sx and cy < sy + sh and cy + ch > sy