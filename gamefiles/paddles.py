import pygame
import math
from gamefiles.blocks import Block
from gamefiles.game_object import Owner
import settings


class Paddle(Block):
    def __init__(self, owner, x, up_key, down_key):
        super().__init__(
            owner,
            x,
            settings.screen_settings.screen_size[1] / 2
            - (
                settings.spawn_settings.paddle_size[1]
                * 0.01
                * settings.screen_settings.screen_size[1]
            )
            / 2,
            settings.spawn_settings.paddle_size[0]
            * 0.01
            * settings.screen_settings.screen_size[0],
            settings.spawn_settings.paddle_size[1]
            * 0.01
            * settings.screen_settings.screen_size[1],
        )
        self.y_velocity = 0
        self.block_count = 0
        self.blocks_avg_pos = pygame.Vector2(0, 0)
        self.up_key = up_key
        self.down_key = down_key
        self.ball_lists = None
        self.block_list = None
        self.half_x = settings.screen_settings.screen_size[0] / 2
        self.half_y = settings.screen_settings.screen_size[1] / 2
        self.paddle_speed_screensize_adjusted = 1
        if owner is Owner.BLUE:
            self.side_filter = self.AI_optimize_screen_left
            self.direction_filter = self.AI_optimize_going_left
        else:
            self.side_filter = self.AI_optimize_screen_right
            self.direction_filter = self.AI_optimize_going_right

    def screensize_change(self):
        self.scale_self()
        self.half_x = settings.screen_settings.screen_size[0] / 2
        self.half_y = settings.screen_settings.screen_size[1] / 2

    def draw(self, screen):
        pygame.draw.rect(
            screen, self.color, self.rect, settings.screen_settings.line_width
        )
        pygame.draw.rect(
            screen,
            self.color,
            self.inflate_percent_longest(
                settings.spawn_settings.health_indicate_descale_percent * 2
            ),
            settings.screen_settings.line_width,
        )

    def update(self, dt, keys, use_ai, difficulty):
        self.y_velocity = 0
        if keys[self.up_key]:
            self.move_up(dt)
            return
        elif keys[self.down_key]:
            self.move_down(dt)
            return
        if use_ai:
            self.AI(dt, difficulty)

    def set_block_avg_pos(self, blocks):
        if len(blocks) > 0 and self.block_count != len(blocks):
            blocks_tot_pos = pygame.Vector2(0, 0)
            for block in blocks:
                blocks_tot_pos += block.rect.center
            self.blocks_avg_pos = blocks_tot_pos.elementwise() / len(blocks)
            self.block_count = len(blocks)

    def move_up(self, dt, speed=1):
        if self.rect.top > 0:
            self.move(dt, -speed)

    def move_down(self, dt, speed=1):
        if self.rect.bottom < settings.screen_settings.screen_size[1]:
            self.move(dt, speed)

    def move(self, dt, speed=1):
        self.y_velocity = (
            settings.game_settings.paddle_speed
            * 0.01
            * settings.screen_settings.screen_size[1]
            * speed
            * dt
        )
        self.rect.centery += self.y_velocity

    def AI_optimize_screen_left(self, ball):
        return ball.rect.centerx < self.half_x

    def AI_optimize_screen_right(self, ball):
        return ball.rect.centerx > self.half_x

    def AI_optimize_going_right(self, ball):
        return ball.velocity.x > 0

    def AI_optimize_going_left(self, ball):
        return ball.velocity.x < 0

    def AI_remove_own_balls(self, ball):
        return ball.owner != self.owner

    def get_closest(self, ball_group, pos=None):
        if pos is None:
            pos = self.rect.centerx
        closest_dist = math.inf
        closest = None
        for ball in ball_group:
            dist = abs(ball.rect.centerx - pos)
            if dist < closest_dist:
                closest = ball
                closest_dist = dist
        return closest

    def AI(self, dt, difficulty):
        if self.ball_lists is None:
            return
        closest = None
        ball_group_base = [item for sublist in self.ball_lists for item in sublist]
        ball_group = ball_group_base
        ball_group = filter(self.side_filter, ball_group)
        ball_group = filter(self.direction_filter, ball_group)

        # protect avg location of blocks | speed 2+
        if difficulty >= 4:
            ball_group = filter(self.AI_remove_own_balls, ball_group)

            if self.block_list is not None:
                self.set_block_avg_pos(self.block_list)

            if self.blocks_avg_pos != pygame.Vector2(0, 0):
                closest = self.get_closest(ball_group, pos=self.blocks_avg_pos.x)
            else:
                closest = self.get_closest(ball_group)

        # only targets enemy balls | speed 1.5
        elif difficulty >= 3:
            ball_group = filter(self.AI_remove_own_balls, ball_group)
            closest = self.get_closest(ball_group)

        # closest ball going to it | speed 1
        elif difficulty >= 2:
            closest = self.get_closest(ball_group)
        # just gets closest|speed 0.5
        else:
            closest = self.get_closest(ball_group_base)

        move_speed = difficulty * 0.5

        if closest is None:
            if self.rect.centery > self.half_y + (self.rect.height / 4):
                self.move_up(dt, move_speed / 2)
            elif self.rect.centery < self.half_y - (self.rect.height / 4):
                self.move_down(dt, move_speed / 2)
            return

        clo_centery = closest.rect.centery
        if clo_centery > self.rect.bottom:
            self.move_down(dt, move_speed)
        elif clo_centery > self.rect.centery:
            self.move_down(dt, move_speed / 2)
        elif clo_centery < self.rect.top:
            self.move_up(dt, move_speed)
        elif clo_centery < self.rect.centery:
            self.move_up(dt, move_speed / 2)
