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

        self.rows = 6
        self.columns = 6

        pygame.init()
        pygame.display.set_caption("Clotzky")
        self.display = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.font = pygame.font.Font(None, 40)
        self.gui = Gui(self.font, self.display)
        self.board = Board(self.rows, self.columns, self.gui)

    def loop(self):
        """
        Main game loop, all events checks and drawing take place here
        @return:
        """
        while True:
            self.draw()
            self.events()
            self.gui.events()
            self.board.tick()
            self.clock.tick(self.fps)

    def events(self):
        """
        Method for checking if any pygame events occur, such as button or key press
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.board.input(event)

    def draw(self):
        """
        Main drawing method. All drawing methods from sub classes are executed here
        @return:
        """
        self.board.draw(self.display)
        self.gui.draw()
        # self.board.draw_cursor(self.display)
        # print("fps: ", self.clock.get_fps())
        pygame.display.update()

    def quit(self):
        """
        Method used to exit the game
        @return:
        """
        pygame.quit()
        sys.exit()


class Board(object):
    def __init__(self, rows, columns, gui):
        """
        The init method for the class board takes 3 parameters
        @param rows: numbers of rows
        @param columns: numbers of columns
        @param gui: gui object, to allow communication between those two classes

        also the main game board is generated here, and different kind of variables for later use
        the game board is drawn dinamically based on the resolution and row-column ammount
        """
        self.screen_height = pygame.display.Info().current_h
        self.screen_width = pygame.display.Info().current_w
        self.gui = gui
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
        self.cursor = None
        self.selected = False
        # zmienne przechowywujace czas animacji oraz ktore obiekty zamienic miejscami i jaka jest odleglosc miedzy nimi
        self.switch_animation = []
        self.switch_details = []
        # zmienne przechowujace czas animacji spadania oraz ktore obiekty maja spadac
        self.fall_animation = []
        self.fall_details = []
        # zmienne przechowujace czas animacji "nowych" obiektow
        self.refill_animation = []
        self.refill_details = []
        self.dt = 6
        # liczba bazowych punktow
        self.points = 100
        # max punkty
        self.max_score = 10000

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
        self.board = [Tiles(self.tile_images[1], (self.tile_side, self.tile_side), self.tile_images_original, self.dt, self.tiles_list[1]) for _ in range(self.size)]
        # przypisanie obiektom odpowiednich wspolrzednych
        for i, tile in enumerate(self.board):
            tile.tile_position.x = (self.left_margin + ((i % self.columns) * self.tile_side))
            tile.tile_position.y = (self.top_margin + (math.floor(i / self.columns) * self.tile_side))
        self.board_generator()

    def board_generator(self):
        """
        a method to generate a board, it can be also saved to a file and later loaded for less waiting time
        @return:
        """
        while self.match():
            for i in range(self.size):
                choice = random.randrange(1, 4)
                self.board[i].tile_type = self.tile_images[choice]
                self.board[i].color = self.tiles_list[choice]
            # with open("generatedboards.pk1", "wb") as output:
            #     pickle.dump(self.board, output, pickle.HIGHEST_PROTOCOL)

    def input(self, event):
        """
        a class that detecs user input and act accordingly depending on the user's action
        @param event:
        @return:
        """
        # zaznaczenie klocka
        if not self.switch_animation and not self.fall_animation and not self.refill_animation:
            if not self.selected:
                for i, tile in enumerate(self.board):
                    if tile.tile_position.collidepoint(event.pos) and tile.color in self.tiles_list[1:-1]:
                        self.cursor = i
                        self.selected = True
                        # self.possible_match()

            elif self.selected:
                self.switch(event)

    def switch(self, event):
        """
        A method used to switch two tiles next to each other, it is made so that it is impossible to switch several
        tiles at once or in the not meant direction ie. diagonally
        @param event:
        @return:
        """
        for i, tile in enumerate(self.board):
            if tile.tile_position.collidepoint(event.pos) and tile.color in self.tiles_list[1:-1]:
                # cofniecie zaznaczenia klocka jesli nastapi jego ponowne klikniecie
                if self.cursor == i:
                    a = self.tiles_list.index(self.board[self.cursor].color)
                    self.board[self.cursor].update_image(self.tile_images[a], 0)
                    self.selected = False
                    # tile.tile_position.x = (self.left_margin + ((i % self.columns) * self.tile_side * 1))
                    # tile.tile_position.y = (self.top_margin + (math.floor(i / self.columns) * self.tile_side * 1))

                # zamiana miejsc dwoch klockow
                else:
                    a = self.tiles_list.index(self.board[self.cursor].color)
                    self.board[self.cursor].update_image(self.tile_images[a], 0)
                    # zabezpieczenie przed zamiana pierwszego klocka w rzedzie z ostatnim klockiem rzedu wyzszego
                    if self.cursor % self.columns == 0 and i % self.columns == self.columns - 1:
                        if i in (self.cursor + 1, self.cursor + self.columns, self.cursor - self.columns):
                                self.selected = False
                                self.board[self.cursor], self.board[i] = self.board[i], self.board[self.cursor]
                                if self.match():
                                    self.switch_animation = [1, self.tile_side]
                                else:
                                    self.switch_animation = [2, self.tile_side * 2]
                                    self.board[self.cursor], self.board[i] = self.board[i], self.board[self.cursor]

                    # zabezpieczenie przed zamiana ostatniego klocka w rzedzie z pierwszym klockiem rzedu nizszego
                    elif self.cursor % self.columns == self.columns - 1 and i % self.columns == 0:
                        if i in (self.cursor - 1, self.cursor + self.columns, self.cursor - self.columns):
                                self.selected = False
                                self.board[self.cursor], self.board[i] = self.board[i], self.board[self.cursor]
                                if self.match():
                                    self.switch_animation = [1, self.tile_side]
                                else:
                                    self.switch_animation = [2, self.tile_side * 2]
                                    self.board[self.cursor], self.board[i] = self.board[i], self.board[self.cursor]

                    else:
                        if i in (self.cursor + 1, self.cursor - 1, self.cursor + self.columns, self.cursor - self.columns):
                                self.selected = False
                                self.board[self.cursor], self.board[i] = self.board[i], self.board[self.cursor]
                                if self.match():
                                    self.switch_animation = [1, self.tile_side]
                                else:
                                    self.switch_animation = [2, self.tile_side * 2]
                                    self.board[self.cursor], self.board[i] = self.board[i], self.board[self.cursor]

                    self.switch_details = [self.board[self.cursor], self.board[i], self.board[i].tile_position.x - self.board[self.cursor].tile_position.x, self.board[i].tile_position.y - self.board[self.cursor].tile_position.y]

    def match(self):
        """
        a method used to find matching tiles which are later removed
        @return: returns a list of matching tiles
        """
        def lines():
            for i in range(self.columns):
                yield range(i, self.size, self.columns)

            for j in range(self.rows):
                yield range(j * self.columns, (j + 1) * self.columns)

        def compare():
            for i, line in enumerate(lines()):
                for k, g in itertools.groupby(line, lambda i: self.board[i].color):
                    # if k == self.tiles_image[0]:
                    #     pass
                    # else:
                    sequence = list(g)
                    if len(sequence) >= 3 and k in self.tiles_list[1:-1]:
                        yield sequence
        # print(list(compare()))
        return list(compare())

    # def possible_match(self):
    #     def lines():
    #         for i in range(self.columns):
    #             yield range(i, self.size, self.columns)
    #
    #         for j in range(self.rows):
    #             yield range(j * self.columns, (j + 1) * self.columns)
    #
    #     def compare():
    #         for i, line in enumerate(lines()):
    #             for k, g in itertools.groupby(line, lambda i: self.board[i].color):
    #                 sequence = list(g)
    #                 if len(sequence) == 2:
    #                     yield sequence
    #     print(compare())
    #     return list(compare())

    def fall_check(self):
        """
        a method used to check if there are any empty tile. it allows the tiles to fall down
        @return:
        """
        for i in range(self.size-self.columns):
            # klocek musi byc kolorowy
            if self.board[i].color in self.tiles_list[1:-1] and self.board[i+self.columns].color == self.tiles_list[0]:
                self.board[i], self.board[i+self.columns] = self.board[i+self.columns], self.board[i]
                self.fall_details.append([self.board[i], self.board[i+self.columns], self.board[i+self.columns].tile_position.y - self.board[i].tile_position.y])
                self.fall_animation.append(self.tile_side)

        if not self.fall_animation:
            for i, tile in enumerate(self.board):
                if tile.color == self.tiles_list[0]:
                    choice = random.randrange(1, 4)
                    tile.tile_type = self.tile_images[choice]
                    tile.color = self.tiles_list[choice]
                    tile.tile_position.y -= self.tile_side
                    self.refill_details.append([self.board[i], self.tile_side])
                    self.refill_animation.append(self.tile_side)
        random.shuffle(self.refill_details)

    def tick(self):
        """
        this method is used to sequence every event such as falling tiles, refilling, swapping
        @return:
        """
        if self.selected:
            self.board[self.cursor].update_image(self.board[self.cursor].tile_type, 90)
            # print(self.board[self.cursor].tile_position.h)
            # self.board[self.cursor].tile_position = self.board[self.cursor].tile_position.inflate(10, 10)
            # self.selected = False
            # self.vy = -self.v

        if not self.switch_animation:
            self.fall_check()
            if not self.refill_animation:
                self.matches = self.match()
                if self.matches:
                    for match in self.matches:
                        self.gui.get_score(self.points * len(match), self.max_score)
                        for tile in match:
                            self.board[tile].color = self.tiles_list[0]
                            self.board[tile].tile_type = self.tile_images[0]

        self.animate(self.switch_animation, self.fall_animation)

    def animate(self, switch_animation, fall_animation):
        """
        a method used for animation, both fall animation and switch animation
        @param switch_animation:
        @param fall_animation:
        @return:
        """
        def normal():
            """
            this switch method is used when there is a match
            @return:
            """
            # przemiesc pierwszy klocek w miejsce drugiego (roznica wspolrzednych miedzy nimi)
            self.switch_details[0].update(self.switch_details[2], self.switch_details[3])
            # przemiesc drugi klocek w miejsce pierwszego (roznica wspolrzednych miedzy nimi)
            self.switch_details[1].update(-self.switch_details[2], -self.switch_details[3])
            self.switch_animation[1] -= self.dt
            if self.switch_animation[1] <= 0:
                self.switch_animation = []

        def revert():
            """
            this switch method is used when there is no match, it reverts the tiles back to their original places
            @return:
            """
            if switch_animation[1] > self.tile_side:
                # przemiesc pierwszy klocek w miejsce drugiego
                self.switch_details[0].update(self.switch_details[2], self.switch_details[3])
                # przemiesc drugi klocek w miejsce pierwszego
                self.switch_details[1].update(-self.switch_details[2], -self.switch_details[3])
                self.switch_animation[1] -= self.dt
            else:
                # gdy zamienia sie miejscami, przemiesc je spowrotem do swojego pierwotnego polozenia
                self.switch_details[0].update(-self.switch_details[2], -self.switch_details[3])
                self.switch_details[1].update(self.switch_details[2], self.switch_details[3])
                self.switch_animation[1] -= self.dt
                if self.switch_animation[1] <= 0:
                    self.switch_animation = []

        def fall():
            """
            this method is used for fall animation
            @return:
            """
            # animacja spadania, osobny czas spadania dla kazdego klocka, gdy wszystkie czasy wyniosa 0, nastepuje czyszczenie tablic
            for i, detail in enumerate(self.fall_details):
                if self.fall_animation[i] > 0:
                    detail[0].fall(0, detail[2])
                    detail[1].fall(0, -detail[2])
                    self.fall_animation[i] -= self.dt / 2
                if self.fall_animation[-1] <= 0:
                    self.fall_animation = []
                    self.fall_details = []

        def refill():
            """
            this method is used for refill animation, it works only on new "generated tiles" not
             tiles already on the board
            @return:
            """
            # animacja uzupelniania nowych klockow
            for i, detail in enumerate(self.refill_details):
                if self.refill_animation[i] > 0:
                    detail[0].fall(0, detail[1])
                    self.refill_animation[i] -= self.dt / 2
                if self.refill_animation[-1] <= 0:
                    self.refill_animation = []
                    self.refill_details = []

        # wybor animacji w zaleznosci czy jest match
        if switch_animation:
            if switch_animation[0] == 1 and switch_animation[1] > 0:
                normal()
            elif switch_animation[0] == 2 and switch_animation[1] > 0:
                revert()

        if fall_animation:
            fall()
        else:
            refill()

    def draw(self, display):
        """
        draw method for the Board class, it draws the board background and the individual tiles
        @param display:
        @return:
        """
        # rysowanie tla
        display.blit(self.background, (0, 0))
        # rysowanie biezacej zawartosci tablicy
        for tile in self.board:
            display.blit(tile.tile_type, tile.tile_position)


class Tiles(pygame.sprite.Sprite):
    def __init__(self, tile_type, size, images, dt, color):
        """
        initialize the tile object, setting the image of a tile and it's coordinates
        @param tile_type:
        @param size:
        @param images:
        @param dt:
        @param color:
        """
        pygame.sprite.Sprite.__init__(self)
        self.images = images
        # stworzenie obiektu surface i rect
        self.tile_position = pygame.Surface(size)
        self.tile_position = self.tile_position.get_rect()
        self.tile_type = tile_type
        self.color = color
        self.cycle = 0
        self.dt = dt

    def update(self, move_x, move_y):
        """
        method used to animate the tiles in conjunction with the board animation methods
        @param move_x:
        @param move_y:
        @return:
        """
        if move_x != 0:
            self.tile_position.x += (move_x / abs(move_x)) * self.dt
        if move_y != 0:
            self.tile_position.y += (move_y / abs(move_y)) * self.dt

    def fall(self, move_x, move_y):
        """
        also an animation method but only used for the falling animation
        @param move_x:
        @param move_y:
        @return:
        """
        if move_x != 0:
            self.tile_position.x += (move_x / abs(move_x)) * self.dt / 2
        if move_y != 0:
            self.tile_position.y += (move_y / abs(move_y)) * self.dt / 2

    def update_image(self, image, angle):
        """
        a method used to change the shape, image and potentially other characteristics of a tile
        it is used for example to rotate the tile on click
        @param image:
        @param angle:
        @return:
        """
        self.tile_type = image
        if self.cycle == 0:
            self.tile_type = pygame.transform.rotate(image, angle)
            self.cycle = 1
        elif self.cycle > 0:
                self.cycle += 1
                if self.cycle == 10:
                    self.cycle = 0


class Gui(object):
    def __init__(self, font, display):
        """
        a prototype Gui class not yet finished, in the future it will display various objects such as player, enemy
        hp bars and portraits, different buttons etc. for now it is used to show the score and the ending text
        @param font:
        @param display:
        """
        self.font = font
        self.display = display
        self.menubutton = False
        self.mute_music = False
        self.mute_sound = False
        self.score = 0
        self.max_score = 10000
        self.player_hp = 0
        self.enemy_hp = 0

    def get_score(self, points, max_score):
        """
        method to update the score
        @param points:
        @param max_score:
        @return:
        """
        self.score += points
        self.max_score = max_score

    def events(self):
        self.draw()

    def draw(self):
        """
        drawing method for the Gui class, used to draw the score and end text
        @return:
        """
        def end_screen():
            text = self.font.render("Congratulations you won!", True, (0, 0, 0))
            self.display.blit(text, (200, 300))

        # def main_menu():
        #     pass

        if self.score < 10000:
            score = self.font.render("Your score: {} / {}".format(self.score, self.max_score), True, (0, 0, 0))
            self.display.blit(score, (150, 600))
        else:
            end_screen()

if __name__ == '__main__':
    Game().loop()
