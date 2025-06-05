from .obstacles import Spike
import random

class SpikeGenerator:
    """Manages spike generation and placement on vertical walls"""

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.spikes: list[list[Spike]] = [[], []]
        self.spike_width = 40
        self.wall_thickness = 40  # How far spikes extend from wall
        self.generate_initial_spikes()

    def generate_initial_spikes(self):
        """Generate initial set of spikes with safe passages"""
        self.spikes.clear()

        # Generate left wall spikes (pointing right)
        self.spikes.append(self._generate_spike_column(x=0, pointing_right=True))

        # Generate right wall spikes (pointing left)
        self.spikes.append(
            self._generate_spike_column(
                x=self.screen_width - self.wall_thickness, pointing_right=False
            )
        )

    def _generate_spike_column(
        self, x, pointing_right, gap_probability=0.8
    ) -> list[Spike]:
        """Generate a column of spikes with random gaps"""
        spike_height = 35
        num_spikes = int(self.screen_height // spike_height)
        spikes = []
        for i in range(num_spikes):
            # Create gaps for safe passage
            if random.random() > gap_probability:
                y = i * spike_height
                spike = Spike(
                    x,
                    y,
                    width=self.wall_thickness,
                    height=spike_height - 2,
                    pointing_right=pointing_right,
                )
                spikes.append(spike)
        return spikes

    def regenerate_spikes(self, coords, difficulty_level=1):
        """Regenerate spikes with increased difficulty"""
        # Increase spike density based on difficulty
        gap_probability = max(0.5, 0.8 - (difficulty_level * 0.05))

        x, _ = coords
        # Generate new spike patterns
        if x > self.screen_width / 2:
            self.spikes[0] = self._generate_spike_column(
                x=0, pointing_right=True, gap_probability=gap_probability
            )
        else:
            self.spikes[1] = self._generate_spike_column(
                x=self.screen_width - self.wall_thickness,
                pointing_right=False,
                gap_probability=gap_probability,
            )

    def check_collisions(self, chicken):
        """Check if chicken collides with any spikes"""
        chicken_rect = chicken.get_rect()
        for spikes in self.spikes:
            for spike in spikes:
                if spike.check_collision(chicken_rect):
                    return True
        return False