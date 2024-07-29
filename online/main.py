
import pygame
from models import Tank, Barrier
from online.client import Client
from utils import generate_map

W, H = 900, 600
pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption('Танки PVP')
barrier_screen = pygame.Surface(screen.get_size())

tanks = [Tank(105, 105, W, H, 0, my=True, auto=False)]
barriers = generate_map(tanks, W, H, Barrier)
missiles = []

client = Client(tanks, barriers, missiles, W, H)


game = True
while game:
    pygame.time.Clock().tick(120)
    screen.blit(barrier_screen, (0, 0))

    barrier_screen.fill((10, 10, 10))
    for barrier in barriers:
        barrier.draw(barrier_screen)

    for missal in missiles:
        missal.move(missiles, tanks, barriers)
        missal.draw(screen)

    for tank in tanks:
        tank.move(tanks, barriers, missiles)
        tank.draw(screen)

    pygame.display.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                [t.attack(missiles) for t in tanks if t.my]
                client.send('attack;')

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            x, y = pygame.mouse.get_pos()
            barrier = [b for b in barriers if x // 30 * 30 == b.x and y // 30 * 30 == b.y]
            if barrier:
                barriers.remove(barrier[0])
            else:
                barriers.append(Barrier(x // 30 * 30, y // 30 * 30, 'brick'))

        if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            x, y = pygame.mouse.get_pos()
            tanks.append(Tank(x // 30 * 30 + 15, y // 30 * 30 + 15, W, H, team=1, auto=True))
