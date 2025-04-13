import pygame
import math
import random
import numpy as np
from utils.params import RUNNER_MAX_SPEED, RUNNER_STEERING_STRENGTH, RUNNER_SMOOTHNESS

class Runner:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(random.uniform(-1, 1), 
                                     random.uniform(-1, 1)).normalize() * 0.5
        self.color = (255, 0, 0)
        self.radius = 15
        self.max_speed = RUNNER_MAX_SPEED
        self.steering_strength = RUNNER_STEERING_STRENGTH  # Lower = smoother turns
        self.border_margin = 80
        self.target_velocity = self.velocity.copy()
        self.smoothness = RUNNER_SMOOTHNESS  # 0-1, higher = smoother direction changes

    def _get_new_direction(self):
        """Generates smoothly changing target direction"""
        angle_change = random.gauss(0, 15) * (1 - self.smoothness)
        return self.target_velocity.rotate(angle_change).normalize()

    def update_random(self):
        # Gradually update target velocity
        if random.random() < 0.5:
            self.target_velocity = self._get_new_direction() * self.max_speed
        
        # Smooth steering toward target velocity
        self.velocity += (self.target_velocity - self.velocity) * self.steering_strength
        
        # Border handling with smooth rebound
        if self.pos.x < self.border_margin:
            self.target_velocity.x = abs(self.target_velocity.x)
        elif self.pos.x > pygame.display.get_surface().get_width() - self.border_margin:
            self.target_velocity.x = -abs(self.target_velocity.x)
            
        if self.pos.y < self.border_margin:
            self.target_velocity.y = abs(self.target_velocity.y)
        elif self.pos.y > pygame.display.get_surface().get_height() - self.border_margin:
            self.target_velocity.y = -abs(self.target_velocity.y)
        
        # Update position
        self.pos += self.velocity

    def get_position(self):
        return self.pos.copy()

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)
        
        # Draw velocity vector (optional visual aid)
        end_pos = self.pos + self.velocity * 20
        pygame.draw.line(surface, (200, 0, 0), self.pos, end_pos, 2)