import pygame
import settings as settings
from enum import Enum


class Owner(Enum):
    BLUE = "blue"
    RED = "red"
    MENU = "grey"
    GLOBAL = "white"


class GameObject(pygame.sprite.Sprite):
    def __init__(self, owner, rect, color=None, rect_as_percent_of_screen=False):
        if hasattr(self, "containers"):
            super().__init__(self.containers)
        else:
            super().__init__()
        self.owner = owner
        if not color:
            self.color = owner.value
        else:
            self.color = color

        self.rect = rect.copy()

        if rect_as_percent_of_screen:
            self.scale_self_to_screen_percent()

    def scale_self(self):
        self.rect = pygame.Rect(
            round(
                self.rect.left * settings.screen_settings.prev_screen_size_scale_dif[0]
            ),
            round(
                self.rect.top * settings.screen_settings.prev_screen_size_scale_dif[1]
            ),
            round(
                self.rect.width * settings.screen_settings.prev_screen_size_scale_dif[0]
            ),
            round(
                self.rect.height
                * settings.screen_settings.prev_screen_size_scale_dif[1]
            ),
        )

    def inflate_percent_ip(self, x, y):
        self.rect.width = round(self.rect.width * (100 + x) * 0.01)
        self.rect.height = round(self.rect.height * (100 + y) * 0.01)

    def inflate_percent(self, x, y):
        temp_rect = self.rect.copy()
        temp_rect.width = round(self.rect.width * (100 + x) * 0.01)
        temp_rect.height = round(self.rect.height * (100 + y) * 0.01)
        temp_rect.center = self.rect.center
        return temp_rect

    def inflate_percent_longest(self, val):
        temp_rect = self.rect.copy()
        if self.rect.width < self.rect.height:
            temp_rect.width = round(self.rect.width * (100 + val) * 0.01)
            temp_rect.height += temp_rect.width - self.rect.width
        else:
            temp_rect.height = round(self.rect.height * (100 + val) * 0.01)
            temp_rect.width += temp_rect.height - self.rect.height

        temp_rect.center = self.rect.center
        return temp_rect

    def scale_self_to_screen_percent(self):
        x, y = self.get_screen_percent_pixels(self.rect.x, self.rect.y)
        width, height = self.get_screen_percent_pixels(
            self.rect.width, self.rect.height
        )
        self.rect = pygame.Rect(x, y, width, height)

    def scale_vect_2(self, vect2):
        return pygame.Vector2(
            vect2.x * settings.screen_settings.screen_size_scale_dif[0],
            vect2.y * settings.screen_settings.screen_size_scale_dif[1],
        )

    def scale_1d(self, float):
        return (
            float
            * (
                settings.screen_settings.screen_size_scale_dif[0]
                + settings.screen_settings.screen_size_scale_dif[1]
            )
            / 2
        )

    def scale_1d_round(self, float):
        return round(
            float
            * (
                settings.screen_settings.screen_size_scale_dif[0]
                + settings.screen_settings.screen_size_scale_dif[1]
            )
            / 2
        )

    def get_screen_percent_pixels(self, x, y):
        return round(x * 0.01 * settings.screen_settings.screen_size[0]), round(
            y * 0.01 * settings.screen_settings.screen_size[1]
        )

    def get_screen_percent_pixels_pos(self, pos):
        return round(pos[0] * 0.01 * settings.screen_settings.screen_size[0]), round(
            pos[1] * 0.01 * settings.screen_settings.screen_size[1]
        )

    def get_screen_percent_pixels_x(self, float):
        return round(float * 0.01 * settings.screen_settings.screen_size[0])

    def get_screen_percent_pixels_y(self, float):
        return round(float * 0.01 * settings.screen_settings.screen_size[1])
