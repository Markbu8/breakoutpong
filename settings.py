class ScreenSettings:
    def __init__(self):
        # Screen settings
        self.init_screen_size = (1280, 720)
        self.screen_size = [1280, 720]
        self.screen_size_scale_dif = [1, 1]
        self.prev_screen_size = [1280, 720]
        self.prev_screen_size_scale_dif = [1, 1]
        self.frame_rate = 60

        # Visual settings
        self.line_width = 2

        # Ball settings
        self.ball_radius = 10

        self._base_line_width = self.line_width

    def screensize_change(self):
        self.screen_size = [self.screen.get_rect().width, self.screen.get_rect().height]
        self.screen_size_scale_dif = [
            self.screen_size[0] / self.init_screen_size[0],
            self.screen_size[1] / self.init_screen_size[1],
        ]
        self.prev_screen_size_scale_dif = [
            self.screen_size[0] / self.prev_screen_size[0],
            self.screen_size[1] / self.prev_screen_size[1],
        ]
        self.prev_screen_size = self.screen_size
        print("SCALED BY:")
        print(self.prev_screen_size_scale_dif)
        self.scale_line()

    def set_screen(self, screen):
        self.screen = screen

    def scale_line(self):
        self.line_width = round(
            self._base_line_width
            * (self.screen_size_scale_dif[0] + self.screen_size_scale_dif[1])
            / 2
        )

    def reset_to_defaults(self):
        self.__init__()


class SpawnSettings:
    def __init__(self):
        # Block Spawn settings
        self.blocks_depth = 3
        self.blocks_size = [2, 10]
        self.health_indicate_descale_percent = 20

        # Paddle Spawn settings
        self.paddle_x_spawn_distance = 2  # number of blocks
        self.paddle_size = [2, 30]


class GameSettings:
    def __init__(self):
        self.modified = False
        # Block settings
        self.blocks_percent_per_sec = 100

        # Paddle settings
        self.paddle_speed = 40  # in percent of screen per second

        # Ball settings
        self.ball_speed = 25  # in percent of screen per second
        self.max_balls = 5
        self.balls_percent_per_sec = 100
        self.block_spawn_positons_none = [[50, 50]]
        self.block_spawn_positons_red = [[50, 25]]
        self.block_spawn_positons_blue = [[50, 75]]

        self.destroy_ball_on_collision = False
        self.destroy_ball_on_kill = False

        self.destroy_neutral_ball_on_collision = True
        self.destroy_neutral_ball_on_kill = True

        # AI settings
        self.blue_ai = False
        self.red_ai = True
        self.blue_ai_difficulty = 3
        self.red_ai_difficulty = 4

        # Collision rules
        self.paddle_back_collide = False
        self.paddle_self_collide = True


class UIGameSettings(GameSettings):
    def __init__(self):
        super().__init__()
        # Block settings
        self.blocks_percent_per_sec = 25

        # Paddle settings
        self.paddle_speed = 40  # in percent of screen per second

        # Ball settings
        self.ball_speed = 15  # in percent of screen per second
        self.max_balls = 5
        self.balls_percent_per_sec = 25
        self.block_spawn_positons_none = [[50, 25], [50, 75]]
        self.block_spawn_positons_red = [[25, 25], [75, 25], [25, 75], [75, 75]]
        self.block_spawn_positons_blue = [[25, 25], [75, 25], [25, 75], [75, 75]]

        self.destroy_ball_on_collision = False
        self.destroy_ball_on_kill = False

        self.destroy_neutral_ball_on_collision = True
        self.destroy_neutral_ball_on_kill = True

        # AI settings
        self.blue_ai = True
        self.red_ai = True
        self.blue_ai_difficulty = 1
        self.red_ai_difficulty = 1

        # Collision rules
        self.paddle_back_collide = False
        self.paddle_self_collide = True


# Create singleton instance
screen_settings = ScreenSettings()
spawn_settings = SpawnSettings()
game_settings = UIGameSettings()
