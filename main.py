from __future__ import annotations

import pygame

from scenes.birthday_slides import BirthdaySlides


def main():
    pygame.init()

    try:
        info = pygame.display.Info()
        width = info.current_w if info.current_w >= 900 else 1280
        height = info.current_h if info.current_h >= 600 else 720

        screen = pygame.display.set_mode(
            (width, height),
            pygame.RESIZABLE,
        )

        pygame.display.set_caption("Best Friend Theatre")

        clock = pygame.time.Clock()

        scene = BirthdaySlides(screen)

        running = True

        while running:
            dt = clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    elif event.key == pygame.K_RIGHT:
                        try:
                            scene.next_slide()
                        except AttributeError:
                            try:
                                scene.next()
                            except AttributeError:
                                pass

                    elif event.key == pygame.K_LEFT:
                        try:
                            scene.previous_slide()
                        except AttributeError:
                            try:
                                scene.prev()
                            except AttributeError:
                                pass

                elif event.type == pygame.VIDEORESIZE:
                    try:
                        scene.width = event.w
                        scene.height = event.h
                    except Exception:
                        pass

            try:
                scene.update(dt)
            except TypeError:
                try:
                    scene.update()
                except AttributeError:
                    pass
            except AttributeError:
                pass

            try:
                scene.draw_current_slide()
            except AttributeError:
                try:
                    scene.draw()
                except AttributeError:
                    pass

            pygame.display.flip()

    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
