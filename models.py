import random
import time
import pygame

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
    def __init__(self, x, y, w, h, team):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.look = 0
        self.team = team
        self.last_attack, self.last_think = 0, 0
        self.stars = 0
        self.hp = 10
        self.p = (-1, 0)
        self.font = pygame.font.Font(pygame.font.match_font('arial'), 18)
        self.surface = main_tank_surface if team == 0 else enemy_tank_surface

    def move(self, _tanks, _barriers, _missiles):
        if self.team == 0:
            keys = pygame.key.get_pressed()
            for _key in ways:
                if keys[_key]:
                    _x = self.x + ways[_key][0]
                    _y = self.y + ways[_key][1]
                    self.look = ways[_key][2]

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
        else:
            self.think(_tanks, _barriers, _missiles)

    def draw(self, _screen):
        surface = pygame.transform.rotate(self.surface, self.look * 90)
        rect = surface.get_rect(center=(0, 0))
        _screen.blit(surface, (self.x + rect.x, self.y + rect.y))

        text_surface = self.font.render(str(self.hp), True, (250, 250, 250))
        _screen.blit(text_surface, (self.x - len(str(self.hp)) * 5, self.y - 30))

        if self.team == 0:
            for i in range(self.stars):
                _screen.blit(star_surface, (self.x - self.stars * 5 + i * 10, self.y - 45))

    def attack(self, _missiles):
        if time.time() - self.last_attack < 1:
            return 0

        x, y = self.x + delta[self.look][0] * 15, self.y + delta[self.look][1] * 15
        _missiles.append(Missile(x, y, self.w, self.h, self.look, 2, 3, self))
        self.last_attack = time.time()

    def damage(self, _damage, _tanks, _barriers):
        self.hp -= _damage

        if self.hp <= 0:
            _tanks.remove(self)
            if self.team != 0 and len(_tanks) == 1:
                for _ in range(_tanks[0].stars + 1):
                    add_new_enemy(_tanks, _barriers, self.team, self.w, self.h)
            return True
        return False

    def think(self, _tanks, _barriers, _missiles):
        enemy = [_tank for _tank in _tanks if _tank.team != self.team]
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
                self.attack(_missiles)
                return 0

        for k in range(5):
            for i in range(*((0, n, 1) if random.random() < 0.5 else (n - 1, -1, -1))):
                for j in range(*((0, m, 1) if random.random() < 0.5 else (m - 1, -1, -1))):
                    ds = [(di, dj) for di, dj in delta if on_map(i + di, j + dj, n, m)]

                    di, dj = min(ds, key=lambda d: a[i + d[0]][j + d[1]] + b[i][j])
                    a[i][j] = min(a[i][j], a[i + di][j + dj] + b[i][j])

        ds = [(di, dj) for di, dj in delta if on_map(i0 + di, j0 + dj, n, m)]
        di, dj = min(ds, key=lambda d: a[i0 + d[0]][j0 + d[1]])
        di, dj = self.p if self.p in ds and a[i0 + self.p[0]][j0 + self.p[1]] == a[i0 + di][j0 + dj] else (di, dj)
        self.look = delta.index((dj, di))

        if b[i0 + di][j0 + dj] != 1 or (i0 + di, j0 + dj) == (i1, j1):
            self.attack(_missiles)
            return 0
        self.x, self.y = self.x + dj, self.y + di
        self.p = (di, dj)


class Barrier:
    def __init__(self, _x, _y, _type):
        self.x = _x
        self.y = _y
        self.type = _type
        self.hp = 3 if _type == 'brick' else 300
        self.surface = bricks_surface if _type == 'brick' else metal_surface

    def draw(self, _screen):
        _screen.blit(self.surface, (self.x, self.y))
        if self.hp < 3:
            _screen.blit(crack_surface, (self.x, self.y))

        if self.hp < 2:
            _crack_surface = pygame.transform.rotate(crack_surface, 90)
            _screen.blit(_crack_surface, (self.x, self.y))

    def damage(self, _barriers):
        self.hp -= 1
        if self.hp <= 0:
            _barriers.remove(self)


class Missile:
    def __init__(self, x, y, w, h, way, speed, damage, parent: Tank):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.way = way
        self.speed = speed
        self.damage = damage
        self.parent = parent

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


def on_map(_x, _y, n, m):
    return 0 <= _x < n and 0 <= _y < m


def add_new_enemy(_tanks, _barriers, team, _w, _h):
    flag = False
    while not flag:
        flag = True
        _x, _y = random.randint(0, _w // 30 - 1) * 30, random.randint(0, _h // 30 - 1) * 30
        for _barrier in _barriers:
            if _barrier.x <= _x <= _barrier.x + 30 and _barrier.y <= _y <= _barrier.y + 30:
                flag = False

        if abs(_tanks[0].x - _x) + abs(_tanks[0].y - _y) < 300:
            flag = False

        if flag:
            _tanks.append(Tank(_x + 15, _y + 15, _w, _h, team))
