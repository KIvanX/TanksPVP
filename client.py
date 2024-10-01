import json
import socket
import threading
import time
import pygame
from models import Barrier, Tank, Missile, ways


class Client:
    def __init__(self, _w, _h):
        self.play = False
        self.barriers = []
        self.tanks = []
        self.missiles = []
        self.w, self.h = _w, _h
        self.p_id = None
        self.attack_request = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        threading.Thread(target=self.listener, daemon=True).start()
        self.send({'type': 'hello'})

    def send(self, s: dict):
        server, local = '62.217.177.130', 'localhost'
        self.socket.sendto(json.dumps(s).encode(), (server, 8008))

    def listener(self):
        time.sleep(0.03)
        while True:
            data, address = self.socket.recvfrom(4096)
            message = json.loads(data.decode())
            if message['type'] == 'update':
                ids = {t['p_id'] for t in message['data']['tanks']}
                self.tanks = [t for t in self.tanks if t.p_id in ids]
                for t in message['data']['tanks']:
                    tank = [tank for tank in self.tanks if tank.p_id == t['p_id']]
                    if not tank:
                        self.tanks.append(Tank(t['x'], t['y'], self.w, self.h, t['p_id'],
                                               my=t['p_id'] == self.p_id, auto=t['auto']))
                        self.tanks[-1].look = t['look']
                    else:
                        tank[0].to_x = t['x']
                        tank[0].to_y = t['y']
                        tank[0].look = t['look']
                        tank[0].hp = t['hp']
                        tank[0].stars = t['stars']

                for b in message['data']['barriers']:
                    barrier = [barrier for barrier in self.barriers if barrier.id == b['id']]
                    if not barrier:
                        if b['hp'] > 0:
                            self.barriers.append(Barrier(b['x'], b['y'], b['type'], b['id']))
                            self.barriers[-1].hp = b['hp']
                    else:
                        barrier[0].hp = b['hp']
                        barrier[0].type = b['type']
                        if b['hp'] <= 0:
                            self.barriers.remove(barrier[0])

                ids = {m['id'] for m in message['data']['missiles']}
                self.missiles = [m for m in self.missiles if m.id in ids]
                for m in message['data']['missiles']:
                    missil = [missil for missil in self.missiles if missil.id == m['id']]
                    if not missil:
                        self.missiles.append(Missile(m['x'], m['y'], self.w, self.h, m['way'], m['id'], 0, 0, None))
                    else:
                        missil[0].to_x = m['x']
                        missil[0].to_y = m['y']

            if message['type'] == 'hello':
                self.p_id = message['data']
                threading.Thread(target=self.sender, daemon=False).start()

    def sender(self):
        while True:
            time.sleep(0.03)

            if not threading.main_thread().is_alive():
                self.send({'type': 'goodbye', 'p_id': self.p_id})
                return False

            x, y = 0, 0
            keys = pygame.key.get_pressed()
            for _key in ways:
                if keys[_key]:
                    x = ways[_key][0]
                    y = ways[_key][1]
            self.send({'type': 'update', 'p_id': self.p_id,
                       'data': {'dx': x, 'dy': y, 'attack': self.attack_request}})
            self.attack_request = False

    def add_tank(self, x, y):
        self.send({'type': 'create', 'p_id': self.p_id,
                   'data': {'x': x, 'y': y, 'type': 'tank'}})

    def add_barrier(self, x, y):
        self.send({'type': 'create', 'p_id': self.p_id,
                   'data': {'x': x, 'y': y, 'type': 'barrier'}})
