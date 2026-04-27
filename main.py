import pygame
import sys
import settings
from gamefiles.gamemanager import GameManager


def main():
    pygame.init()
    screen = pygame.display.set_mode(
        (
            settings.screen_settings.init_screen_size[0],
            settings.screen_settings.init_screen_size[1],
        ),
        pygame.RESIZABLE,
    )
    settings.screen_settings.set_screen(screen)
    game_manager = GameManager(screen)
    clock = pygame.time.Clock()
    dt = 0
    resize_timer = -1
    while True:
        # quit
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
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

        # resize/rescale everything after 0.1 sec
        if resize_timer > 0:
            resize_timer -= dt

        elif resize_timer <= 0 and resize_timer != -1:
            game_manager.resize_rescale()
            resize_timer = -1
        game_manager.update(dt)
        game_manager.draw()

        pygame.display.flip()
        dt = clock.tick(settings.screen_settings.frame_rate) / 1000


if __name__ == "__main__":
    main()
