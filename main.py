import pygame
import sys
import math
import random
import itertools


class Game(object):

    def __init__(self):
        self.fps = 60
        self.clock = pygame.time.Clock()
        self.screen_width = 720
        self.screen_height = 960
        self.rows = 8
        self.columns = 8
        self.dt = 0

        pygame.init()
        pygame.display.set_caption("Clotzky")
        self.display = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.board = Board(self.rows, self.columns)

    def loop(self):
        while True:
            self.draw()
            self.events()
            self.board.match()
            self.board.remove()
            self.clock.tick(self.fps)
            self.dt = 0

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.board.input(event)
            # if event.type == pygame.KEYDOWN:
            #     self.board.input(event)

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
        self.tiles_image = [pygame.image.load("images/{}.png".format(tile)) for tile in tiles_list.split()]
        # przeskalowanie obrazkow klockow wzgledem wielkosci ekranu
        self.tiles_image = [pygame.transform.scale(i, (self.tile_side, self.tile_side)) for i in self.tiles_image]
        # zapełnienie planszy przezroczystmi obrazkami (puste pola)
        self.board = [self.tiles_image[0] for _ in range(self.size)]
        # stworzenie rect na podstawie board
        self.tiles_rect_list = [tile.get_rect() for tile in self.board]
        print(self.tiles_rect_list[1])
        # przypisanie obiektom odppowiednich wspolrzednych
        for i, tile in enumerate(self.tiles_rect_list):
            tile.x = (self.left_margin + ((i % self.columns) * self.tile_side*1))
            tile.y = (self.top_margin + (math.floor(i / self.columns) * self.tile_side*1))
        # stworzenie obiektow klasy Tiles
        self.board = [Tiles(self.tiles_image[0], (self.tiles_rect_list[i])) for i in range(self.size)]
        self.reset()

    def reset(self):
        for i in range(self.size):
            self.board[i] = Tiles(random.choice(self.tiles_image[1:-1]), self.board[i].tile_rect)

    def input(self, event):
        # zaznaczenie klocka
        if not self.selected:
            for i, tile in enumerate(self.board):
                if tile.tile_rect.collidepoint(event.pos) and tile.tile_type in self.tiles_image[1:-1]:
                    self.cursor = i
                    self.selected = True
                    print("coord selection", tile.tile_rect)
                    print("cursor", self.cursor)

        elif self.selected:
            self.switch(event)
        # if event.key == pygame.K_DOWN:
        #     self.board[0].tile_rect.move(10, 10)
        #     print("3", self.board[0].tile_rect)

    def switch(self, event):
        def switch_animation(selected, target):
            self.distance_x = (selected.tile_rect.x - target.tile_rect.x)
            self.distance_y = (selected.tile_rect.y - target.tile_rect.y)
            print("1 sel", selected.tile_rect)
            print("1 tar", target.tile_rect)
            selected.tile_rect.move_ip(-self.distance_x, -self.distance_y)
            target.tile_rect.move_ip(self.distance_x, self.distance_y)
            print("2 sel", selected.tile_rect)
            print("2 tar", target.tile_rect)

        for i, tile in enumerate(self.board):
            if tile.tile_rect.collidepoint(event.pos) and tile.tile_type in self.tiles_image[1:-1]:
                # cofniecie zaznaczenia klocka jesli nastapi jego ponowne klikniecie
                if self.cursor == i:
                    self.selected = False

                # zamiana miejsc dwoch klockow
                else:
                    # zabezpieczenie przed zamiana pierwszego klocka w rzedzie z ostatnim klockiem rzedu wyzszego
                    if self.cursor % self.columns == 0 and i % self.columns == self.columns - 1:
                        if i in (self.cursor + 1, self.cursor + self.columns, self.cursor - self.columns):
                                self.selected = False
                                self.board[i], self.board[self.cursor] = self.board[self.cursor], self.board[i]
                                switch_animation(self.board[self.cursor], self.board[i])

                    # zabezpieczenie przed zamiana ostatniego klocka w rzedzie z pierwszym klockiem rzedu nizszego
                    elif self.cursor % self.columns == self.columns - 1 and i % self.columns == 0:
                        if i in (self.cursor - 1, self.cursor + self.columns, self.cursor - self.columns):
                                self.selected = False
                                self.board[i], self.board[self.cursor] = self.board[self.cursor], self.board[i]
                                switch_animation(self.board[self.cursor], self.board[i])

                    else:
                        if i in (self.cursor + 1, self.cursor - 1, self.cursor + self.columns, self.cursor - self.columns):
                                self.selected = False
                                self.board[i], self.board[self.cursor] = self.board[self.cursor], self.board[i]
                                switch_animation(self.board[self.cursor], self.board[i])

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
                self.board[i] = Tiles(self.tiles_image[0], self.board[i].tile_rect)

    def fall(self):
        pass

    def draw(self, display):
        # rysowanie tla
        display.blit(self.background, (0, 0))
        # rysowanie biezacej zawartosci tablicy
        for i, tile in enumerate(self.board):
            display.blit(tile.tile_type, tile.tile_rect)
        if self.selected:
            self.board[self.cursor].tile_rect = self.board[self.cursor].tile_rect.move(self.vy, self.vy)
            self.vy = -self.vy


class Tiles(object):
    def __init__(self, tile_type, tile_rect):
        self.tile_type = tile_type
        self.tile_rect = tile_rect

if __name__ == '__main__':
    Game().loop()
