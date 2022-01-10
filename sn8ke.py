import random

import machine
import utime

from frozen.display import DISPLAY, reset_display
from frozen.buttons import BUTTON_DOWN, BUTTON_UP, BUTTON_ENTER
from frozen.colors import RED, BLACK, WHITE, GRAY, GREEN
from frozen.image import render_image

BGCOLOR = BLACK

BODY_COLOR = GRAY
HEAD_COLOR = WHITE
FOOD_COLOR = GREEN

DIR_STRAIGHT = 0
DIR_LEFT = -1
DIR_RIGHT = 1

# clock-wise order
BEARINGS = (
    (1, 0),  # right
    (0, 1),  # down
    (-1, 0),  # left
    (0, -1),  # up
)


class GamePlan(object):
    x0, y0 = 5, 15
    x1, y1 = DISPLAY.width - 5, DISPLAY.height - 5
    ps = 4  # pixel size

    def border(self, color: int):
        DISPLAY.fill_rectangle(self.x0, self.y0, self.w() * self.ps, self.h() * self.ps, color)
        DISPLAY.fill_rectangle(
            self.x0 + self.ps, self.y0 + self.ps,
            (self.w() - 2) * self.ps, (self.h() - 2) * self.ps,
            BGCOLOR)

    def pixel(self, x: int, y: int, color: int):
        DISPLAY.fill_rectangle(
            self.x0 + x * self.ps, self.y0 + y * self.ps, self.ps, self.ps, color)

    def w(self) -> int:
        return (self.x1 - self.x0) // self.ps

    def h(self) -> int:
        return (self.y1 - self.y0) // self.ps


class Snake(object):
    def __init__(self, x: int, y: int, plan: GamePlan):
        self.body = []
        self.food = 5
        self.plan = plan
        self.body.append((x, y))
        plan.pixel(x, y, BODY_COLOR)
        x += 1
        self.body.append((x, y))
        plan.pixel(x, y, HEAD_COLOR)

    def move(self, direction: int):
        # work out new head position
        hx, hy = self.body[-1]
        nx, ny = self.body[-2]
        dx = hx - nx
        dy = hy - ny
        bearing_index = BEARINGS.index((dx, dy))
        new_bearing_index = ((bearing_index + direction) + len(BEARINGS)) % len(BEARINGS)
        ndx, ndy = BEARINGS[new_bearing_index]
        nhx = hx + ndx
        nhy = hy + ndy

        # move head
        self.plan.pixel(hx, hy, BODY_COLOR)
        self.body.append((nhx, nhy))
        self.plan.pixel(nhx, nhy, HEAD_COLOR)

        if self.food > 0:
            self.food -= 1
        else:
            # move tail
            tx, ty = self.body[0]
            self.plan.pixel(tx, ty, BGCOLOR)
            del self.body[0]


class Food(object):
    x = 0
    y = 0
    value = 0

    def create(self, snake: Snake, plan: GamePlan):
        while True:
            self.x = random.randint(1, plan.w() - 2)
            self.y = random.randint(1, plan.h() - 2)
            if (self.x, self.y) not in snake.body:
                break
        self.value += 1
        plan.pixel(self.x, self.y, FOOD_COLOR)


def write_speed(speed: float):
    DISPLAY.set_pos(5, 5)
    DISPLAY.write("speed: %5.1f kp/h" % speed)


def write_speed_update(speed: float):
    DISPLAY.set_pos(5 + len("speed: ") * DISPLAY.font.max_width(), 5)
    DISPLAY.write("%5.1f" % speed)


def write_centered(text: str, y: int):
    text_width = len(text) * DISPLAY.font.max_width()
    x = (DISPLAY.width - text_width) // 2
    DISPLAY.set_pos(x, y)
    DISPLAY.write(text)


def delay2speed(delay_ms: int, step: int) -> float:
    return 3600 * step / delay_ms


def play_game():
    reset_display()

    delay_ms = 150

    plan = GamePlan()
    plan.border(RED)

    snake = Snake(plan.w() // 2, plan.h() // 2, plan)

    food = Food()
    food.create(snake, plan)

    write_speed(delay2speed(delay_ms, plan.ps))

    while True:
        if not BUTTON_DOWN.value():
            dir = DIR_LEFT
        elif not BUTTON_UP.value():
            dir = DIR_RIGHT
        else:
            dir = DIR_STRAIGHT

        snake.move(dir)

        head = snake.body[-1]
        if snake.body.index(head) != len(snake.body) - 1:
            # hit self
            break

        hx, hy = head
        if hx <= 0 or hx >= plan.w() - 1 or hy <= 0 or hy >= plan.h() - 1:
            # hit wall
            break

        if head == (food.x, food.y):
            start = utime.ticks_ms()
            snake.food += food.value
            food.create(snake, plan)
            delay_ms = max(0, delay_ms - 9)
            write_speed_update(delay2speed(delay_ms, plan.ps))
            utime.sleep_ms(max(0, delay_ms - utime.ticks_diff(utime.ticks_ms(), start)))
        else:
            utime.sleep_ms(delay_ms)

    write_centered("You crashed!", 100)
    write_centered("Wear a helmet!", 120)
    write_centered("top speed", 140)
    write_centered("%.2f" % delay2speed(delay_ms, plan.ps), 152)
    write_centered("kilopixels per hour", 164)


def run():
    reset_display()
    render_image(DISPLAY, "/sn8ke.pic", 0, 0, 240, 320)
    utime.sleep_ms(3000)

    while True:
        play_game()
        utime.sleep_ms(1000)
        while True:
            if not BUTTON_ENTER.value():
                break
            if not BUTTON_UP.value() and not BUTTON_DOWN.value():
                machine.reset()
            utime.sleep_ms(10)
