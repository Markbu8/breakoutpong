import pygame
import random
import settings as settings
from gamefiles.blocks import Block
from gamefiles.balls import Ball
from gamefiles.paddles import Paddle
from gamefiles.game_object import Owner
from collections import deque
import copy


def initialize_walls():
    walls = pygame.sprite.Group()
    screen_width, screen_height = settings.screen_settings.screen_size
    # walls
    walls.add(Block(Owner.GLOBAL, 0, -1000, screen_width, 1000))
    walls.add(Block(Owner.GLOBAL, -1000, 0, 1000, screen_height))
    walls.add(Block(Owner.GLOBAL, screen_width, 0, 1000, screen_height))
    walls.add(Block(Owner.GLOBAL, 0, screen_height, screen_width, 1000))

    return walls


def initialize_paddles():
    screen_width = settings.screen_settings.screen_size[0]

    pad_x = (
        (
            (
                settings.spawn_settings.blocks_size[0]
                * settings.spawn_settings.blocks_depth
            )
            + (
                settings.spawn_settings.paddle_x_spawn_distance
                * settings.spawn_settings.blocks_size[0]
            )
        )
        * 0.01
        * screen_width
    )

    paddle_blue = Paddle(Owner.BLUE, pad_x, pygame.K_w, pygame.K_s)

    paddle_red = Paddle(
        Owner.RED,
        screen_width
        - pad_x
        - (settings.spawn_settings.paddle_size[0] * 0.01 * screen_width),
        pygame.K_i,
        pygame.K_k,
    )

    return paddle_red, paddle_blue


class BuildBalls:
    def __init__(
        self,
        owner,
        max_balls,
        balls_percent_per_sec,
        spawn_positions,
    ):
        self.percent_spawn_positions = spawn_positions
        self.real_spawn_positions = copy.deepcopy(self.percent_spawn_positions)
        self.set_real_spawn_positions()
        self.steps = 0
        self.block_add_list = deque()
        self.owner = owner
        self.max_balls = max_balls
        self.balls_per_sec = (
            balls_percent_per_sec * 0.01 * max_balls
        ) / settings.screen_settings.frame_rate

    def screensize_change(self):
        self.set_real_spawn_positions()

    def set_balls_per_sec(self, balls_percent_per_sec, max_balls):
        self.balls_per_sec = (
            balls_percent_per_sec * 0.01 * max_balls
        ) / settings.screen_settings.frame_rate

    def set_real_spawn_positions(self):
        self.real_spawn_positions = []
        for s in self.percent_spawn_positions:
            self.real_spawn_positions.append(
                (
                    round(s[0] * 0.01 * settings.screen_settings.screen_size[0]),
                    round(s[1] * 0.01 * settings.screen_settings.screen_size[1]),
                )
            )

    def add_to_spawn_queue(self, pos, velocity, abs_speed=False):
        self.block_add_list.append(Ball(self.owner, pos, velocity, abs_speed))

    def step(self, balls):
        for _ in range(len(self.block_add_list)):
            balls.add(self.block_add_list.popleft())
        if len(balls) >= self.max_balls:
            return
        self.steps += self.balls_per_sec
        while self.steps >= 1:
            self.steps -= 1
            balls.add(
                Ball(
                    self.owner,
                    random.choice(self.real_spawn_positions),
                    pygame.Vector2(0, 1).rotate(random.uniform(0, 360)),
                )
            )


class BuildBallsBlue(BuildBalls):
    def __init__(self):
        super().__init__(
            Owner.BLUE,
            settings.game_settings.max_balls,
            settings.game_settings.balls_percent_per_sec,
            settings.game_settings.block_spawn_positons_blue,
        )


class BuildBallsRed(BuildBalls):
    def __init__(self):
        super().__init__(
            Owner.RED,
            settings.game_settings.max_balls,
            settings.game_settings.balls_percent_per_sec,
            settings.game_settings.block_spawn_positons_red,
        )


