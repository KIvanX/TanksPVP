
import socket
import threading
import time

from models import Barrier, Tank
from utils import get_free_position


class Client:
    def __init__(self, _tanks, _barriers, _missiles, _w, _h):
        self.play = False
        self.barriers = _barriers
        self.tanks = _tanks
        self.missiles = _missiles
        self.w, self.h = _w, _h
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(('0.0.0.0', 8008))
        threading.Thread(target=self.listener, daemon=True).start()

    def send(self, s: str):
        self.socket.send(s.encode())

    def listener(self):
        while True:
            data = self.socket.recv(1024).decode()
            if data.startswith('init'):
                self.play = True
                if ' ' not in data:
                    a = [[0] * (self.w // 30) for _ in range(self.h // 30)]
                    for _barrier in self.barriers:
                        a[_barrier.y // 30][_barrier.x // 30] = 1 if _barrier.type == 'brick' else 2
                    self.send('init ' + ''.join([''.join([str(e) for e in line]) for line in a]) + ';')
                    self.tanks.append(Tank(0, 0, self.w, self.h, 1, auto=False))
                else:
                    self.barriers.clear()
                    data = data[:-1].split()[-1]
                    for i in range(len(data)):
                        if data[i] != '0':
                            x, y = i % (self.w // 30) * 30, i // (self.w // 30) * 30
                            self.barriers.append(Barrier(x, y, 'brick' if data[i] == '1' else 'metal'))

                    _x, _y = get_free_position(self.tanks, self.barriers, self.w, self.h)
                    self.tanks[0].x = _x
                    self.tanks[0].y = _y
                    self.tanks.append(Tank(0, 0, self.w, self.h, 1, auto=False))
                threading.Thread(target=self.sender, daemon=True).start()

            if data.startswith('position') and data[-1] == ';':
                x, y, look = data[:-1].split()[1:]
                tank = [t for t in self.tanks if not t.my and not t.auto][0]
                tank.to_x, tank.to_y, tank.look = int(x), int(y), int(look)

            if data.startswith('attack'):
                tank = [t for t in self.tanks if not t.my and not t.auto][0]
                tank.attack(self.missiles)

    def sender(self):
        while True:
            tank = [t for t in self.tanks if t.my]
            if not tank:
                return 0
            self.send(f'position {tank[0].x} {tank[0].y} {tank[0].look};')
            time.sleep(0.1)
