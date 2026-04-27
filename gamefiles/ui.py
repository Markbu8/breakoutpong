import pygame
import sys
import math
from gamefiles.game_object import GameObject, Owner
import settings

from typing import Any, Optional, Set


class UISettings:
    def __init__(self):
        # UI settings
        # all values in percent of screen
        self.font_size = 20

        self.button_size = [20, 20]

        self.score_size = [10, 10]
        self.score_font_size = 50

        self.slider_size = [20, 4]


ui_settings = UISettings()

# sizes and pos are in percent of screen
# overriding the position of a class, prevents it from being spaced from a Spacing_Function
# (ITEM)_toggleFrame function denotes toggling the top level item/Frame.
# so (Menu)_toggleFrame would toggle the "Menu" in the first dictionary
# (ITEM)_toggle function denotes toggling a bool if it exists
# so (game_settings.blue_ai)_toggleFrame would toggle blue ai on or off
Ui_elements = {
    "Menu": {
        "Enabled": True,
        "Frame_size": [20, 80],
        "Center_pos": [50, 50],
        "Spacing_function": "space_vertical",
        "Classes": {
            "Button": {
                "Start": {
                    "Click_Functions": ["start_game", "(Settings_Menu)_toggleFrame"],
                    "Click_Functions_args": [None, False],
                },
                "Settings": {
                    "Click_Functions": "(Settings_Menu)_toggleFrame",
                },
                "Score and button toggle": {
                    "Click_Functions": [
                        "(Score)_toggleFrame",
                        "(Toggle_UI_Collisions)_toggleFrame",
                        "(Toggle_Pause)_toggleFrame",
                    ],
                },
                "Quit": {"Color": "white", "Click_Functions": ["quit_game"]},
            }
        },
    },
    "Score": {
        "Enabled": True,
        "Frame_size": [
            ui_settings.score_size[0] * 2,
            ui_settings.score_size[1],
        ],
        "Center_pos": [50, ui_settings.score_size[1] / 2],
        "Default_Font_Size": ui_settings.score_font_size,
        "Classes": {
            "Score": {
                "blue": {
                    "Size": ui_settings.score_size,
                    "Color": "blue",
                },
                "red": {
                    "Size": ui_settings.score_size,
                    "Color": "red",
                },
            }
        },
    },
    "Settings_Menu": {
        "Enabled": False,
        "Frame_size": [100, 30],
        "Center_pos": [50, 35],
        "Classes": {
            "Button": {
                "Blue AI": {
                    "Size": [14, 5],
                    "Pos": [6, 5],
                    "Color": "blue",
                    "Setting": "game_settings.blue_ai",
                    "Click_Functions": "(game_settings.blue_ai)_toggle",
                },
                "Red AI": {
                    "Size": [14, 5],
                    "Pos": [80, 5],
                    "Color": "red",
                    "Setting": "game_settings.red_ai",
                    "Click_Functions": "(game_settings.red_ai)_toggle",
                },
                "UI Settings": {
                    "Size": [15, 5],
                    "Pos": [18, 15],
                    "Color": "white",
                    "Click_Functions": "set_game_settings",
                    "Click_Functions_args": settings.UIGameSettings,
                },
                "Game Settings": {
                    "Size": [15, 5],
                    "Pos": [67, 15],
                    "Color": "white",
                    "Click_Functions": "set_game_settings",
                    "Click_Functions_args": settings.GameSettings,
                },
            },
            "Slider": {
                "Ball speed": {
                    "Size": [20, 4],
                    "Color": "green",
                    "Invert": True,
                    "Setting": "game_settings.ball_speed",
                },
                "Paddle speed": {
                    "Size": [20, 4],
                    "Color": "green",
                    "Setting": "game_settings.paddle_speed",
                },
                "Blue difficulty": {
                    "Size": [20, 4],
                    "Min_max": [0, 4],
                    "Color": "blue",
                    "Setting": "game_settings.blue_ai_difficulty",
                },
                "Red difficulty": {
                    "Size": [20, 4],
                    "Min_max": [0, 4],
                    "Color": "red",
                    "Setting": "game_settings.red_ai_difficulty",
                },
            },
        },
    },
    "Toggle_UI_Collisions": {
        "Enabled": True,
        "Frame_size": [20, 20],
        "Center_pos": [30, 10],
        "Spacing_function": "no_spacing",
        "Classes": {
            "Button": {
                "UI Collisions always on": {
                    "Size": [20, 10],
                    "Color": "grey",
                    "Click_Functions": [
                        "toggle_ui_collisions",
                    ],
                },
            }
        },
    },
    "Toggle_Pause": {
        "Enabled": True,
        "Frame_size": [20, 20],
        "Center_pos": [70, 10],
        "Spacing_function": "no_spacing",
        "Classes": {
            "Button": {
                "Resume": {
                    "Size": [20, 10],
                    "Enabled": False,
                    "Color": "blueviolet",
                    "Click_Functions": "toggle_paused",
                },
                "Pause": {
                    "Size": [20, 10],
                    "Enabled": True,
                    "Color": "aqua",
                    "Click_Functions": "toggle_paused",
                },
            },
        },
    },
    "Paused": {
        "Enabled": False,
        "Frame_size": [80, 80],
        "Center_pos": [50, 50],
        "Classes": {
            "Button": {
                "Paused": {
                    "Size": [80, 80],
                    "Font Size": 100,
                    "Color": "aqua",
                },
            },
        },
    },
}

