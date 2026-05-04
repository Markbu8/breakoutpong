import pygame
from gamefiles.paddles import Paddle
from gamefiles.game_object import GameObject, Owner
import settings as settings


class Ball(GameObject):
    def __init__(self, owner, pos, velocity, abs_speed=False):
        self.pos = pygame.Vector2(pos)
        if abs_speed is True:
            self.velocity = pygame.Vector2(velocity[0], velocity[1])
        else:
            self.velocity = pygame.Vector2(
                velocity[0] * settings.screen_settings.screen_size[0] * 0.01,
                velocity[1] * settings.screen_settings.screen_size[1] * 0.01,
            )
        collider_offset = (
            self.velocity.length() / settings.screen_settings.frame_rate * 2
        )
        init_rect = pygame.Rect(
            0,
            0,
            settings.screen_settings.ball_radius * 2,
            settings.screen_settings.ball_radius * 2,
        )
        init_rect.inflate_ip(collider_offset, collider_offset)
        init_rect.centerx = pos[0]
        init_rect.centery = pos[1]
        super().__init__(owner, init_rect)
        self.base_radius = settings.screen_settings.ball_radius
        self.radius = self.scale_1d(self.base_radius)
        self.color = owner.value

    def screensize_change(self):
        self.scale_self()
        self.pos = self.scale_vect_2(self.pos)
        self.velocity = self.scale_vect_2(self.velocity)
        self.radius = self.scale_1d(self.base_radius)

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            self.rect.center,
            self.radius,
            settings.screen_settings.line_width,
        )

    def update(self, dt):
        self.pos += self.velocity * dt * settings.game_settings.ball_speed
        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def bounce(self, block):
        if block is None:
            return False

        rect = block.rect
        vel = self.velocity
        ball_rect = self.rect

        ball_center = pygame.Vector2(ball_rect.center)
        r = self.radius

        min_pen = float("inf")
        normal = None

        pen = (ball_center.x + r) - rect.left
        if 0 < pen < min_pen:
            min_pen, normal = pen, pygame.Vector2(-1, 0)

        pen = rect.right - (ball_center.x - r)
        if 0 < pen < min_pen:
            min_pen, normal = pen, pygame.Vector2(1, 0)

        pen = (ball_center.y + r) - rect.top
        if 0 < pen < min_pen:
            min_pen, normal = pen, pygame.Vector2(0, -1)

        pen = rect.bottom - (ball_center.y - r)
        if 0 < pen < min_pen:
            min_pen, normal = pen, pygame.Vector2(0, 1)

        if normal is None:
            return False

        # prevent bouncing if moving away
        if vel.dot(normal) >= 0:
            return False

        self.velocity = vel.reflect(normal)

        if isinstance(block, Paddle):
            self.velocity = self.velocity.rotate(block.y_velocity)

        return True
