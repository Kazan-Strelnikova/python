import pygame
import sys
import os
import random

FPS = 8

clock = pygame.time.Clock()
running = True
pygame.init()
size = 539, 539
screen = pygame.display.set_mode(size)
image = pygame.Surface([100, 100])
cell = 0
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0
cell = size[0] // 29#кол-во клеточек

def load_image(name):
    fullname = os.path.join(name)
    image = pygame.image.load(fullname).convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()



def runGame():
    global headpos
    screen.fill((0, 100, 0))
    all_sprites.draw(screen)
    # Set a random start point.
    startx = random.randint(5, cell - 6)
    starty = random.randint(5, cell - 6)
    snake = [{'x': startx, 'y': starty}, {'x': startx - 1, 'y': starty}, {'x': startx - 2, 'y': starty}]
    direction = RIGHT

    # Start the apple in a random place.
    apple = getRandomLocation()

    while True:  # main game loop
        for event in pygame.event.get():  # event handling loop
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and direction != RIGHT:
                    direction = LEFT
                elif event.key == pygame.K_RIGHT and direction != LEFT:
                    direction = RIGHT
                elif event.key == pygame.K_UP and direction != DOWN:
                    direction = UP
                elif event.key == pygame.K_DOWN and direction != UP:
                    direction = DOWN
                elif event.key == pygame.K_ESCAPE:
                    terminate()

        # check if the worm has hit itself or the edge
        if snake[HEAD]['x'] == -1 or snake[HEAD]['x'] == cell or snake[HEAD]['y'] == -1 or snake[HEAD]['y'] == cell:
            gameover()  # game over
        for wormBody in snake[1:]:
            if wormBody['x'] == snake[HEAD]['x'] and wormBody['y'] == snake[HEAD]['y']:
                gameover()  # game over

        # check if worm has eaten an apply
        if snake[HEAD]['x'] == apple['x'] and snake[HEAD]['y'] == apple['y']:
            # don't remove worm's tail segment
            apple = getRandomLocation()  # set a new apple somewhere
        else:
            del snake[-1]  # remove worm's tail segment

        # move the worm by adding a segment in the direction it is moving
        if direction == UP:
            newHead = {'x': snake[HEAD]['x'], 'y': snake[HEAD]['y'] - 1}
        elif direction == DOWN:
            newHead = {'x': snake[HEAD]['x'], 'y': snake[HEAD]['y'] + 1}
        elif direction == LEFT:
            newHead = {'x': snake[HEAD]['x'] - 1, 'y': snake[HEAD]['y']}
        elif direction == RIGHT:
            newHead = {'x': snake[HEAD]['x'] + 1, 'y': snake[HEAD]['y']}
        snake.insert(0, newHead)
        headpos = newHead

        drawSnake(snake, direction)
        drawApple(apple)
        pygame.display.update()
        clock.tick(FPS)


def getRandomLocation():
    return {'x': random.randint(0, cell - 1), 'y': random.randint(0, cell - 1)}


def start_screen():
    intro_text = [" Змейка "]

    fon = pygame.transform.scale(load_image('snake.jpg'), (size[0], size[1]))

    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 100)
    text_coord = 120
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('pink'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 130
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def gameover():
    intro_text = [" GAME ", ' OVER ']
    font = pygame.font.Font(None, 200)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color(247, 121, 167))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 30
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                runGame()  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    global cell
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))
    #cell = max_width если поле больше экрана
    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_images = {'wall': load_image('box.png'), 'empty': load_image('grass.png')}
tile_width = tile_height = 30

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)

def generate_level(level):
    x, y = None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
    return x, y


def drawSnake(snake, direction):
    all_sprites.draw(screen)
    for coord in snake:
        x = coord['x'] * tile_width
        y = coord['y'] * tile_height
        if coord == snake[0] and direction == UP:
            image = load_image("headu.png")
            screen.blit(image, (x, y))
        elif coord == snake[0] and direction == DOWN:
            image = load_image("headd.png")
            screen.blit(image, (x, y))
        elif coord == snake[0] and direction == LEFT:
            image = load_image("headl.png")
            screen.blit(image, (x, y))
        elif coord == snake[0] and direction == RIGHT:
            image = load_image("headr.png")
            screen.blit(image, (x, y))
        else:
            image = load_image("body.png")
            screen.blit(image, (x, y))


def drawApple(apple):
    x = apple['x'] * tile_width
    y = apple['y'] * tile_height
    image = load_image("apple.png")
    screen.blit(image, (x, y))



level = load_level('map1.txt')
level_x, level_y = generate_level(load_level('map1.txt'))

start_screen()
screen.fill((0, 100, 0))
all_sprites.draw(screen)
while True:
    runGame()
