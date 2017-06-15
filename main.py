import pygame
import sys
import math
import random
import itertools
import pickle


class Game(object):

    def __init__(self):
        self.fps = 60
        self.clock = pygame.time.Clock()
        self.screen_width = 720
        self.screen_height = 960
        self.rows = 8
        self.columns = 8

        pygame.init()
        pygame.display.set_caption("Clotzky")
        self.display = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.board = Board(self.rows, self.columns)

    def loop(self):
        while True:
            self.draw()
            self.events()
            self.board.tick()
            self.clock.tick(self.fps)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.board.input(event)

    def draw(self):
        self.board.draw(self.display)
        # self.board.draw_cursor(self.display)
        # print("fps: ", self.clock.get_fps())
        pygame.display.update()

    def quit(self):
        pygame.quit()
        sys.exit()


class Board(object):
    def __init__(self, rows, columns):
        self.screen_height = pygame.display.Info().current_h
        self.screen_width = pygame.display.Info().current_w
        self.rows = rows
        self.columns = columns
        # calkowita liczba klockow na planszy
        self.size = rows * columns
        # marginesy
        self.left_margin = self.screen_height / 7.68
        self.top_margin = self.screen_width / 6.83
        # inicjalizacja zmiennych zwiazanych z polem gry
        self.event = None
        self.matches = None
        self.fall = None
        self.cursor = None
        self.selected = False
        self.animation = []
        # zmienna przechowywujaca ktore obiekty zamienic miejscami oraz jaka jest pomiedzy nimi odleglosc
        self.switch_details = []
        self.vy = 5
        self.asd = True

        # ustawienie wartości długości boków klocków
        if self.rows > self.columns:
            self.tile_side = math.floor((self.screen_height - self.top_margin*2) / self.rows)
        else:
            self.tile_side = math.floor((self.screen_width - self.left_margin*2) / self.columns)
        # załadowanie tla
        self.background = pygame.image.load("images/bg.jpg")
        # przeskalowanie obrazka tla wzgledem wielkosci ekranu
        self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))
        # lista klockow
        self.tiles_list = ["empty", "red", "blue", "green", "yellow"]
        # ladowanie obrazkow klockow
        self.tile_images_original = [pygame.image.load("images/{}.png".format(i)) for i in self.tiles_list]
        # przeskalowanie obrazkow klockow
        self.tile_images = [pygame.transform.scale(i, (self.tile_side, self.tile_side)) for i in self.tile_images_original]
        # zapelnienie planszy, stworzenie obiektow klasy Tiles
        self.board = [Tiles(self.tile_images[1], (self.tile_side, self.tile_side), self.tile_images_original) for _ in range(self.size)]
        # przypisanie obiektom odpowiednich wspolrzednych
        for i, tile in enumerate(self.board):
            tile.tile_position.x = (self.left_margin + ((i % self.columns) * self.tile_side * 1))
            tile.tile_position.y = (self.top_margin + (math.floor(i / self.columns) * self.tile_side * 1))
        self.board_generator()

    def board_generator(self):
        while self.match():
            for i in range(self.size):
                self.board[i].tile_type = random.choice(self.tile_images[1:-1])
            # with open("generatedboards.pk1", "wb") as output:
            #     pickle.dump(self.board, output, pickle.HIGHEST_PROTOCOL)

    def input(self, event):
        # zaznaczenie klocka
        print(self.animation)
        if not self.animation:
            if not self.selected:
                for i, tile in enumerate(self.board):
                    if tile.tile_position.collidepoint(event.pos) and tile.tile_type in self.tile_images[1:-1]:
                        self.cursor = i
                        self.selected = True
                        # self.possible_match()

            elif self.selected:
                self.switch(event)

    def switch(self, event):

        for i, tile in enumerate(self.board):
            if tile.tile_position.collidepoint(event.pos) and tile.tile_type in self.tile_images[1:-1]:

                # cofniecie zaznaczenia klocka jesli nastapi jego ponowne klikniecie
                if self.cursor == i:
                    self.selected = False
                    self.asd = True
                    # tile.tile_position.x = (self.left_margin + ((i % self.columns) * self.tile_side * 1))
                    # tile.tile_position.y = (self.top_margin + (math.floor(i / self.columns) * self.tile_side * 1))
                    print(tile.tile_position.x, tile.tile_position.y)

                # zamiana miejsc dwoch klockow
                else:
                    # zabezpieczenie przed zamiana pierwszego klocka w rzedzie z ostatnim klockiem rzedu wyzszego
                    if self.cursor % self.columns == 0 and i % self.columns == self.columns - 1:
                        if i in (self.cursor + 1, self.cursor + self.columns, self.cursor - self.columns):
                                self.selected = False
                                self.board[self.cursor], self.board[i] = self.board[i], self.board[self.cursor]
                                if self.match():
                                    self.animation = (1, self.tile_side)
                                else:
                                    self.animation = (2, self.tile_side*2)
                                    self.board[self.cursor], self.board[i] = self.board[i], self.board[self.cursor]

                    # zabezpieczenie przed zamiana ostatniego klocka w rzedzie z pierwszym klockiem rzedu nizszego
                    elif self.cursor % self.columns == self.columns - 1 and i % self.columns == 0:
                        if i in (self.cursor - 1, self.cursor + self.columns, self.cursor - self.columns):
                                self.selected = False
                                self.board[self.cursor], self.board[i] = self.board[i], self.board[self.cursor]
                                if self.match():
                                    self.animation = (1, self.tile_side)
                                else:
                                    self.animation = (2, self.tile_side*2)
                                    self.board[self.cursor], self.board[i] = self.board[i], self.board[self.cursor]

                    else:
                        if i in (self.cursor + 1, self.cursor - 1, self.cursor + self.columns, self.cursor - self.columns):
                                self.selected = False
                                self.board[self.cursor], self.board[i] = self.board[i], self.board[self.cursor]
                                if self.match():
                                    self.animation = [1, self.tile_side]
                                    print(self.animation)
                                else:
                                    self.animation = [2, self.tile_side*2]
                                    print(self.animation)
                                    self.board[self.cursor], self.board[i] = self.board[i], self.board[self.cursor]

                    self.switch_details = [self.board[self.cursor], self.board[i], self.board[i].tile_position.x - self.board[self.cursor].tile_position.x, self.board[i].tile_position.y - self.board[self.cursor].tile_position.y]
                    # print(self.switch_details)

    def match(self):
        def lines():
            for i in range(self.columns):
                yield range(i, self.size, self.columns)

            for j in range(self.rows):
                yield range(j * self.columns, (j + 1) * self.columns)

        def compare():
            for i, line in enumerate(lines()):
                for k, g in itertools.groupby(line, lambda i: self.board[i].tile_type):
                    # if k == self.tiles_image[0]:
                    #     pass
                    # else:
                    sequence = list(g)
                    if len(sequence) >= 3 and k in self.tile_images[1:-1]:
                        yield sequence
        # print(list(compare()))
        return list(compare())

    def possible_match(self):
        def lines():
            for i in range(self.columns):
                yield range(i, self.size, self.columns)

            for j in range(self.rows):
                yield range(j * self.columns, (j + 1) * self.columns)

        def compare():
            for i, line in enumerate(lines()):
                for k, g in itertools.groupby(line, lambda i: self.board[i].tile_type):
                    sequence = list(g)
                    if len(sequence) == 2:
                        yield sequence
        print(compare())
        return list(compare())

    def tick(self):
        if self.selected:
            if self.asd:
                self.asd = False
                print(self.cursor)
            self.board[self.cursor].update(0, 0, True)
            # print(self.board[self.cursor].tile_position.h)
            # self.board[self.cursor].tile_position = self.board[self.cursor].tile_position.inflate(10, 10)
            # self.selected = False
            # self.vy = -self.v

        if not self.animation:
            self.matches = self.match()
            if self.matches:
                for match in self.matches:
                    for tile in match:
                        self.board[tile].tile_type = self.tile_images[0]

        self.animate(self.animation)

    def animate(self, animation):
        def normal():
            self.switch_details[0].update(self.switch_details[2], self.switch_details[3], False)
            self.switch_details[1].update(-self.switch_details[2], -self.switch_details[3], False)
            self.animation[1] -= 2
            if self.animation[1] == 0:
                self.animation = []

        def revert():
            if animation[1] > self.tile_side:
                self.switch_details[0].update(self.switch_details[2], self.switch_details[3], False)
                self.switch_details[1].update(-self.switch_details[2], -self.switch_details[3], False)
                self.animation[1] -= 2
            else:
                self.switch_details[0].update(-self.switch_details[2], -self.switch_details[3], False)
                self.switch_details[1].update(self.switch_details[2], self.switch_details[3], False)
                self.animation[1] -= 2
                if self.animation[1] == 0:
                    self.animation = []

        if animation:
            if animation[0] == 1 and animation[1] > 0:
                normal()
            elif animation[0] == 2 and animation[1] > 0:
                revert()

        # def fall(self):
        #     pass

    def draw(self, display):
        # rysowanie tla
        display.blit(self.background, (0, 0))
        # rysowanie biezacej zawartosci tablicy
        for tile in self.board:
            display.blit(tile.tile_type, tile.tile_position)


class Tiles(pygame.sprite.Sprite):
    def __init__(self, tile_type, size, images):
        pygame.sprite.Sprite.__init__(self)
        self.images = images
        # stworzenie obiektu surface i rect
        self.tile_position = pygame.Surface(size)
        self.tile_position = self.tile_position.get_rect()
        self.tile_type = tile_type
        self.tile_type_copy = tile_type

    def update(self, move_x, move_y, selected):
        # if selected:
            # print(self.tile_position)
            # self.tile_type = self.images[1]
        # else:
        #     self.tile_type = self.tile_type_copy
        if move_x != 0:
            self.tile_position.x += (move_x / abs(move_x)) * 2
        if move_y != 0:
            self.tile_position.y += (move_y / abs(move_y)) * 2


if __name__ == '__main__':
    Game().loop()
