import pygame
from gamefiles.game_object import GameObject, Owner
import settings as settings
import random

# chance goes down the list
block_types = {
    "white": {
        "color": "white",
        "chance": 0.1,
        "health": 1,
        "spawn_count_when_killed": 1,
        "spawn_type": Owner.GLOBAL,
    },
    "grey": {
        "color": "grey",
        "chance": 0.1,
        "health": 4,
        "score": 6,
        "speed_change_when_hit": 0.8,
        "spawn_count_when_killed": 5,
    },
    "purple": {
        "color": "purple",
        "chance": 0.05,
        "health": 2,
        "speed_change_when_killed": 1.5,
        "spawn_count_when_killed": 2,
        "spawned_ball_speed": 1.5,
    },
    "yellow": {
        "color": "yellow",
        "chance": 0.05,
        "health": 4,
        "score": 3,
        "speed_change_when_killed": 2,
        "spawned_ball_speed": 2,
    },
    "none": {
        "color": None,
        "chance": 1.0,
    },
}


class Block(GameObject):
    def __init__(
        self, owner, x, y, width=None, height=None, Type="none", randomize_type=False
    ):
        init_rect = pygame.Rect(
            x,
            y,
            settings.spawn_settings.blocks_size[0]
            * 0.01
            * settings.screen_settings.screen_size[0],
            settings.spawn_settings.blocks_size[1]
            * 0.01
            * settings.screen_settings.screen_size[1],
        )

        if width:
            init_rect.width = width
        if height:
            init_rect.height = height

        super().__init__(owner, init_rect)

        self.type = Type
        self.color = owner.value

        if randomize_type:
            for key, value in block_types.items():
                if random.random() <= value["chance"]:
                    self.type = key
                    break
        if self.type == "none":
            self.color = owner.value
        else:
            self.color = block_types[self.type].get("color")

        h = block_types[self.type].get("health")
        if not isinstance(h, int):
            h = 1
        self.health = h

    def screensize_change(self):
        self.scale_self()

    def draw(self, screen):
        for i in range(self.health):
            scale_percent = -(
                i * settings.spawn_settings.health_indicate_descale_percent
            )
            pygame.draw.rect(
                screen,
                self.color,
                self.inflate_percent_longest(scale_percent),
                settings.screen_settings.line_width,
            )

    def hit(self):
        self.health -= 1
        values = block_types[self.type]

        spawn_type = values.get("spawn_type")

        if self.health > 0:
            count = values.get("spawn_count_when_hit")
            speed = values.get("speed_change_when_hit")
            if count is None:
                count = 0
            if speed is None:
                speed = 1
            return count, speed, 0, values.get("spawn_type"), False
        else:
            count = values.get("spawn_count_when_killed")
            speed = values.get("speed_change_when_killed")
            if count is None:
                count = 0
            if speed is None:
                speed = 1
            self.kill()
            score = values.get("score")
            if not score:
                score = 1
            return count, speed, score, values.get("spawn_type"), True
