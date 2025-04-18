import pygame
import math
import random
import numpy as np
from collections import defaultdict
from utils.params import WIDTH, HEIGHT

class ChaserIntelligent:
    def __init__(self, x, y, rl_agent):
        self.pos = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize() * 0.5
        self.target_velocity = self.velocity.copy()
        self.radius = 15
        self.speed = 2.5
        self.max_speed = 3.5
        self.steering_strength = 0.08
        self.mode = "exploration"
        self.rl_agent = rl_agent
        self.explore_target = None
        self.last_state = None
        self.last_action = None
        self.switch_cooldown = 0
        self.exploration_cell_size = 30  # Smaller cells for smoother movement
        self.mode_switch = False

    def update(self, env, runner, other_chasers):
        state = env.get_state(self, runner, other_chasers)
        
        # Check if any chaser can see the runner
        swarm_sees_runner = (state[2] > 0.5) or any(
            c.last_state is not None and c.last_state[2] > 0.5 
            for c in other_chasers
        )

        # Mode switching with cooldown
        if self.switch_cooldown <= 0:
            if swarm_sees_runner:
                self.mode = "pursuit"
                self.switch_cooldown = 30
            else:
                self.mode = "exploration"

        # Execute behavior
        if self.mode == "pursuit":
            self._pursuit_behavior(runner)
            self.last_action = -1
        else:
            self._explore(env)
            self.last_action = None
        
        self.switch_cooldown -= 1
        self.mode_switch = np.array_equal(self.last_state, state)

        self.last_state = state
        self._enforce_bounds()

    def _pursuit_behavior(self, runner):
        """Smooth pursuit with steering"""
        target_direction = (runner.pos - self.pos).normalize()
        self.target_velocity = target_direction * self.max_speed * 1.2
        self._apply_steering()

    def _explore(self, env):
        """Improved randomized exploration"""
        if (self.explore_target is None or 
            env.get_visit_count(self.explore_target) > 1 or
            self.pos.distance_to(self.explore_target) < 15):
            
            # Get all unexplored cells in radius, then pick one randomly
            unexplored = []
            search_radius = 300
            
            # Check cells in spiral pattern for efficiency
            for distance in range(50, int(search_radius), self.exploration_cell_size):
                for angle in range(0, 360, 30):
                    rad = math.radians(angle)
                    cell_x = self.pos.x + math.cos(rad) * distance
                    cell_y = self.pos.y + math.sin(rad) * distance
                    cell_pos = pygame.Vector2(cell_x, cell_y)
                    
                    if self._is_within_bounds(cell_pos):
                        visits = env.get_visit_count(cell_pos)
                        if visits <= 1:  # Prioritize unexplored or visited once
                            unexplored.append(cell_pos)
            
            # Random selection from available unexplored cells
            if unexplored:
                self.explore_target = random.choice(unexplored)
            else:
                # Fallback to random position with central bias
                self.explore_target = pygame.Vector2(
                    random.gauss(WIDTH/2, WIDTH/4),
                    random.gauss(HEIGHT/2, HEIGHT/4)
                )
                self.explore_target.x = max(20, min(self.explore_target.x, WIDTH-20))
                self.explore_target.y = max(20, min(self.explore_target.y, HEIGHT-20))
        
        # Smooth movement toward target
        if self.explore_target:
            desired_velocity = (self.explore_target - self.pos).normalize() * self.max_speed * 0.8
            self.target_velocity = desired_velocity
            self._apply_steering()

    def _apply_steering(self):
        """Smooth steering with velocity"""
        self.velocity += (self.target_velocity - self.velocity) * self.steering_strength
        self.pos += self.velocity

    def _enforce_bounds(self):
        """Strict border containment with bounce"""
        border_margin = 15
        bounce_factor = 0.8
        
        if self.pos.x < border_margin:
            self.pos.x = border_margin
            self.velocity.x *= -bounce_factor
        elif self.pos.x > WIDTH - border_margin:
            self.pos.x = WIDTH - border_margin
            self.velocity.x *= -bounce_factor
            
        if self.pos.y < border_margin:
            self.pos.y = border_margin
            self.velocity.y *= -bounce_factor
        elif self.pos.y > HEIGHT - border_margin:
            self.pos.y = HEIGHT - border_margin
            self.velocity.y *= -bounce_factor

    def _is_within_bounds(self, pos):
        """Check if position is within valid bounds"""
        border_margin = 20
        return (border_margin <= pos.x <= WIDTH - border_margin and 
                border_margin <= pos.y <= HEIGHT - border_margin)
    

def create_triangular_formation(center, radius, rl_agent):
    """Creates 3 chasers in equilateral triangle formation"""
    chasers = []
    for angle in [30, 150, 270]:  # 120° separation
        chaser = ChaserIntelligent(
            center.x + radius * math.cos(math.radians(angle)),
            center.y + radius * math.sin(math.radians(angle)),
            rl_agent
        )
        chaser.formation_offset = pygame.Vector2(
            radius * math.cos(math.radians(angle)),
            radius * math.sin(math.radians(angle))
        )
        chasers.append(chaser)
    
    return chasers