ui_collision_enabled = False


class UI:
    def __init__(self, game_manager):
        self.owner = "UI"
        self.game_manager = game_manager
        self.game_started = False
        self.frames = {}
        self.paused = False
        self.ui_render = pygame.sprite.Group()
        self.ui_collisions = pygame.sprite.Group()
        self.score_board = pygame.sprite.Group()
        for element_key, element_value in Ui_elements.items():
            self.frames[element_key] = Frame(element_key, element_value)
        self.set_btn_score_slider_lists_from_frames()
        self.collided_classes = []
        self.not_collided_classes = []
        self.collided_buttons = []
        self.game_started = False
        self.callable_functions = {
            "start_game": self.start_game,
            "toggle_paused": self.toggle_paused,
            "quit_game": self.quit_game,
            "toggle_ui_collisions": self.toggle_ui_collisions,
            "toggle_frame": self.toggle_frame,
            "toggle_class": self.toggle_class,
            "toggle_spaced": self.toggle_spaced,
            "set_game_settings": self.set_game_settings,
        }

    def set_btn_score_slider_lists_from_frames(self):
        self.ui_render.empty()
        self.ui_collisions.empty()
        self.score_board.empty()
        for f in self.frames.values():
            if not f.enabled:
                continue
            for c in f.classes.values():
                if c.enabled is False:
                    continue
                self.ui_render.add(c)
                if c.collide_enabled is True:
                    self.ui_collisions.add(c)
                if type(c) is Score:
                    self.score_board.add(c)

    def update(self):
        self.get_collide_classes()
        self.Hover_collision()

        for c in self.collided_classes:
            c.update()
            c.updatecollided()

        for c in self.not_collided_classes:
            c.update()

    def get_collide_classes(self):
        self.collided_classes = []
        self.not_collided_classes = []
        for f in self.frames.values():
            if not f.enabled:
                continue
            for c in f.classes.values():
                if c.rect.collidepoint(pygame.mouse.get_pos()):
                    self.collided_classes.append(c)
                else:
                    self.not_collided_classes.append(c)

    def Hover_collision(self):
        changed = False
        for c in self.collided_classes:
            if c.hovered != True:
                changed = True
            c.hovered = True
            if ui_collision_enabled is False:
                c.collide_enabled = True
        for c in self.not_collided_classes:
            if c.hovered != False:
                changed = True
            c.hovered = False
            if ui_collision_enabled is False:
                c.collide_enabled = False
        if changed:
            self.set_btn_score_slider_lists_from_frames()

    def get_clicked_classes(self):
        # lists for avoiding calling lower functions/loops/race condition
        func_strings_list = []
        func_args_list = []

        for button in self.collided_classes:
            if button.enabled is False or not isinstance(button, Button):
                continue
            # if click_function_string is a single item, convert it to list
            func_strings = button.click_function_string
            if func_strings is None:
                continue
            if isinstance(func_strings, list) is False:
                func_strings = [func_strings]

            func_args = button.click_function_args
            if isinstance(func_args, list) is False:
                func_args = [func_args]

            self.collided_buttons.append(button)
            print(f"----------------------")
            print(f"Clicked: ({button.text}) at Frame ({button.frame.owner})")
            for i, func_string in enumerate(func_strings):
                if not isinstance(func_string, str):
                    continue

                # if (First_level_element)_toggleFrame does exist, toggle the First_level_element Frame
                if self.wrapped_in(func_string, "toggleFrame"):
                    func_string = func_string[1 : func_string.find(")", 1)]
                    func_frame = self.frames.get(func_string)
                    if func_frame is None:
                        print(
                            f"({button.text}): ERROR: Frame: ({func_string}) does not exist"
                        )
                    else:
                        print(f"({button.text}): Toggled Frame: ({func_frame.owner})")
                        if func_args == [] and isinstance(func_args[i], bool):
                            func_frame.toggle_self(func_args[i])
                        else:
                            func_frame.toggle_self()
                        self.set_btn_score_slider_lists_from_frames()
                    continue

                # if (First_level_element)_toggle does exist, toggle the element
                elif self.wrapped_in(func_string, "toggle"):
                    print()
                    func_string = func_string[1 : func_string.find(")", 1)]
                    obj_name, attr = func_string.split(".")
                    cur_val = getattr(getattr(settings, obj_name), attr)
                    setattr(getattr(settings, obj_name), attr, not cur_val)
                    print(
                        f"({button.text}): Toggled: {obj_name}.{attr} to {not cur_val}"
                    )

                else:
                    # else call the function by name
                    if func_args is None:
                        func_strings_list.append(func_string)
                        func_args_list.append(None)
                    else:
                        func_strings_list.append(func_string)
                        func_args_list.append(func_args[i])

        # avoid calling lower functions/loops/race condition
        if len(func_strings_list) != len(func_args_list):
            print(f"{self.owner}: ERROR: Invalid/No Args for {func_strings_list[i]}()")
            return
        for i in range(len(func_strings_list)):
            if func_args_list[i] is None:
                print(f"{self.owner}: Executing Function: {func_strings_list[i]}")
                self.callable_functions[func_strings_list[i]]()
            else:
                print(
                    f"{self.owner}: Executing Function: {func_strings_list[i]}({func_args_list[i].__name__})"
                )
                self.callable_functions[func_strings_list[i]](func_args_list[i])

    def wrapped_in(self, string, wrap_word):
        return string.startswith("(") and string.endswith(f")_{wrap_word}")

    def toggle_frame(self, name, b=None):
        if isinstance(b, bool):
            self.frames[name].toggle_self(b)
        else:
            self.frames[name].toggle_self()
        self.set_btn_score_slider_lists_from_frames()

    def toggle_class(self, f_name, c_name, b=None):
        if isinstance(b, bool):
            self.frames[f_name].classes[c_name].toggle_self(b)
        else:
            self.frames[f_name].classes[c_name].toggle_self()
        self.set_btn_score_slider_lists_from_frames()

    def toggle_spaced(self, f_name, c_name, b=None):
        if isinstance(b, bool):
            self.frames[f_name].classes[c_name].toggle_spaced(b)
        else:
            self.frames[f_name].classes[c_name].toggle_spaced()
        self.frames[f_name].Space()
        self.set_btn_score_slider_lists_from_frames()

    def add_score(self, f_name, c_name, num=1):
        self.frames[f_name].classes[c_name].add_score(num)

    def toggle_ui_collisions(self, b=None):
        global ui_collision_enabled
        ui_collision_enabled = not ui_collision_enabled if b is None else b
        for f in self.frames.values():
            for c in f.classes.values():
                c.hovered = False
                c.collide_enabled = ui_collision_enabled
        self.set_btn_score_slider_lists_from_frames()

    def start_game(self):
        self.game_manager.reset(True, True, True, True, True)
        self.game_started = True
        self.game_manager.paused = False
        self.toggle_class("Toggle_Pause", "Resume", False)
        self.toggle_class("Toggle_Pause", "Pause", True)
        self.toggle_frame("Paused", False)
        self.toggle_frame("Menu", False)
        self.Hover_collision()
        self.toggle_ui_collisions(False)
        if self.frames["Settings_Menu"].enabled:
            self.toggle_frame("Settings_Menu")

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def toggle_paused(self, force=False):
        if force or (
            len(self.collided_buttons) == 1
            and (
                self.collided_buttons[0].text == "Paused"
                or self.collided_buttons[0].text == "Pause"
                or self.collided_buttons[0].text == "Resume"
            )
        ):
            self.paused = not self.paused
            self.toggle_class("Toggle_Pause", "Resume", self.paused)
            self.toggle_class("Toggle_Pause", "Pause", not self.paused)
            self.game_manager.paused = self.paused
            self.toggle_frame("Paused", self.paused)
            if self.game_started is False:
                return
            self.toggle_frame("Menu", self.paused)
            if self.frames["Settings_Menu"].enabled:
                self.toggle_frame("Settings_Menu")

    def screensize_change(self):
        for c in self.frames.values():
            c.screensize_change()

    def set_game_settings(self, setting):
        settings.game_settings = setting()
        settings.game_settings.modified = True

    def draw(self, screen):
        self.collided_buttons = []
        for c in self.ui_render:
            c.draw(screen)


