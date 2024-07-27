import random
import pygame
from models import Tank, Barrier

W, H = 900, 600
pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption('Танки Оффлайн PVP')

tanks = [Tank(105, 105, W, H, 0), Tank(W - 75, H - 75, W, H, 1)]
missiles = []

barriers, barrier_screen = [], pygame.Surface(screen.get_size())
while len(barriers) < random.randint(200, 500):
    x = random.randint(0, W // 30 - 1) * 30
    y = random.randint(0, H // 30 - 1) * 30
    flag = True
    for tank in tanks:
        if tank.x - 45 < x < tank.x + 15 and tank.y - 45 < y < tank.y + 45:
            flag = False
    nei = 0
    for barrier in barriers:
        if barrier.x == x and barrier.y == y:
            flag = False
        if (barrier.x - x)**2 + (barrier.y - y)**2 < 40**2:
            nei += 1
    if flag and random.random() < 0.001 + 0.1 * nei:
        barriers.append(Barrier(x, y, 'brick' if random.random() < 0.8 else 'metal'))
prev_len = 0

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
            if event.key == pygame.K_RETURN:
                tanks[0].attack(missiles)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            tanks[0].attack(missiles)

        # if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
        #     x, y = pygame.mouse.get_pos()
        #     barrier = [b for b in barriers if x // 30 * 30 == b.x and y // 30 * 30 == b.y]
        #     if barrier:
        #         barriers.remove(barrier[0])
        #     else:
        #         barriers.append(Barrier(x // 30 * 30, y // 30 * 30, 'brick'))

        # if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
        #     x, y = pygame.mouse.get_pos()
        #     tanks.append(Tank(x // 30 * 30 + 15, y // 30 * 30 + 15))
