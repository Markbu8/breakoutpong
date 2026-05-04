import asyncio
import sys
import pygame

IS_WEB = sys.platform == "emscripten"
if IS_WEB:
    import platform  # pygbag's; provides .window

import settings as settings
from gamefiles.gamemanager import GameManager

flags = 0 if IS_WEB else pygame.RESIZABLE


def get_browser_size():
    return int(platform.window.innerWidth), int(platform.window.innerHeight)


async def main():
    pygame.init()

    if IS_WEB:
        w, h = get_browser_size()
    else:
        w, h = (
            settings.screen_settings.init_screen_size[0],
            settings.screen_settings.init_screen_size[1],
        )

    screen = pygame.display.set_mode((w, h), flags)
    settings.screen_settings.set_screen(screen)
    game_manager = GameManager(screen)
    clock = pygame.time.Clock()
    dt = 0
    resize_timer = -1
    last_size = (w, h)

    while True:
        # detect browser window resize on web
        if IS_WEB:
            new_size = get_browser_size()
            if new_size != last_size:
                screen = pygame.display.set_mode(new_size, flags)
                settings.screen_settings.set_screen(screen)
                last_size = new_size
                resize_timer = 0.25

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.VIDEORESIZE:
                resize_timer = 0.25
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game_manager.toggle_paused()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                # reset
                settings.spawn_settings = settings.SpawnSettings()
                settings.game_settings = settings.UIGameSettings()
                game_manager = GameManager(screen)
                resize_timer = 0.0001
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game_manager.mouse_down()

        # resize/rescale everything after the timer expires
        if resize_timer > 0:
            resize_timer -= dt
        elif resize_timer <= 0 and resize_timer != -1:
            game_manager.resize_rescale()
            resize_timer = -1

        game_manager.update(dt)
        game_manager.draw()

        pygame.display.flip()
        dt = clock.tick(settings.screen_settings.frame_rate) / 1000
        await asyncio.sleep(0)


asyncio.run(main())
