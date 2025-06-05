from kivy.vector import Vector

class Chicken:
    """Player character - a chicken that bounces between walls"""

    def __init__(self, x, y, size=30):
        self.pos = Vector(x, y)
        self.velocity = Vector(180, 0)  # Start moving right
        self.gravity_velocity = Vector(0, 0)  # Separate gravity velocity
        self.size = size
        self.radius = size // 2
        self.gravity = -981  # Gravity acceleration
        self.jump_force = 400  # Jump force
        self.alive = True

    def jump(self):
        """Make the chicken jump"""
        if self.alive:
            self.gravity_velocity.y = self.jump_force

    def update(self, dt, game_bounds) -> (bool, (int, int)):  # type: ignore
        """Update chicken position and handle wall bouncing"""
        if not self.alive:
            return (False, (0, 0))

        # Apply gravity
        self.gravity_velocity.y += self.gravity * dt

        # Update position with both horizontal and vertical movement
        self.pos.x += self.velocity.x * dt
        self.pos.y += self.gravity_velocity.y * dt

        # Check horizontal wall collisions and bounce
        wall_hit = False
        if self.pos.x <= self.radius:  # Left wall
            self.pos.x = self.radius
            self.velocity.x = abs(self.velocity.x)  # Bounce right
            wall_hit = True
        elif self.pos.x >= game_bounds[0] - self.radius:  # Right wall
            self.pos.x = game_bounds[0] - self.radius
            self.velocity.x = -abs(self.velocity.x)  # Bounce left
            wall_hit = True

        # Check vertical bounds (death)
        if self.pos.y <= self.radius or self.pos.y >= game_bounds[1] - self.radius:
            self.alive = False

        return (wall_hit, (self.pos.x, self.pos.y))

    def get_rect(self):
        """Get collision rectangle"""
        return (
            self.pos.x - self.radius,
            self.pos.y - self.radius,
            self.size,
            self.size,
        )