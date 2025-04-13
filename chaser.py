import pygame
from utils.colors import BLUE, GREEN
import math

class Chaser:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.color = BLUE
        self.radius = 12
        self.speed = 0  # Will be set in formation update
        self.direction = pygame.Vector2(0, 0)  # Will be calculated
        self.formation_offset = pygame.Vector2(0, 0)  # Position relative to formation center

    def update(self, formation_center, formation_angle):
        # Maintain formation position (no chasing logic yet)
        target_pos = formation_center + self.formation_offset.rotate(formation_angle)
        self.direction = (target_pos - self.pos).normalize()
        self.pos += self.direction * self.speed

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)

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
        chaser.speed = 4.0
        chasers.append(chaser)
    
    return chasers

def draw_chaser_lines(screen, chasers):
    if len(chasers) >= 3:
        pygame.draw.polygon(screen, GREEN, 
                          [(c.pos.x, c.pos.y) for c in chasers[:3]], 2)
