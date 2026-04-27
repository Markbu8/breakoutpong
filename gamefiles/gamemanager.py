import pygame
import time
from gamefiles.ui import UI
import settings
from gamefiles.initialize_objects import *


class GameManager:
    def __init__(self, screen):
        pygame.display.set_caption("Breakout Pong")
        self.screen = screen
        self.ui = UI(self)
        self.score = self.ui.score_board
        self.score_list = self.score.sprites()
        self.ui_collisions = self.ui.ui_collisions
        self.ui_render = self.ui.ui_render
        self.paused = False
        self.reset()
        self.resize_rescale()
        self.count = 0
        self.totaltime = 0

    def reset(
        self,
        reset_blocks=True,
        reset_balls=True,
        reset_paddles=True,
        start_game=None,
        reset_settings=True,
    ):

        self.walls = pygame.sprite.Group()
        self.blocks_red = pygame.sprite.Group()
        self.blocks_blue = pygame.sprite.Group()
        self.balls_none = pygame.sprite.Group()
        self.balls_red = pygame.sprite.Group()
        self.balls_blue = pygame.sprite.Group()

        self.to_reset = False

        self.walls = initialize_walls()

        if reset_paddles:
            self.paddle_red, self.paddle_blue = initialize_paddles()

        self.elements = (
            self.walls,
            self.blocks_red,
            self.blocks_blue,
            self.balls_none,
            self.balls_red,
            self.balls_blue,
        )

        for score in self.score_list:
            score.set_score(0)
        if reset_balls:
            self.BuildBallsBlue = BuildBallsBlue()
            self.BuildBallsRed = BuildBallsRed()
            self.BuildBallsNone = BuildBallsNone()
            self.spawn_balls_dictionary = {
                Owner.RED: self.BuildBallsRed,
                Owner.BLUE: self.BuildBallsBlue,
                Owner.GLOBAL: self.BuildBallsNone,
            }
        if reset_blocks:
            self.BuildBlocksBlue = BuildBlocksBlue()
            self.BuildBlocksRed = BuildBlocksRed()

        self.paddle_blue.ball_lists = [self.balls_none, self.balls_red, self.balls_blue]
        self.paddle_blue.block_list = self.blocks_blue
        self.paddle_red.ball_lists = [self.balls_none, self.balls_red, self.balls_blue]
        self.paddle_red.block_list = self.blocks_red
        if reset_settings:
            if start_game:
                if not settings.game_settings.modified:
                    settings.game_settings = settings.GameSettings()
            else:
                settings.game_settings = settings.UIGameSettings()
            self.paddle_blue.use_ai = settings.game_settings.blue_ai
            self.paddle_blue.difficulty = settings.game_settings.blue_ai_difficulty
            self.paddle_red.use_ai = settings.game_settings.red_ai
            self.paddle_red.difficulty = settings.game_settings.red_ai_difficulty

    def resize_rescale(self):
        settings.screen_settings.screensize_change()
        for element in self.elements:
            for each in element:
                each.screensize_change()
        self.paddle_red.screensize_change()
        self.paddle_blue.screensize_change()
        self.ui.screensize_change()
        self.BuildBlocksBlue.screensize_change()
        self.BuildBlocksRed.screensize_change()
        self.BuildBallsBlue.screensize_change()
        self.BuildBallsRed.screensize_change()

    def draw(self):
        pass

    def toggle_paused(self):
        self.paused = not self.paused
        self.ui.toggle_paused(force=True)

    def mouse_down(self):
        self.ui.get_clicked_classes()

    def update(self, dt):
        start = time.perf_counter()
        self.ui.update()
        if not self.paused:
            self.step()
            self.children_update(dt)
            self.all_collisions()

        if self.to_reset:
            if self.ui.game_started:
                self.ui.start_game()
            else:
                self.reset(True, True, True, False, False)

        self.screen.fill((0, 0, 0))
        self.ui.draw(self.screen)
        for element in self.elements:
            for each in element:
                each.draw(self.screen)
        self.paddle_red.draw(self.screen)
        self.paddle_blue.draw(self.screen)

        self.totaltime += time.perf_counter() - start
        self.count += 1
        if self.count > 599:
            print(f"ten sec avg ms: {self.totaltime/600*1000}")
            self.count = 0
            self.totaltime = 0

    def children_update(self, dt):
        keys = pygame.key.get_pressed()
        self.paddle_red.update(
            dt,
            keys,
            settings.game_settings.red_ai,
            settings.game_settings.red_ai_difficulty,
        )

        self.paddle_blue.update(
            dt,
            keys,
            settings.game_settings.blue_ai,
            settings.game_settings.blue_ai_difficulty,
        )
        for element in self.elements:
            element.update(dt)

    def step(self):
        self.BuildBlocksBlue.step(self.blocks_blue)
        self.BuildBlocksRed.step(self.blocks_red)
        self.BuildBallsBlue.step(self.balls_blue)
        self.BuildBallsRed.step(self.balls_red)
        self.BuildBallsNone.step(self.balls_none)

    def all_collisions(self):

        paddle_red = self.paddle_red
        paddle_blue = self.paddle_blue
        walls = self.walls
        balls_red = self.balls_red
        balls_blue = self.balls_blue
        blocks_red = self.blocks_red
        blocks_blue = self.blocks_blue
        balls_none = self.balls_none

        self.collisions(balls_none, self.ui_collisions)
        self.collisions(balls_red, self.ui_collisions)
        self.collisions(balls_blue, self.ui_collisions)

        self.collisions(balls_none, walls)
        self.collisions(balls_red, walls)
        self.collisions(balls_blue, walls)

        self.collisions(balls_none, blocks_red, do_kill=True)
        self.collisions(balls_none, blocks_blue, do_kill=True)
        self.collisions(balls_red, blocks_red, skip_if=self.in_front_of_right_paddle)
        self.collisions(
            balls_blue, blocks_red, skip_if=self.in_front_of_right_paddle, do_kill=True
        )
        self.collisions(
            balls_red, blocks_blue, skip_if=self.in_front_of_left_paddle, do_kill=True
        )
        self.collisions(balls_blue, blocks_blue, skip_if=self.in_front_of_left_paddle)

        if settings.game_settings.paddle_back_collide:
            if settings.game_settings.paddle_self_collide:
                self.collisions(balls_red, paddle_red)
                self.collisions(balls_blue, paddle_blue)
            self.collisions(balls_none, paddle_red)
            self.collisions(balls_none, paddle_blue)
            self.collisions(balls_blue, paddle_red)
            self.collisions(balls_red, paddle_blue)
        else:
            if settings.game_settings.paddle_self_collide:
                self.collisions(balls_red, paddle_red, skip_if=self.going_left)
                self.collisions(balls_blue, paddle_blue, skip_if=self.going_right)
            self.collisions(balls_none, paddle_red, skip_if=self.going_left)
            self.collisions(balls_none, paddle_blue, skip_if=self.going_right)
            self.collisions(balls_blue, paddle_red, skip_if=self.going_left)
            self.collisions(balls_red, paddle_blue, skip_if=self.going_right)

    # keep_if is unused currently; kept for API symmetry with skip_if
    def collisions(self, balls, blocks, keep_if=None, skip_if=None, do_kill=False):
        if self.to_reset:
            return
        if isinstance(blocks, pygame.sprite.Sprite):
            blocks = [blocks]
        if keep_if:
            balls = filter(keep_if, balls)
        if skip_if:
            balls = filter(lambda b: not skip_if(b), balls)

        for ball in balls:
            block = pygame.sprite.spritecollideany(ball, blocks)
            if ball.bounce(block) is False or do_kill is False:
                continue
            count, speed, score, spawn_type, is_killed = block.hit()
            ball.velocity *= speed
            self.spawn_balls(count, speed, ball, spawn_type)
            if ball.owner is Owner.GLOBAL:
                if settings.game_settings.destroy_neutral_ball_on_collision or (
                    settings.game_settings.destroy_neutral_ball_on_kill and is_killed
                ):
                    ball.kill()
            else:
                if settings.game_settings.destroy_ball_on_collision or (
                    settings.game_settings.destroy_ball_on_kill and is_killed
                ):
                    ball.kill()

            if len(blocks) < 1:
                self.to_reset = True
            else:
                self.add_score(ball, score)

    def spawn_balls(self, count, speed, ball, spawn_type):
        if not spawn_type:
            spawn_type = ball.owner
        for _ in range(count):
            self.spawn_balls_dictionary[spawn_type].add_to_spawn_queue(
                ball.rect.center,
                ball.velocity.rotate(random.uniform(-45, 45)) * speed,
                True,
            )

    def add_score(self, ball, amount=1):
        if ball.owner is Owner.RED:
            self.score_list[1].add_score(amount)
        elif ball.owner is Owner.BLUE:
            self.score_list[0].add_score(amount)

    # side, velocity, and lower than padde pos optimization
    def going_right(self, ball):
        return ball.velocity.x > 0

    def going_left(self, ball):
        return ball.velocity.x < 0

    def in_front_of_left_paddle(self, ball):
        return ball.rect.right > self.paddle_blue.rect.left

    def in_front_of_right_paddle(self, ball):
        return ball.rect.left < self.paddle_red.rect.right
