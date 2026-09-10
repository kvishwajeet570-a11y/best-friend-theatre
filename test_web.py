import asyncio
import pygame

async def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 450))
    clock = pygame.time.Clock()

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((20, 20, 40))
        pygame.display.flip()

        clock.tick(60)
        await asyncio.sleep(0)

asyncio.run(main())
