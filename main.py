from math import ceil, floor
import pygame
from pygame import Rect, Surface, Color
from pygame.math import Vector2


sprites: Surface
RED = Color("#FF0000")

class Element:
    _x: int
    _y: float
    visible: bool
    rect: Rect
    sprite_index: int

    def __init__(self, x: int, y: float, sprite_index: int):
        self.rect = Rect((0, 0), (16, 16))
        self.x = 16 * x
        self.y = 16.0 * y
        self.sprite_offset = 16 * sprite_index
        self.visible = False


    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value: int):
        self._x = value
        self.rect.left = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value: int):
        self._y = value
        self.rect.top = value

    def scroll(self):
        self._x -= 1

    def draw(self, surface: Surface):
        surface.blit(sprites, (self.x, self.y), (self.sprite_offset, 0, 16, 16))

    def __repr__(self):
        return f"<{self.__class__.__name__} ({self.x}, {self.y})>"

class Block(Element):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, 1)

class Spike(Element):
    def __init__(self, x: int, y: int, sprite_index: int):
        super().__init__(x, y, sprite_index)

class SpikeUp(Spike):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, 2)

class SpikeDown(Spike):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, 3)

class SpikeLeft(Spike):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, 4)

class SpikeRight(Spike):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, 5)

class FinishLine(Element):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, 6)

class Level:
    elements: list
    _scroll: float
    visible_elements: list

    def __init__(self):
        self.elements = []
        self.visible_elements = []
        self._scroll = 0.0
        #self.load()
        for x in range(0, 64):
            if x > 13 and x % 13 <= 4:
                continue
            self.elements.append(Block(x, 9))
            if x > 10:
                if x % 5 == 0 or x % 3 == 0:
                    self.elements.append(Block(x, 8))
                if x % 5 == 0 and x % 3 == 0:
                    self.elements.append(Block(x, 7))
        for y in range(0, 9):
            self.elements.append(FinishLine(63, y))
        self.update_visible_elements()

    def load(self):
        self.elements = []
        with open("level", "rt") as file:
            y = 0
            for line in file.readlines():
                for x in range(0, len(line)):
                    c = line[x]
                    print(c, end="")
                    if c == '#':
                        self.elements.append(Block(x, y))
                    elif c == '<':
                        self.elements.append(SpikeLeft(x, y))
                    elif c == '>':
                        self.elements.append(SpikeRight(x, y))
                    elif c == '^':
                        self.elements.append(SpikeUp(x, y))
                    elif c == 'v' or c == 'V':
                        self.elements.append(SpikeDown(x, y))
                    elif c == '|':
                        self.elements.append(FinishLine(x, y))

    def update_visible_elements(self):
        for element in self.elements:
            if element.visible and element.x < -16:
                element.visible = False
                self.visible_elements.remove(element)
            elif not element.visible and -16 < element.x < 320:
                element.visible = True
                self.visible_elements.append(element)

    def scroll(self, dt, velocity):
        self._scroll += dt * velocity
        i_scroll = int(self._scroll)
        if i_scroll > 0:
            for element in self.elements:
                element.x -= i_scroll
            self.update_visible_elements()
            self._scroll -= float(i_scroll)

class Player(Element):
    is_jumping: bool
    is_on_ground: bool
    velocity_x: float
    velocity_y: float
    _scroll: float

    def __init__(self):
        super().__init__(0, 0, 0)
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.is_jumping = False
        self.is_on_ground = False

    def jump(self):
        if not self.is_jumping and self.is_on_ground:
            self.velocity.y += 100

class Game:
    WAIT = 0
    RUNNING = 1
    PAUSED = 2
    WON = 10
    FAILED = 13
    BACKGROUND_COLOR = Color("#DC7EE5")

    status: int
    player: Player
    level: Level
    x_velocity: float
    y_velocity: float


    def __init__(self) -> None:
        self.status = Game.WAIT
        self.player = Player()
        self.y_velocity = 0.0

    def new_game(self, level):
        self.status = Game.WAIT
        self.level = level
        self.x_velocity = 0.0
        self.y_velocity = 0.0
        self.player.x = 0
        self.player.y = 16*8
        self.player.is_on_ground = True
        self.player.is_jumping = True

    def start(self):
        self.status = Game.RUNNING
        self.x_velocity = 250.0

    def jump(self):
        if self.player.is_on_ground:
            print("Jump !")
            self.y_velocity = 200.0

    def collides_with(self, element_types):
        for element in self.level.visible_elements:
            if not isinstance(element, element_types):
               continue
            if element.rect.colliderect(self.player.rect):
                # print(f"collided with {element}")
                return True
        return False

    def reached_finish_line(self):
        return self.collides_with(FinishLine)

    def collides_with_lethal_element(self):
        return self.collides_with((Block, Spike))

    def banged_head(self):
        return self.collides_with(Block)

    def landed_on_block(self):
        return self.collides_with(Block)

    def update(self, delta_time: float) -> bool:

        if self.status == Game.RUNNING:
            self.level.scroll(delta_time, self.x_velocity)

            if self.x_velocity > 0:
                self.player.y -= self.y_velocity * delta_time
                self.y_velocity -= 9.8
                self.player.is_on_ground = False
                print(f"player = {self.player.rect}, y_velocity = {self.y_velocity}")
                if self.y_velocity > 0 and self.banged_head():
                    # banged his head
                    print("Banged his head")
                    self.status = Game.FAILED
                    return False
                elif self.y_velocity < 0:
                    self.player.y += 1
                    if self.landed_on_block():
                        # banged his head
                        print("Landed on floor")
                        print(self.player)
                        self.y_velocity = 0
                        self.player.is_on_ground = True
                        self.player.y = 16 * floor(self.player.y / 16)
                        print(self.player)
                    elif self.player.y > 140:
                        # fell of the plateform
                        print("Fell off")
                        self.status = Game.FAILED
                        return False
                    else:
                        self.player.y -= 1

        if self.reached_finish_line():
            self.status = Game.WON
            return False
        if self.collides_with_lethal_element():
            self.status = Game.FAILED
            return False

        return True

    def render(self, surface: Surface):
        surface.fill(Game.BACKGROUND_COLOR)
        for element in self.level.visible_elements:
            element.draw(surface)
        self.player.draw(surface)


def main():
    global sprites

    # initializes the pygame module
    pygame.init()

    # creates a screen variable of size 800 x 600
    screen = pygame.display.set_mode([640, 320])

    # sets the frame rate of the program
    clock = pygame.time.Clock()

    camera = Rect((0, 0),(16 * 20, 16 * 10))
    camera.left = -20

    offscreen = Surface(camera.size)

    end = False

    sprites = pygame.image.load("sprites.png")

    game = Game()
    game.new_game(Level())
    game.start()
    game.status = Game.PAUSED
    #player.set_on_ground(level)

    while not end:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    end = True
                elif event.key == pygame.K_SPACE:
                    if game.status == Game.PAUSED:
                        game.status = Game.RUNNING
                    elif game.status == Game.RUNNING:
                        game.jump()
                elif event.key == pygame.K_F5:
                    game.new_game(Level())
                    game.start()
        dt = clock.tick(60) / 1000.0

        game.update(dt)
        #    end = True
        #    break

        game.render(offscreen)

        screen.blit(pygame.transform.scale(offscreen, (640,320)), (0,0))
        pygame.display.flip()

    pygame.quit()

main()