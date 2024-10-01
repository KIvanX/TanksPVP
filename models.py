import random
import time
import pygame

from utils import on_map, get_free_position

delta = [(0, -1), (-1, 0), (0, 1), (1, 0)]
ways = {pygame.K_UP: (0, -1, 0), pygame.K_DOWN: (0, 1, 2), pygame.K_LEFT: (-1, 0, 1), pygame.K_RIGHT: (1, 0, 3),
        pygame.K_w: (0, -1, 0), pygame.K_s: (0, 1, 2), pygame.K_a: (-1, 0, 1), pygame.K_d: (1, 0, 3)}
bricks_surface = pygame.transform.scale(pygame.image.load('images/bricks.png'), (30, 30))
metal_surface = pygame.transform.scale(pygame.image.load('images/metal.png'), (30, 30))
crack_surface = pygame.transform.scale(pygame.image.load('images/crack.png'), (30, 30))
main_tank_surface = pygame.transform.scale(pygame.image.load('images/main_tank.png'), (30, 30))
enemy_tank_surface = pygame.transform.scale(pygame.image.load('images/enemy_tank.png'), (30, 30))
star_surface = pygame.transform.scale(pygame.image.load('images/star.png'), (10, 10))


class Tank:
    def __init__(self, x, y, w, h, p_id, my=False, auto=False):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.look = 0
        self.my = my
        self.auto = auto
        self.p_id = p_id
        self.last_attack, self.last_think = 0, 0
        self.stars = 0
        self.hp = 10
        self.p = (-1, 0)
        self.font = pygame.font.Font(pygame.font.match_font('arial'), 18)
        self.dx, self.dy = 0, 0
        self.to_x, self.to_y = x, y

    def move(self, _tanks, _barriers, _missiles):
        _x, _y = 0, 0
        if self.my:
            keys = pygame.key.get_pressed()
            for _key in ways:
                if keys[_key]:
                    _x = self.x + ways[_key][0]
                    _y = self.y + ways[_key][1]
                    self.look = ways[_key][2]
        elif self.auto:
            return self.think(_tanks, _barriers, _missiles)
        else:
            _x = self.x + self.dx
            _y = self.y + self.dy
            if self.dx or self.dy:
                self.look = (3 if self.dx > 0 else 1) if self.dx else (2 if self.dy > 0 else 0)

        _flag = True
        for _tank in _tanks:
            if _tank != self and _tank.x - 15 <= _x <= _tank.x + 15 and _tank.y - 15 <= _y <= _tank.y + 15:
                _flag = False

        for _barrier in _barriers:
            if _barrier.x - 10 <= _x <= _barrier.x + 40 and _barrier.y - 10 <= _y <= _barrier.y + 40:
                _flag = False

            if not (15 < _x < self.w - 15 and 15 < _y < self.h - 15):
                _flag = False

        if _flag:
            self.x, self.y = _x, _y
            return 0

    def move_to(self):
        ln = ((self.to_x - self.x) ** 2 + (self.to_y - self.y) ** 2) ** 0.5
        if 3 < ln < 100:
            self.x += (self.to_x - self.x) // 3
            self.y += (self.to_y - self.y) // 3
        elif not 3 < ln < 100:
            self.x, self.y = self.to_x, self.to_y

    def draw(self, _screen):
        raw_surface = main_tank_surface if self.my else enemy_tank_surface
        surface = pygame.transform.rotate(raw_surface, self.look * 90)
        rect = surface.get_rect(center=(0, 0))
        _screen.blit(surface, (self.x + rect.x, self.y + rect.y))

        text_surface = self.font.render(str(self.hp), True, (250, 250, 250))
        _screen.blit(text_surface, (self.x - len(str(self.hp)) * 5, self.y - 30))

        if not self.auto:
            for i in range(self.stars):
                _screen.blit(star_surface, (self.x - self.stars * 5 + i * 10, self.y - 45))
        else:
            text_surface = self.font.render('Bot', True, (250, 250, 250))
            _screen.blit(text_surface, (self.x - 10, self.y - 45))

    def attack(self, _missiles, miss=0.0):
        if random.random() < miss:
            self.last_attack = time.time()

        if time.time() - self.last_attack < 1:
            return False

        x, y = self.x + delta[self.look][0] * 15, self.y + delta[self.look][1] * 15
        _missiles.append(Missile(x, y, self.w, self.h, self.look, random.randint(10**6, 10**12), 5, 3, self))
        self.last_attack = time.time()
        return True

    def damage(self, _damage, _tanks, _barriers):
        self.hp -= _damage

        if self.hp <= 0:
            _tanks.remove(self)
            if self.auto and len(_tanks) == 1:
                for _ in range(_tanks[0].stars // 3 + 1):
                    _x, _y = get_free_position(_tanks, _barriers, self.w, self.h)
                    _tanks.append(Tank(_x, _y, self.w, self.h, random.randint(10**6, 10**12)))
            return True
        return False

    def think(self, _tanks, _barriers, _missiles):
        enemy = [_tank for _tank in _tanks if not _tank.auto]
        if not enemy:
            return 0

        if enemy[0].x - 15 < self.x < enemy[0].x + 15 and enemy[0].y - 15 < self.y < enemy[0].y + 15:
            enemy[0].x, enemy[0].y = enemy[0].x + self.p[1], enemy[0].y + self.p[0]

        if not ((self.y - 15) % 30 == (self.x - 15) % 30 == 0):
            self.x, self.y = self.x + self.p[1], self.y + self.p[0]
            return 0

        if time.time() - self.last_think < 0.1:
            return 0
        self.last_think = time.time()

        n, m = self.h // 30, self.w // 30
        a, b = [[1000] * m for _ in range(n)], [[1] * m for _ in range(n)]

        i0, j0, i1, j1 = self.y // 30, self.x // 30, enemy[0].y // 30, enemy[0].x // 30
        a[i1][j1] = 0

        for _barrier in _barriers:
            b[_barrier.y // 30][_barrier.x // 30] = 10 if _barrier.type == 'brick' else 1000

        for _missile in _missiles:
            for i in range(5):
                dx, dy = delta[_missile.way]
                if on_map(_missile.y // 30 + dy * i, _missile.x // 30 + dx * i, n, m):
                    b[_missile.y // 30 + dy * i][_missile.x // 30 + dx * i] = 1000

        for i in range(30):
            i2, j2 = i0 + self.p[0] * i, j0 + self.p[1] * i
            if on_map(i2, j2, n, m) and b[i2][j2] != 1:
                break

            if on_map(i2, j2, n, m) and i2 == i1 and j2 == j1:
                self.attack(_missiles, miss=0.35)
                return 0

        for k in range(5):
            for i in range(*((0, n, 1) if random.random() < 0.5 else (n - 1, -1, -1))):
                for j in range(*((0, m, 1) if random.random() < 0.5 else (m - 1, -1, -1))):
                    ds = [(di, dj) for di, dj in delta if on_map(i + di, j + dj, n, m)]

                    di, dj = min(ds, key=lambda d: a[i + d[0]][j + d[1]] + b[i][j])
                    a[i][j] = min(a[i][j], a[i + di][j + dj] + b[i][j])

        ds = [(di, dj) for di, dj in delta if on_map(i0 + di, j0 + dj, n, m)]
        di, dj = min(ds, key=lambda d: a[i0 + d[0]][j0 + d[1]])
        is_leave = self.p in ds and a[i0 + self.p[0]][j0 + self.p[1]] == a[i0 + di][j0 + dj] and random.random() < 0.7
        di, dj = self.p if is_leave else (di, dj)
        self.look = delta.index((dj, di))

        if b[i0 + di][j0 + dj] != 1 or (i0 + di, j0 + dj) == (i1, j1):
            self.attack(_missiles)
            return 0
        self.x, self.y = self.x + dj, self.y + di
        self.p = (di, dj)


class Barrier:
    def __init__(self, x, y, _type, b_id):
        self.x = x
        self.y = y
        self.id = b_id
        self.type = _type
        self.updated = 10
        self.hp = 3 if _type == 'brick' else 300

    def draw(self, _screen):
        _screen.blit(bricks_surface if self.type == 'brick' else metal_surface, (self.x, self.y))
        if self.hp < 3:
            _screen.blit(crack_surface, (self.x, self.y))

        if self.hp < 2:
            _crack_surface = pygame.transform.rotate(crack_surface, 90)
            _screen.blit(_crack_surface, (self.x, self.y))

    def damage(self, _barriers):
        self.updated = 10
        self.hp -= 1


class Missile:
    def __init__(self, x, y, w, h, way, m_id, speed, damage, parent):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.way = way
        self.id = m_id
        self.speed = speed
        self.damage = damage
        self.parent = parent
        self.to_x, self.to_y = x, y

    def draw(self, _screen):
        pygame.draw.rect(_screen, (255, 255, 255), (self.x, self.y, 2, 2))

    def move(self, _missiles: list, _tanks: list[Tank], _barriers: list[Barrier]):
        self.x += delta[self.way][0] * self.speed
        self.y += delta[self.way][1] * self.speed

        for _tank in _tanks:
            if _tank.x - 15 <= self.x <= _tank.x + 15 and _tank.y - 15 <= self.y <= _tank.y + 15:
                self.parent.stars = min(6, self.parent.stars + int(_tank.damage(self.damage, _tanks, _barriers)))
                _missiles.remove(self)
                return 0

        for _barrier in _barriers:
            if _barrier.x <= self.x <= _barrier.x + 30 and _barrier.y <= self.y <= _barrier.y + 30:
                _barrier.damage(_barriers)
                _missiles.remove(self)
                return 0

        if not on_map(self.x, self.y, self.w, self.h):
            _missiles.remove(self)

    def move_to(self):
        ln = ((self.to_x - self.x) ** 2 + (self.to_y - self.y) ** 2) ** 0.5
        if self.to_x and 1 < ln < 5000:
            self.x += (self.to_x - self.x) // 5
            self.y += (self.to_y - self.y) // 5
        elif self.to_x and not 1 < ln < 5000:
            self.x, self.y = self.to_x, self.to_y
