import pygame
from utils.colors import BLUE, GREEN
from utils.params import CHASER_SPEED
import math

class Chaser:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.color = (0, 100, 255)  # Blue
        self.radius = 12
        self.speed = CHASER_SPEED
        self.capture_radius = 25  # Pixels

    def update_simple(self, runner_position):
        """Simple proportional pursuit"""
        direction = (runner_position - self.pos).normalize()
        self.pos += direction * self.speed

    def has_captured(self, runner_position):
        return self.pos.distance_to(runner_position) < self.capture_radius

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)
    
    def get_position(self):
        self.pos.copy()

def create_triangular_formation(center, radius):
    """Creates 3 chasers in equilateral triangle formation"""
    chasers = []
    for angle in [30, 150, 270]:  # 120° separation
        chaser = Chaser(
            center.x + radius * math.cos(math.radians(angle)),
            center.y + radius * math.sin(math.radians(angle))
        )
        chaser.formation_offset = pygame.Vector2(
            radius * math.cos(math.radians(angle)),
            radius * math.sin(math.radians(angle))
        )
        chasers.append(chaser)
    
    return chasers

def draw_chaser_lines(screen, chasers):
    if len(chasers) >= 3:
        pygame.draw.polygon(screen, GREEN, 
                          [(c.pos.x, c.pos.y) for c in chasers[:3]], 2)
