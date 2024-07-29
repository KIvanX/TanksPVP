import random


def on_map(_x, _y, n, m):
    return 0 <= _x < n and 0 <= _y < m


def get_free_position(_tanks, _barriers, _w, _h):
    flag = False
    while not flag:
        flag = True
        _x, _y = random.randint(0, _w // 30 - 1) * 30, random.randint(0, _h // 30 - 1) * 30
        for _barrier in _barriers:
            if _barrier.x <= _x <= _barrier.x + 30 and _barrier.y <= _y <= _barrier.y + 30:
                flag = False

        for _t in _tanks:
            if abs(_t.x - _x) + abs(_t.y - _y) < 200:
                flag = False

        if flag:
            return _x + 15, _y + 15


def generate_map(tanks, w, h, Barrier):
    barriers = []
    while len(barriers) < random.randint(200, 500):
        x = random.randint(0, w // 30 - 1) * 30
        y = random.randint(0, h // 30 - 1) * 30
        flag = True
        for tank in tanks:
            if tank.x - 45 < x < tank.x + 15 and tank.y - 45 < y < tank.y + 45:
                flag = False
        nei = 0
        for barrier in barriers:
            if barrier.x == x and barrier.y == y:
                flag = False
            if (barrier.x - x) ** 2 + (barrier.y - y) ** 2 < 40 ** 2:
                nei += 1
        if flag and random.random() < 0.001 + 0.1 * nei:
            barriers.append(Barrier(x, y, 'brick' if random.random() < 0.8 else 'metal'))

    return barriers