class Frame(GameObject):
    def __init__(self, f_key, frame_value):
        init_size = frame_value["Frame_size"].copy()
        super().__init__(
            f_key,
            pygame.Rect(0, 0, init_size[0], init_size[1]),
            color="white",
            rect_as_percent_of_screen=True,
        )
        self.rect.center = self.get_screen_percent_pixels_pos(frame_value["Center_pos"])
        default_font_Size = frame_value.get("Default_Font_Size")
        self.default_Font_Size = (
            default_font_Size if default_font_Size else ui_settings.font_size
        )
        self.spacing_function = frame_value.get("Spacing_function")
        self.callable_spacing_function = {
            None: self.fallback_spacing,
            "no_spacing": self.no_spacing,
            "fallback_spacing": self.fallback_spacing,
            "space_horizontal": self.space_horizontal,
            "space_vertical": self.space_vertical,
            "space_grid": self.space_grid,
            "edges": self.edges,
        }
        self.classes = {}
        enabled = frame_value.get("Enabled")
        self.enabled = enabled if isinstance(enabled, bool) else True
        self.set_classes(frame_value)

    def set_classes(self, frame_value):
        init_size = frame_value["Frame_size"].copy()
        init_pos = frame_value["Center_pos"].copy()
        init_pos[0] = init_pos[0] - (init_size[0] / 2)
        init_pos[1] = init_pos[1] - (init_size[1] / 2)
        i = -1
        for frame_class_key, frame_class_values in frame_value["Classes"].items():
            c_class = globals().get(frame_class_key)
            if c_class is None:
                continue
            for item_key, item_value in frame_class_values.items():

                size = item_value.get("Size")
                pos = item_value.get("Pos")
                font = item_value.get("Font Size")
                enabled = item_value.get("Enabled")

                if size is None:
                    if c_class == Score:
                        size = ui_settings.score_size
                    elif c_class == Slider:
                        size = ui_settings.slider_size
                    else:
                        size = ui_settings.button_size

                extra = {}
                if c_class == Slider:
                    extra["min_max"] = item_value.get("Min_max")
                    extra["invert"] = item_value.get("Invert")

                self.classes[item_key] = c_class(
                    text=item_key,
                    color=item_value.get("Color"),
                    x=pos[0] if pos is not None else init_pos[0],
                    y=pos[1] if pos is not None else init_pos[1],
                    width=size[0],
                    height=size[1],
                    font_size=font if font is not None else self.default_Font_Size,
                    click_function_string=item_value.get("Click_Functions"),
                    click_function_args=item_value.get("Click_Functions_args"),
                    spaced=pos is None,
                    enabled=enabled if isinstance(enabled, bool) else True,
                    frame=self,
                    setting=item_value.get("Setting"),
                    **extra,
                )

            self.Space()

    def Space(self):
        print(f"{self.owner}: Executing Spacing Function: {self.spacing_function}")
        self.callable_spacing_function[self.spacing_function]()

    def no_spacing(self):
        pass

    def fallback_spacing(self):
        self.space_grid()

    def space_horizontal(self):
        items = [c for c in self.classes.values() if c.spaced]
        n = len(items)
        if n == 0:
            return
        if n == 1:
            items[0].rect.center = self.rect.center
            return
        first_cx = self.rect.left + items[0].rect.width // 2
        last_cx = self.rect.right - items[-1].rect.width // 2
        for i, item in enumerate(items):
            item.rect.centerx = round(first_cx + (last_cx - first_cx) * i / (n - 1))
            item.rect.centery = self.rect.centery

    def space_vertical(self):
        items = [c for c in self.classes.values() if c.spaced]
        n = len(items)
        if n == 0:
            return
        if n == 1:
            items[0].rect.center = self.rect.center
            return
        first_cy = self.rect.top + items[0].rect.height // 2
        last_cy = self.rect.bottom - items[-1].rect.height // 2
        for i, item in enumerate(items):
            item.rect.centerx = self.rect.centerx
            item.rect.centery = round(first_cy + (last_cy - first_cy) * i / (n - 1))

    def space_grid(self):
        items = [c for c in self.classes.values() if c.spaced]
        n = len(items)
        if n == 0:
            return
        if n == 1:
            items[0].rect.center = self.rect.center
            return
        cols = math.ceil(math.sqrt(n))
        rows = math.ceil(n / cols)
        cell_w = self.rect.width / cols
        cell_h = self.rect.height / rows
        for i, item in enumerate(items):
            col = i % cols
            row = i // cols
            cx = round(self.rect.left + cell_w * col + cell_w / 2)
            cy = round(self.rect.top + cell_h * row + cell_h / 2)
            item.rect.center = (cx, cy)
            item.rect.clamp_ip(self.rect)

    def edges(self):
        items = [c for c in self.classes.values() if c.spaced]
        n = len(items)
        if n == 0:
            return
        r = self.rect
        w, h = r.width, r.height
        perimeter = 2 * (w + h)
        step = perimeter / n
        for i, item in enumerate(items):
            dist = step / 2 + i * step
            if dist < w:
                item.rect.centerx = round(r.left + dist)
                item.rect.top = r.top
            elif dist < w + h:
                item.rect.right = r.right
                item.rect.centery = round(r.top + (dist - w))
            elif dist < 2 * w + h:
                item.rect.centerx = round(r.right - (dist - w - h))
                item.rect.bottom = r.bottom
            else:
                item.rect.left = r.left
                item.rect.centery = round(r.bottom - (dist - 2 * w - h))
            item.rect.clamp_ip(r)

    def screensize_change(self):
        for c in self.classes.values():
            c.screensize_change()

    def draw(self, screen):
        for c in self.classes.values():
            c.draw(screen)

    def toggle_self(self, b=None):
        if isinstance(b, bool):
            self.enabled = b
        else:
            self.enabled = not self.enabled


