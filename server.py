import json
import random
import socket
import threading
import time
import pygame
from models import Barrier, Tank


def create_world():
    global barriers, missiles, tanks

    missiles, barriers, tanks = [], [], []
    while len(barriers) < random.randint(200, 500):
        x = random.randint(0, W // 30 - 1) * 30
        y = random.randint(0, H // 30 - 1) * 30
        flag = True
        nei = 0
        for barrier in barriers:
            if barrier.x == x and barrier.y == y:
                flag = False
            if (barrier.x - x) ** 2 + (barrier.y - y) ** 2 < 40 ** 2:
                nei += 1
        if flag and random.random() < 0.001 + 0.1 * nei:
            barriers.append(Barrier(x, y, 'brick' if random.random() < 0.8 else 'metal', random.randint(0, 10**12)))


def sending():
    global barriers

    while True:
        for player in list(players.values()).copy():
            _message = {'type': 'update',
                        'data': {'tanks': [{'x': t.x, 'y': t.y, 'look': t.look, 'p_id': t.p_id,
                                            'hp': t.hp, 'stars': t.stars} for t in tanks.copy()],
                                 'barriers': [{'x': b.x, 'y': b.y, 'type': b.type, 'id': b.id,
                                               'hp': b.hp} for b in barriers if b.updated],
                                 'missiles': [{'x': m.x, 'y': m.y, 'way': m.way, 'id': m.id} for m in missiles]}}
            _message['data']['barriers'] = _message['data']['barriers'][:10]
            server_socket.sendto(json.dumps(_message).encode(), player['address'])
        k = 0
        for b in barriers:
            if b.updated and k < 10:
                k, b.updated = k + 1, 0 if b.updated < 2 else b.updated - 1
        time.sleep(0.1)


def listening():
    global players, tanks
    while True:
        data, client_address = server_socket.recvfrom(256)
        message = json.loads(data.decode())

        players = {p_id: p for p_id, p in players.items() if time.time() - p['last_update'] < 3}
        tanks = [t for t in tanks if t.p_id in players or t.auto]

        if message['type'] == 'hello':
            if not players:
                create_world()

            for b in barriers:
                b.updated = 10

            p_id = random.randint(0, 10 ** 12)
            free_cells = {(i % 30, i // 30) for i in range(600) if i % 30 not in [0, 30] and i // 30 not in [0, 20]}
            for _barrier in barriers:
                free_cells.remove((_barrier.x // 30, _barrier.y // 30))
            x, y = random.choice(list(free_cells))
            tanks.append(Tank(x * 30 + 15, y * 30 + 15, W, H, p_id))
            players[p_id] = {'address': client_address, 'tank': tanks[-1], 'last_update': time.time()}
            server_socket.sendto(json.dumps({'type': 'hello', 'data': p_id}).encode(), client_address)
        elif message['type'] == 'update':
            if message.get('p_id') not in players:
                continue
            players[message['p_id']]['last_update'] = time.time()
            players[message['p_id']]['tank'].dx = message['data']['dx']
            players[message['p_id']]['tank'].dy = message['data']['dy']
            if message['data'].get('attack'):
                players[message['p_id']]['tank'].attack(missiles)
        elif message['type'] == 'goodbye':
            players[message['p_id']]['last_update'] = time.time() - 5
        elif message['type'] == 'create':
            x, y = message['data']['x'], message['data']['y']
            if message['data']['type'] == 'tank':
                _barrier = [b for b in barriers if b.x == x - 15 and b.y == y - 15]
                _tank = [t for t in tanks if (t.x - x)**2 + (t.y - y)**2 < 1000]
                if _barrier:
                    _barrier[0].hp = 0
                    _barrier[0].updated = 10
                if _tank:
                    tanks.remove(_tank[0])
                else:
                    tanks.append(Tank(x, y, W, H, random.randint(0, 10**12), auto=True))
            else:
                _barrier = [b for b in barriers if b.x == x and b.y == y]
                if not _barrier:
                    barriers.append(Barrier(message['data']['x'], message['data']['y'], 'brick',
                                            random.randint(0, 10 ** 12)))
                else:
                    if _barrier[0].type == 'brick':
                        _barrier[0].type = 'metal'
                        _barrier[0].hp = 300
                    else:
                        _barrier[0].hp = 0
                    _barrier[0].updated = 10


pygame.init()
W, H = 900, 600
tanks = []
barriers = []
missiles = []
players = {}

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('localhost', 8008))
threading.Thread(target=sending, daemon=True).start()
threading.Thread(target=listening, daemon=True).start()
print("Сервер запущен...")

while True:
    pygame.time.Clock().tick(80)

    for missal in missiles:
        missal.move(missiles, tanks, barriers)

    for tank in tanks:
        tank.move(tanks, barriers, missiles)
