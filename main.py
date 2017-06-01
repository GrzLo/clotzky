import pygame
import sys
import math
import random
import itertools


class Game(object):

    def __init__(self):
        self.fps = 30
        self.clock = pygame.time.Clock()
        self.screen_width = 720
        self.screen_height = 960
        self.rows = 8
        self.columns = 8

        pygame.init()
        pygame.display.set_caption("Klocki ALPHA")
        self.display = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.board = Board(self.rows, self.columns)

    def loop(self):
        while True:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.board.input(event)
            self.board.match()
            self.board.remove()
            self.clock.tick(self.fps)

    def quit(self):
        pygame.quit()
        sys.exit()

    def draw(self):
        self.board.draw(self.display)
        # self.board.draw_cursor(self.display)
        # print("fps: ", self.clock.get_fps())
        pygame.display.update()


class Board(object):
    def __init__(self, rows, columns):
        self.screen_height = pygame.display.Info().current_h
        self.screen_width = pygame.display.Info().current_w
        self.rows = rows
        self.columns = columns
        self.size = rows * columns
        self.left_margin = self.screen_height / 7.68
        self.top_margin = self.screen_width / 6.83
        self.cursor = None
        self.vy = 1
        self.selected = False
        self.event = None

        # ustawienie wartości długości boków klocków
        if self.rows > self.columns:
            self.tile_side = math.floor((self.screen_height - self.top_margin*2) / self.rows)
        else:
            self.tile_side = math.floor((self.screen_width - self.left_margin*2) / self.columns)
        # załadowanie tla
        self.background = pygame.image.load("images/bg.jpg")
        # przeskalowanie obrazka tla wzgledem wielkosci ekranu
        self.background = pygame.transform.scale(self.background, (self.screen_width, self.screen_height))

        tiles_list = "empty red blue green yellow"
        # stworzenie listy przechowujaca zaladowane pliki z obrazkami klockow
        self.tiles_list = [pygame.image.load("images/{}.png".format(tile)) for tile in tiles_list.split()]
        # przeskalowanie obrazkow klockow wzgledem wielkosci ekranu
        self.tiles_list = [pygame.transform.scale(i, (self.tile_side, self.tile_side)) for i in self.tiles_list]
        # zapełnienie planszy przezroczystmi obrazkami (puste pola)
        self.board = [self.tiles_list[0] for _ in range(self.size)]
        # stworzenie rect na podstawie board
        self.tiles_rect_list = [tile.get_rect() for tile in self.board]
        # stworzenie obiektow klasy Tiles
        self.board = [Tiles(self.tiles_list[0], (0, 0)) for _ in range(self.size)]
        # przypisanie obiektom odppowiednich wspolrzednych
        for i, tile in enumerate(self.tiles_rect_list):
            tile.x = (self.left_margin + ((i % self.columns) * self.tile_side*1))
            tile.y = (self.top_margin + (math.floor(i / self.columns) * self.tile_side*1))
        self.reset()

    def reset(self):
        for i in range(self.size):
            self.board[i] = Tiles(random.choice(self.tiles_list[1:-1]), self.tiles_rect_list)

    def input(self, event):
        if not self.selected:
            for i, tile in enumerate(self.tiles_rect_list):
                if tile.collidepoint(event.pos):
                    self.selected = True
                    self.cursor = i
        elif self.selected:
            self.switch(event)

    def switch(self, event):
        self.event = event
        for i, tile in enumerate(self.tiles_rect_list):
            if tile.collidepoint(event.pos):
                # cofniecie zaznaczenia klocka
                if self.cursor == i:
                    self.selected = False
                    # print("kursor:", self.cursor)
                    # print("i:", i)

                # zamiana miejsc dwoch klockow
                else:
                    if i in (self.cursor + 1, self.cursor - 1, self.cursor + 8, self.cursor - 8):
                        self.board[i], self.board[self.cursor] = self.board[self.cursor], self.board[i]
                        self.selected = False
                        # print("kursor:", self.cursor)
                        # print("i:", i)

    def match(self):
        def lines():
            for i in range(self.columns):
                yield range(i, self.size, self.columns)

            for j in range(self.rows):
                yield range(j * self.columns, (j + 1) * self.columns)

        def compare():
            for i, line in enumerate(lines()):
                for k, g in itertools.groupby(line, lambda i: self.board[i].tile_type):
                    sequence = list(g)
                    if len(sequence) >= 3:
                        yield sequence
        return list(compare())

    def remove(self):
        for line in self.match():
            for i in line:
                self.board[i] = Tiles(self.tiles_list[0], self.tiles_rect_list)

    def draw(self, display):
        # rysowanie tla
        display.blit(self.background, (0, 0))
        # rysowanie biezacej zawartosci tablicy
        for i, tile in enumerate(self.board):
            display.blit(tile.tile_type, self.tiles_rect_list[i])
        if self.selected:
            self.tiles_rect_list[self.cursor] = self.tiles_rect_list[self.cursor].move(self.vy, self.vy)
            self.vy = -self.vy


class Tiles(object):
    def __init__(self, tile_type, tile_rect):
        self.tile_type = tile_type
        self.tile_rect = tile_rect

if __name__ == '__main__':
    Game().loop()
