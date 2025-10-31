# snake_game.py
import pygame
import random
import json
import os
from typing import Optional
from enum import Enum


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class SnakeGame:
    """
    Gesture-controlled Snake Game with:
      • Wrap-around edge movement
      • Smooth transition trails
      • Keyboard toggles for wrap (W) and pause (P)
    """

    def __init__(self, width: int = 400, height: int = 600, grid_size: int = 20):
        self.width = width
        self.height = height
        self.grid_size = grid_size

        self.grid_width = max(4, self.width // self.grid_size)
        self.grid_height = max(4, self.height // self.grid_size)

        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.NOKIA_GREEN = (155, 188, 15)
        self.DARK_GREEN = (139, 172, 15)
        self.LIGHT_GREEN = (204, 255, 51)
        self.RED = (255, 0, 0)
        self.ORANGE = (255, 165, 0)
        self.YELLOW = (255, 255, 0)
        self.CYAN = (0, 255, 255)

        # Pygame fonts
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Load high score
        self.high_score = self.load_high_score()

        # Effects & power-ups
        self.particles = []
        self.transition_particles = []
        self.power_ups = []
        self.power_up_spawn_chance = 0.1
        self.last_power_up_score = 0

        # Game state
        self.paused = False
        self.screen = None

        # Wrap-around settings
        self.wrap_around = True
        self.wrap_transition_frames = 3

        # Initialize game
        self.reset_game()

    # ------------------------------------
    # Score handling
    # ------------------------------------
    def load_high_score(self) -> int:
        try:
            if os.path.exists('high_score.json'):
                with open('high_score.json', 'r') as f:
                    d = json.load(f)
                    return int(d.get('high_score', 0))
        except Exception:
            pass
        return 0

    def save_high_score(self):
        try:
            with open('high_score.json', 'w') as f:
                json.dump({'high_score': int(self.high_score)}, f)
        except Exception:
            pass

    # ------------------------------------
    # Game setup
    # ------------------------------------
    def reset_game(self):
        self.grid_width = max(4, self.width // self.grid_size)
        self.grid_height = max(4, self.height // self.grid_size)
        start_x = self.grid_width // 2
        start_y = self.grid_height // 2
        self.snake = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.score = 0
        self.game_over = False
        self.speed_boost = False
        self.base_speed = 6
        self.boost_speed = 12
        self.particles = []
        self.transition_particles = []
        self.power_ups = []
        self.paused = False
        self.spawn_fruit()

    def spawn_fruit(self):
        while True:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            if (x, y) not in self.snake and not any((x, y) == p['pos'] for p in self.power_ups):
                self.fruit = (x, y)
                break
        if self.score - self.last_power_up_score >= 30 and random.random() < self.power_up_spawn_chance:
            self.spawn_power_up()
            self.last_power_up_score = self.score

    def spawn_power_up(self):
        while True:
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            if (x, y) not in self.snake and (x, y) != self.fruit:
                self.power_ups.append({'pos': (x, y), 'type': 'star', 'lifespan': 200})
                break

    # ------------------------------------
    # Visual Effects
    # ------------------------------------
    def add_particle_effect(self, x: int, y: int, color=None):
        if color is None:
            color = self.ORANGE
        for _ in range(12):
            particle = {
                'x': x * self.grid_size + self.grid_size // 2,
                'y': y * self.grid_size + self.grid_size // 2,
                'vx': random.uniform(-4, 4),
                'vy': random.uniform(-4, 4),
                'life': 40,
                'max_life': 40,
                'color': color
            }
            self.particles.append(particle)

    def _add_transition_trail(self, grid_x: int, grid_y: int):
        """Add a short fading trail when snake wraps across the screen."""
        for _ in range(8):
            particle = {
                'x': grid_x * self.grid_size + self.grid_size // 2,
                'y': grid_y * self.grid_size + self.grid_size // 2,
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-1, 1),
                'life': self.wrap_transition_frames,
                'max_life': self.wrap_transition_frames,
                'color': (0, 200, 255)
            }
            self.transition_particles.append(particle)

    # ------------------------------------
    # Core Game Logic
    # ------------------------------------
    def update_particles(self):
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.2
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)

    def update_power_ups(self):
        for pu in self.power_ups[:]:
            pu['lifespan'] -= 1
            if pu['lifespan'] <= 0:
                self.power_ups.remove(pu)

    def change_direction(self, new_direction: str):
        if self.game_over or self.paused:
            return
        mapping = {"UP": Direction.UP, "DOWN": Direction.DOWN,
                   "LEFT": Direction.LEFT, "RIGHT": Direction.RIGHT}
        if new_direction in mapping:
            new_dir = mapping[new_direction]
            opposite = {
                Direction.UP: Direction.DOWN,
                Direction.DOWN: Direction.UP,
                Direction.LEFT: Direction.RIGHT,
                Direction.RIGHT: Direction.LEFT
            }
            if new_dir != opposite.get(self.direction):
                self.next_direction = new_dir

    def toggle_pause(self):
        self.paused = not self.paused

    def toggle_wrap(self):
        self.wrap_around = not self.wrap_around
        print(f"Wrap-around {'ENABLED' if self.wrap_around else 'DISABLED'}")

    def set_speed_boost(self, boost: bool):
        self.speed_boost = bool(boost)

    def update(self):
        if self.game_over or self.paused:
            return
        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)

        # --- WRAP-AROUND MOVEMENT ---
        if self.wrap_around:
            if new_head[0] < 0:
                new_head = (self.grid_width - 1, new_head[1])
                self._add_transition_trail(0, new_head[1])
            elif new_head[0] >= self.grid_width:
                new_head = (0, new_head[1])
                self._add_transition_trail(self.grid_width - 1, new_head[1])
            elif new_head[1] < 0:
                new_head = (new_head[0], self.grid_height - 1)
                self._add_transition_trail(new_head[0], 0)
            elif new_head[1] >= self.grid_height:
                new_head = (new_head[0], 0)
                self._add_transition_trail(new_head[0], self.grid_height - 1)
        else:
            # --- CLASSIC WALL COLLISION ---
            if (new_head[0] < 0 or new_head[0] >= self.grid_width or
                    new_head[1] < 0 or new_head[1] >= self.grid_height):
                self.game_over = True
                if self.score > self.high_score:
                    self.high_score = self.score
                    self.save_high_score()
                return

        # --- SELF COLLISION ---
        if new_head in self.snake:
            self.game_over = True
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            return

        # --- UPDATE POSITION ---
        self.snake.insert(0, new_head)

        # Fruit collision
        if new_head == self.fruit:
            self.score += 10
            self.add_particle_effect(new_head[0], new_head[1], self.RED)
            self.spawn_fruit()
        else:
            self.snake.pop()

        # Power-up collision
        for pu in self.power_ups[:]:
            if new_head == pu['pos']:
                self.score += 20
                self.add_particle_effect(new_head[0], new_head[1], self.YELLOW)
                self.power_ups.remove(pu)

        self.update_particles()
        self.update_power_ups()

    # ------------------------------------
    # Drawing
    # ------------------------------------
    def draw_snake_segment(self, surface, x: int, y: int, is_head: bool = False):
        px = x * self.grid_size
        py = y * self.grid_size
        rect = pygame.Rect(px + 1, py + 1, self.grid_size - 2, self.grid_size - 2)
        if is_head:
            pygame.draw.rect(surface, self.LIGHT_GREEN, rect)
            eye_size = 3
            pygame.draw.rect(surface, self.BLACK, pygame.Rect(px + 5, py + 5, eye_size, eye_size))
            pygame.draw.rect(surface, self.BLACK, pygame.Rect(px + 12, py + 5, eye_size, eye_size))
        else:
            pygame.draw.rect(surface, self.NOKIA_GREEN, rect)
        pygame.draw.rect(surface, self.DARK_GREEN, rect, 1)

    def draw_fruit(self, surface):
        x, y = self.fruit
        px = x * self.grid_size
        py = y * self.grid_size
        glow = pygame.Rect(px - 2, py - 2, self.grid_size + 4, self.grid_size + 4)
        pygame.draw.rect(surface, self.ORANGE, glow, 2)
        fruit_rect = pygame.Rect(px + 2, py + 2, self.grid_size - 4, self.grid_size - 4)
        pygame.draw.rect(surface, self.RED, fruit_rect)
        shine = pygame.Rect(px + 4, py + 4, 4, 4)
        pygame.draw.rect(surface, self.WHITE, shine)

    def draw_power_ups(self, surface):
        for pu in self.power_ups:
            x, y = pu['pos']
            px = x * self.grid_size
            py = y * self.grid_size
            if pu['lifespan'] % 20 < 10:
                pygame.draw.rect(surface, self.YELLOW, pygame.Rect(px + 3, py + 3, self.grid_size - 6, self.grid_size - 6))
                cx = px + self.grid_size // 2
                cy = py + self.grid_size // 2
                pygame.draw.circle(surface, self.CYAN, (cx, cy), 3)

    def draw_particles(self, surface):
        """Draw fruit and wrap transition particles."""
        for p in self.particles[:]:
            life_frac = max(0.0, p['life'] / float(p['max_life']))
            alpha = int(255 * life_frac)
            size = max(1, int(4 * life_frac))
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            color = (*p['color'], alpha)
            pygame.draw.circle(surf, color, (size, size), size)
            surface.blit(surf, (int(p['x'] - size), int(p['y'] - size)))
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)

        for p in self.transition_particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            life_frac = max(0.0, p['life'] / float(p['max_life']))
            alpha = int(180 * life_frac)
            size = int(3 + 4 * life_frac)
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            color = (*p['color'], alpha)
            pygame.draw.circle(surf, color, (size, size), size)
            surface.blit(surf, (int(p['x'] - size), int(p['y'] - size)))
            if p['life'] <= 0:
                self.transition_particles.remove(p)

    def draw_grid(self, surface):
        for x in range(0, self.width, self.grid_size):
            pygame.draw.line(surface, (30, 30, 30), (x, 0), (x, self.height))
        for y in range(0, self.height, self.grid_size):
            pygame.draw.line(surface, (30, 30, 30), (0, y), (self.width, y))
        if self.wrap_around:
            edge_glow = pygame.Surface((self.width, 10), pygame.SRCALPHA)
            edge_glow.fill((0, 255, 255, 40))
            surface.blit(edge_glow, (0, 0))
            surface.blit(edge_glow, (0, self.height - 10))

    def draw_ui(self):
        score_text = self.font.render(f"Score: {self.score}", True, self.WHITE)
        self.screen.blit(score_text, (10, 10))
        high_text = self.small_font.render(f"High: {self.high_score}", True, self.YELLOW)
        self.screen.blit(high_text, (10, 45))
        mode_text = self.small_font.render(f"Mode: {'WRAP' if self.wrap_around else 'CLASSIC'}", True, self.CYAN)
        self.screen.blit(mode_text, (10, 70))

        if self.speed_boost:
            boost_text = self.small_font.render("SPEED BOOST!", True, self.CYAN)
            self.screen.blit(boost_text, (10, 95))

        if self.paused:
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(160)
            overlay.fill(self.BLACK)
            self.screen.blit(overlay, (0, 0))
            pause = self.font.render("PAUSED", True, self.WHITE)
            self.screen.blit(pause, (self.width // 2 - pause.get_width() // 2, self.height // 2))

        if self.game_over:
            overlay = pygame.Surface((self.width, self.height))
            overlay.set_alpha(200)
            overlay.fill(self.BLACK)
            self.screen.blit(overlay, (0, 0))
            go = self.font.render("GAME OVER", True, self.WHITE)
            fs = self.font.render(f"Score: {self.score}", True, self.WHITE)
            if self.score == self.high_score and self.score > 0:
                hs = self.small_font.render("NEW HIGH SCORE!", True, self.YELLOW)
                self.screen.blit(hs, (self.width // 2 - hs.get_width() // 2, self.height // 2 - 60))
            restart = self.small_font.render("Show 'UP' to restart", True, self.NOKIA_GREEN)
            self.screen.blit(go, (self.width // 2 - go.get_width() // 2, self.height // 2 - 20))
            self.screen.blit(fs, (self.width // 2 - fs.get_width() // 2, self.height // 2 + 20))
            self.screen.blit(restart, (self.width // 2 - restart.get_width() // 2, self.height // 2 + 60))

    def draw(self):
        if self.screen is None:
            return
        self.screen.fill(self.BLACK)
        self.draw_grid(self.screen)
        if not self.game_over:
            for i, seg in enumerate(self.snake):
                self.draw_snake_segment(self.screen, seg[0], seg[1], i == 0)
            self.draw_fruit(self.screen)
            self.draw_power_ups(self.screen)
            self.draw_particles(self.screen)
        self.draw_ui()

    # ------------------------------------
    # Utilities
    # ------------------------------------
    def handle_restart(self, gesture: Optional[str]):
        if self.game_over and gesture == "UP":
            self.reset_game()

    def get_current_speed(self) -> int:
        return self.boost_speed if self.speed_boost else self.base_speed