class BuildBallsNone(BuildBalls):
    def __init__(self):
        super().__init__(
            Owner.GLOBAL,
            0,
            settings.game_settings.balls_percent_per_sec,
            settings.game_settings.block_spawn_positons_none,
        )


class BuildBlocks:
    def __init__(self, blocks_percent_per_sec):
        self.x = 0
        self.y = 0
        self.blocks_queue = deque()
        self.steps = 0
        self.total_blocks = 0
        self.blocks_percent_per_sec = blocks_percent_per_sec
        self.blocks_per_sec = 0
        self.screensize_change()

    def set_total_size(self, temp_list):
        random.shuffle(temp_list)
        for r in temp_list:
            self.blocks_queue.append(r)
        self.total_blocks = len(self.blocks_queue)
        self.blocks_per_sec = (
            self.blocks_percent_per_sec * 0.01 * self.total_blocks
        ) / settings.screen_settings.frame_rate

    def screensize_change(self):
        self.block_size = (
            round(
                settings.spawn_settings.blocks_size[0]
                * 0.01
                * settings.screen_settings.screen_size[0]
            ),
            round(
                settings.spawn_settings.blocks_size[1]
                * 0.01
                * settings.screen_settings.screen_size[1]
            ),
        )
        self.remainder = (100 % self.block_size[0], 100 % self.block_size[1])
        self.remainder_per = (
            (
                round((100 // self.block_size[0]) / self.remainder[0])
                if self.remainder[0] > 0
                else 0
            ),
            (
                round((100 // self.block_size[1]) / self.remainder[1])
                if self.remainder[1] > 0
                else 0
            ),
        )

        new_queue = deque()
        for i in range(len(self.blocks_queue)):
            temp_block = self.blocks_queue.popleft()
            temp_block.screensize_change()
            new_queue.append(temp_block)
        self.blocks_queue = new_queue

    def step(self, blocks):
        q_size = len(self.blocks_queue)
        if q_size == 0:
            return
        self.steps += min(self.blocks_per_sec, q_size)
        while self.steps >= 1:
            self.steps -= 1
            blocks.add(self.blocks_queue.popleft())


class BuildBlocksBlue(BuildBlocks):
    def __init__(self, blocks_percent_per_sec=None):
        if blocks_percent_per_sec is None:
            blocks_percent_per_sec = settings.game_settings.blocks_percent_per_sec
        super().__init__(blocks_percent_per_sec)
        temp_list = []
        for j in range(
            0,
            settings.screen_settings.screen_size[1],
            self.block_size[1] + self.remainder_per[1],
        ):
            for i in range(
                0,
                self.block_size[0] * settings.spawn_settings.blocks_depth,
                self.block_size[0] + self.remainder_per[0],
            ):
                temp_list.append(Block(Owner.BLUE, i, j, randomize_type=True))
        self.set_total_size(temp_list)


class BuildBlocksRed(BuildBlocks):
    def __init__(self, blocks_percent_per_sec=None):
        if blocks_percent_per_sec is None:
            blocks_percent_per_sec = settings.game_settings.blocks_percent_per_sec
        super().__init__(blocks_percent_per_sec)
        self.base_x = settings.screen_settings.screen_size[0] - self.remainder_per[0]
        self.x = self.base_x
        temp_list = []
        for j in range(
            0,
            settings.screen_settings.screen_size[1],
            self.block_size[1] + self.remainder_per[1],
        ):
            for i in range(
                settings.screen_settings.screen_size[0] - self.block_size[0],
                settings.screen_settings.screen_size[0]
                - (self.block_size[0] * (settings.spawn_settings.blocks_depth + 1)),
                -self.block_size[0] + self.remainder_per[0],
            ):
                temp_list.append(Block(Owner.RED, i, j, randomize_type=True))
        self.set_total_size(temp_list)
