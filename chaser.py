import pygame
from utils.colors import BLUE, GREEN
from utils.params import CHASER_SPEED, WIDTH, HEIGHT, BORDER_MARGIN, SENSE_RADIUS
import math
import random

class Chaser:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.color = (0, 100, 255)  # Blue
        self.radius = 12
        self.speed = CHASER_SPEED
        self.capture_radius = 25  # Pixels

        self.velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * 0.5
        self.target_velocity = self.velocity.copy()
        self.max_speed = CHASER_SPEED
        self.steering_strength = 0.05 
        self.wander_smoothness = 0.7
        self.mode = "exploration"

    def _get_new_wander_direction(self):
        angle_change = random.gauss(0, 20) * (1 - self.wander_smoothness)
        return self.target_velocity.rotate(angle_change).normalize()

    def update_simple(self, runner_pos, runner_visible, chasers):
        if runner_visible:
            # Proportional pursuit
            self.mode = "pursuit"
            direction = (runner_pos - self.pos).normalize()
            self.pos += direction * self.speed
        else:
            # Gradually change wander direction
            self.mode = "exploration"
            if random.random() < 0.1:
                self.target_velocity = self._get_new_wander_direction() * self.max_speed

            repulsion = pygame.Vector2(0, 0)
            for other in chasers:
                if other is not self:
                    offset = self.pos - other.pos
                    dist = offset.length()
                    if 0 < dist < SENSE_RADIUS:
                        repulsion += offset / (dist**2)
            
            # Smooth transition toward new direction
            steer = self.target_velocity + repulsion * 100  # Tune strength as needed
            self.velocity += (steer - self.velocity) * self.steering_strength

            if self.pos.x < BORDER_MARGIN:
                self.target_velocity.x = abs(self.target_velocity.x)
            elif self.pos.x > WIDTH - BORDER_MARGIN:
                self.target_velocity.x = -abs(self.target_velocity.x)

            if self.pos.y < BORDER_MARGIN:
                self.target_velocity.y = abs(self.target_velocity.y)
            elif self.pos.y > HEIGHT - BORDER_MARGIN:
                self.target_velocity.y = -abs(self.target_velocity.y)

            self.pos += self.velocity

    def update_hybrid_1(self, runner_pos, runner_visible, all_chasers):
        neighbors = [c for c in all_chasers if c.id != self.id and self.pos.distance_to(c.pos) <= self.comm_radius]

        if runner_visible:
            self.mode = 'pursuit'
            self.last_runner_pos = runner_pos
            for neighbor in neighbors:
                neighbor.receive_runner_position(runner_pos)

        if self.mode == 'pursuit':
            if self.last_runner_pos:
                direction = (self.last_runner_pos - self.pos).normalize()
                self.velocity += (direction * self.max_speed - self.velocity) * self.steering_strength
                self.pos += self.velocity

                if self.pos.distance_to(self.last_runner_pos) < self.sense_radius:
                    self.mode = 'exploration'
                    self.last_runner_pos = None
        else:
            if random.random() < 0.1:
                self.target_velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * self.max_speed
            repulsion = pygame.Vector2(0, 0)
            for neighbor in neighbors:
                offset = self.pos - neighbor.pos
                dist = offset.length()
                if dist > 0 and dist < 100:
                    repulsion += offset / (dist ** 2)

            steer = self.target_velocity + repulsion * 100
            self.velocity += (steer - self.velocity) * self.steering_strength

            if self.pos.x < self.border_margin:
                self.target_velocity.x = abs(self.target_velocity.x)
            elif self.pos.x > WIDTH - self.border_margin:
                self.target_velocity.x = -abs(self.target_velocity.x)
            if self.pos.y < self.border_margin:
                self.target_velocity.y = abs(self.target_velocity.y)
            elif self.pos.y > HEIGHT - self.border_margin:
                self.target_velocity.y = -abs(self.target_velocity.y)

            self.pos += self.velocity

    def receive_runner_position(self, runner_pos):
        if self.mode != 'pursuit':
            self.mode = 'pursuit'
            self.last_runner_pos = runner_pos

    def has_captured(self, runner_position):
        return self.pos.distance_to(runner_position) < self.capture_radius

    def draw(self, surface):
        if self.mode == 'pursuit':
            color = (0, 0, 139)  # Dark blue
        else:
            color = (173, 216, 230)  # Light blue (exploring)

        pygame.draw.circle(surface, color, (int(self.pos.x), int(self.pos.y)), self.radius)
    
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
