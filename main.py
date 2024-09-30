
import pygame
from client import Client

W, H = 900, 600
pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption('Танки PVP')
barrier_screen = pygame.Surface(screen.get_size())

client = Client(W, H)


game = True
while game:
    pygame.time.Clock().tick(80)
    screen.blit(barrier_screen, (0, 0))

    barrier_screen.fill((10, 10, 10))
    for barrier in client.barriers:
        barrier.draw(barrier_screen)

    for missal in client.missiles:
        missal.move_to()
        missal.draw(screen)

    for tank in client.tanks:
        tank.move_to()
        tank.draw(screen)

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                client.attack_request = True

        if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            x, y = pygame.mouse.get_pos()
            client.add_tank(x // 30 * 30 + 15, y // 30 * 30 + 15)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            x, y = pygame.mouse.get_pos()
            client.add_barrier(x // 30 * 30, y // 30 * 30)