class Button(GameObject):
    def __init__(
        self,
        text,
        color,
        x,
        y,
        width=ui_settings.button_size[0],
        height=ui_settings.button_size[1],
        font_size=ui_settings.font_size,
        click_function_string=None,
        click_function_args=None,
        spaced=True,
        enabled=True,
        frame=None,
        collide_enabled=False,
        hovered=False,
        setting=None,
    ):
        super().__init__(
            Owner.MENU,
            pygame.Rect(x, y, width, height),
            color,
            rect_as_percent_of_screen=True,
        )
        self.frame = frame
        self.enabled = enabled
        self.collide_enabled = collide_enabled
        self.hovered = hovered
        self.spaced = spaced
        self.text = text
        self.text_base = self.text
        self.base_font_size = font_size
        self.font_size = self.scale_1d_round(self.base_font_size)
        self.font = pygame.font.SysFont("dejavuserif", self.font_size)
        self.font_surface = self.font.render(self.text, True, self.color)
        self.text_rect = self.font_surface.get_rect(center=self.rect.center)
        self.click_function_string = click_function_string
        self.click_function_args = click_function_args
        self.setting = setting
        if self.setting:
            self.attr_name, self.attr = self.setting.split(".")
            self.get_attr_value()
            self.last_attr_value = None

    def screensize_change(self):
        self.scale_self()
        self.font_size = self.scale_1d_round(self.base_font_size)

    def update_font(self):
        self.font = pygame.font.SysFont("dejavuserif", self.font_size)

        if self.setting:
            match self.attr_value:
                case float():
                    self.text = self.text_base + ":" + "{:.1f}".format(self.attr_value)
                case _:
                    self.text = self.text_base + ":" + str(self.attr_value)

        self.font_surface = self.font.render(self.text, True, self.color)
        self.text_rect = self.font_surface.get_rect(center=self.rect.center)

    def update(self):
        if self.setting != None:
            self.get_attr_value()

    def updatecollided(self):
        pass

    def draw(self, screen):
        if self.enabled:
            if self.collide_enabled:
                pygame.draw.rect(
                    screen,
                    self.color,
                    self.inflate_percent_longest(-10),
                    settings.screen_settings.line_width,
                    10,
                )
            if self.hovered and (self.collide_enabled and ui_collision_enabled):
                pygame.draw.rect(
                    screen,
                    self.color,
                    self.inflate_percent_longest(-20),
                    settings.screen_settings.line_width,
                    10,
                )
            pygame.draw.rect(
                screen,
                self.color,
                self.rect,
                settings.screen_settings.line_width,
                10,
            )
            self.update_font()
            screen.blit(self.font_surface, self.text_rect)

    def get_attr_value(self):
        self.attr_value = getattr(getattr(settings, self.attr_name), self.attr)

    def set_attr_value(self, value):
        setattr(getattr(settings, self.attr_name), self.attr, value)
        getattr(settings, self.attr_name).modified = True
        self.last_attr_value = value

    def toggle_self(self, b=None):
        if isinstance(b, bool):
            self.enabled = b
        else:
            self.enabled = not self.enabled

    def toggle_spaced(self, b=None):
        if isinstance(b, bool):
            self.spaced = b
        else:
            self.spaced = not self.enabled


