import time
import random
import math
from collections import defaultdict
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text
from luma.core.legacy.font import proportional, CP437_FONT, LCD_FONT
from luma.led_matrix.device import max7219


def matrix(device):
    wrd_rgb = [
        (154, 173, 154),
        (0, 255, 0),
        (0, 235, 0),
        (0, 220, 0),
        (0, 185, 0),
        (0, 165, 0),
        (0, 128, 0),
        (0, 0, 0),
        (154, 173, 154),
        (0, 145, 0),
        (0, 125, 0),
        (0, 100, 0),
        (0, 80, 0),
        (0, 60, 0),
        (0, 40, 0),
        (0, 0, 0)
    ]

    clock = 0
    blue_pilled_population = []
    max_population = device.width * 20

    def increase_population():
        blue_pilled_population.append([random.randint(0, device.width),
                                       0,
                                       random.gauss(1.2, 0.8)])

    while True:
        clock += 1
        with canvas(device, dither=True) as draw:
            for person in blue_pilled_population:
                x, y, speed = person
                for rgb in wrd_rgb:
                    if 0 <= y < device.height:
                        draw.point((x, y), fill=rgb)
                    y -= 1
                person[1] += speed
            time.sleep(0.2)

        if clock % 5 == 0 or clock % 3 == 0:
            increase_population()

        while len(blue_pilled_population) > max_population:
            blue_pilled_population.pop(0)

def flying_points(device):
    points = [
        ([random.randint(0, device.width - 1),
          random.randint(0, device.height - 1)],
         (random.gauss(0, 1), random.gauss(0, 1))) for _ in range(20)]

    while True:
        with canvas(device) as draw:
            for point in points:
                pos, speed = point
                draw.point(pos, fill="white")
                pos[0] = (pos[0] + speed[0]) % device.width
                pos[1] = (pos[1] + speed[0]) % device.height
        time.sleep(0.1)

def bouncing_contrast(device):
    c = 1
    dc = 1
    while True:
        device.contrast(c)
        with canvas(device) as draw:
            tw = len(str(c)) * 8
            text(draw, (c % device.width, 0), str(c), fill="white", font=CP437_FONT)
        c += dc
        if c > 99:
            dc = -1
        elif c < 2:
            dc = 1
        time.sleep(0.08)

def snowfall(device):
    c = 100
    device.contrast(c)
    points = []
    def points_in_row(y):
        return list(filter(lambda p: p[1] == y, points))

    def new_point():
        valids = [y for y in range(device.height) \
                  if len(points_in_row(y)) < device.width * 7 / 8]
        if not valids:
            return

        points.append([0, random.choice(valids)])

    new_point()
    something_moved = True
    while something_moved:
        something_moved = False
        with canvas(device) as draw:
            for point in points:
                draw.point(point, fill="white") 
                in_row = points_in_row(point[1])
                if point[0] + 1 not in [x for (x, _) in in_row] \
                   and point[0] + 1 < device.width:
                    point[0] += 1
                    something_moved = True

            time.sleep(0.03)
            if random.random() > 0.002:
                new_point()

    while c > 0:
        device.contrast(c)
        c -= 1
        time.sleep(0.015)

def double_sine(device):
    phase = 1
    dphase = 0.6
    maxphase = 15
    minphase = -15
    c = 0
    while True:
        with canvas(device) as draw:
            for x in range(device.width):
                y = math.sin(c / 3 + phase * x / device.width) * device.height / 2 + device.height / 2
                draw.point((x, y), fill="white")
                draw.point((x, device.height - y), fill="white")
        if phase >= maxphase:
            dphase = -1
        elif phase <= minphase:
            dphase = 1
        phase += dphase
        c -= 1
        time.sleep(0.1)


serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, width=32, height=8, block_orientation=-90)
device.contrast(100)

with canvas(device) as draw:
    text(draw, (0, 0), "Hiya", fill="white", font=CP437_FONT)
time.sleep(0.8)

double_sine(device)
