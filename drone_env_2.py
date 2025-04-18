import numpy as np
from collections import defaultdict
import pygame

class DroneEnv:
    def __init__(self, width, height, sense_radius):
        self.width = width
        self.height = height
        self.sense_radius = sense_radius
        self.cell_size = 30  # Smaller cells for finer exploration
        self.exploration_map = defaultdict(int)

    def reset(self):
        self.exploration_map.clear()

    def get_state(self, chaser, runners, other_chasers):
        state = []
        # 1. Relative position & visibility for each runner
        for runner in runners:
            if self._can_see(chaser.pos, runner.pos):
                rel = (runner.pos - chaser.pos) / self.sense_radius
                state.extend([rel.x, rel.y, 1.0])
            else:
                state.extend([0.0, 0.0, 0.0])
        # 2. Local exploration (4 directions: 0°, 90°, 180°, 270°)
        for angle in [0, 90, 180, 270]:
            sample = chaser.pos + pygame.Vector2(
                np.cos(np.radians(angle)) * self.cell_size,
                np.sin(np.radians(angle)) * self.cell_size
            )
            visits = self.get_visit_count(sample)
            state.append(min(visits, 10) / 10)
        # 3. Nearest neighbor chaser info
        nearest = self._get_nearest_chaser(chaser, other_chasers)
        if nearest:
            rel = (nearest.pos - chaser.pos) / self.sense_radius
            state.extend([rel.x, rel.y])
        else:
            state.extend([0.0, 0.0])
        return np.array(state, dtype=np.float32)

    def get_reward(self, chaser, runners, captured_flags):
        reward = 0.0
        # Exploration penalty
        visits = self.get_visit_count(chaser.pos)
        reward -= visits * 0.1
        # Step penalty
        reward -= 0.01
        # Capture reward for chaser's current target
        if hasattr(chaser, 'current_target') and chaser.current_target is not None:
            if captured_flags[chaser.current_target]:
                reward += 2.0
        # Proximity bonus to current target
        if hasattr(chaser, 'current_target') and chaser.current_target is not None:
            runner = runners[chaser.current_target]
            dist = chaser.pos.distance_to(runner.pos)
            if dist < self.sense_radius:
                reward += 0.1 * (1 - dist / self.sense_radius)
        # Switching penalty
        if hasattr(chaser, 'last_target') and chaser.last_target is not None \
           and chaser.current_target != chaser.last_target:
            reward -= 0.2
        return reward

    def get_visit_count(self, pos):
        cell = (int(pos.x / self.cell_size), int(pos.y / self.cell_size))
        return self.exploration_map[cell]

    def mark_visited(self, pos):
        cell = (int(pos.x / self.cell_size), int(pos.y / self.cell_size))
        self.exploration_map[cell] += 1

    def _can_see(self, pos1, pos2):
        return pos1.distance_to(pos2) <= self.sense_radius

    def _get_nearest_chaser(self, current, others):
        visible = [c for c in others if self._can_see(current.pos, c.pos)]
        if not visible:
            return None
        return min(visible, key=lambda c: current.pos.distance_to(c.pos))