class Score(Button):
    def __init__(
        self,
        text,
        color,
        x,
        y,
        width=ui_settings.score_size[0],
        height=ui_settings.score_size[1],
        **kwargs,
    ):
        super().__init__(text, color, x, y, width, height, **kwargs)
        self.score = 0

    def add_score(self, amount):
        self.set_score(self.score + amount)

    def set_score(self, amount):
        self.score = amount
        self.text = str(self.score)


class Slider(Button):
    def __init__(
        self,
        text,
        color,
        x,
        y,
        width=ui_settings.slider_size[0],
        height=ui_settings.slider_size[1],
        min_max=None,
        invert=False,
        **kwargs,
    ):
        super().__init__(text, color, x, y, width, height, **kwargs)
        self.min_max = min_max
        self.invert = invert
        self.is_x = True
        if self.rect.height > self.rect.width:
            self.is_x = False
        ball_radius = min(self.rect.width, self.rect.height)
        self.ball = GameObject(self.owner, pygame.Rect(0, 0, ball_radius, ball_radius))
        self.ball.inflate_percent_ip(50, 50)
        self.ball.rect.center = self.rect.center
        self.value = 0

    def screensize_change(self):
        super().screensize_change()
        self.ball.scale_self()
        self.set_slider_value_rect()
        self.set_slider_value(self.attr_value)
        self.set_ball_rect_pos()

    def set_slider_value_rect(self):
        self.value_rect = pygame.Rect(
            0,
            0,
            self.rect.width - self.ball.rect.width,
            self.rect.height - self.ball.rect.height,
        )
        self.value_rect.center = self.rect.center

    def draw(self, screen):
        super().draw(screen)
        pygame.draw.rect(
            screen,
            "white",
            self.ball.rect,
            settings.screen_settings.line_width,
            100,
        )

    def updatecollided(self):
        self.set_slider_value()
        self.set_ball_rect_pos()

    def update(self):
        super().update()
        if self.last_attr_value != self.attr_value:
            self.set_slider_value(self.attr_value)
            self.set_ball_rect_pos()

    def set_slider_value(self, value=None):
        if self.setting is None:
            return

        if not self.min_max:
            self.min_max = [0, self.attr_value * 2]

        if value:
            self.value = value / self.min_max[1]
        else:
            mouse_pos = pygame.mouse.get_pos()
            if self.is_x:
                self.value = (mouse_pos[0] - self.value_rect.left) / (
                    self.value_rect.right - self.value_rect.left
                )
            else:
                self.value = (mouse_pos[1] - self.value_rect.bottom) / (
                    self.value_rect.top - self.value_rect.bottom
                )
            self.invert_value()
            mapped = self.min_max[0] + self.value * (self.min_max[1] - self.min_max[0])
            mapped = max(self.min_max[0], min(self.min_max[1], mapped))
            self.set_attr_value(mapped)

        self.value = max(0, min(1, self.value))

    def set_ball_rect_pos(self):
        self.invert_value()
        if self.is_x:
            self.ball.rect.centerx = min(
                self.value_rect.right,
                self.value_rect.left + (self.value_rect.width * self.value),
            )
            self.ball.rect.centery = self.value_rect.centery
        else:
            self.ball.rect.centery = min(
                self.value_rect.bottom,
                self.value_rect.top + (self.value_rect.height * self.value),
            )
            self.ball.rect.centerx = self.value_rect.centerx
        self.invert_value()

    def invert_value(self):
        if self.invert:
            self.value = 1 - self.value
