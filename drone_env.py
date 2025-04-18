import numpy as np
from collections import defaultdict
import pygame

class DroneEnv:
    def __init__(self, width, height, sense_radius):
        self.width = width
        self.height = height
        self.sense_radius = sense_radius
        self.cell_size = 30  # Reduced from 40 for smoother movement
        self.exploration_map = defaultdict(int)
        
    def reset(self):
        self.exploration_map.clear()
        
    def get_state(self, chaser, runner, other_chasers):
        """Convert environment observations to state vector"""
        state = []
        
        # 1. Relative runner position (normalized)
        if self._can_see(chaser.pos, runner.pos):
            rel_pos = (runner.pos - chaser.pos) / self.sense_radius
            state.extend([rel_pos.x, rel_pos.y, 1.0])  # 1.0 = visible
        else:
            state.extend([0, 0, 0])  # 0.0 = not visible
            
        # 2. Local exploration (4 directions)
        for angle in [0, 90, 180, 270]:
            sample_pos = chaser.pos + pygame.Vector2(
                np.cos(np.radians(angle)) * 100,
                np.sin(np.radians(angle)) * 100
            )
            visits = self.get_visit_count(sample_pos)
            state.append(min(visits, 10) / 10)  # Normalized 0-1

            
        # 3. Nearest neighbor info
        nearest = self._get_nearest_chaser(chaser, other_chasers)
        if nearest:
            rel_pos = (nearest.pos - chaser.pos) / self.sense_radius
            state.extend([rel_pos.x, rel_pos.y])
        else:
            state.extend([0, 0])
            
        return np.array(state, dtype=np.float32)
    
    def get_reward(self, chaser, runner, other_chasers):
        reward = 0
        
        # Enhanced exploration rewards
        visits = self.get_visit_count(chaser.pos)
        reward -= visits * 0.1
        
        # if hasattr(chaser, 'explore_target') and chaser.explore_target:
        #     target_visits = self.get_visit_count(chaser.explore_target)
        #     if target_visits == 0:
        #         reward += 0.5 * (1 - chaser.pos.distance_to(chaser.explore_target)/500)
        
        # Small constant penalty to encourage movement
        reward -= 0.01
        
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
        return min(visible, key=lambda c: current.pos.distance_to(c.pos)) if visible else None