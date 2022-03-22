import pygame as pg
from Vector import Vector
from pygame.sprite import Sprite, Group
from copy import copy
from random import randint
from timer import CommandTimer
from ship import Ship
# from alien import Alien
# from stats import Stats


class Barriers:
    def __init__(self, game):
        self.game = game
        self.alien_fleet = game.alien_fleet
        self.barriers = Group()
        for n in range(4):
            self.create_barrier(n)

    def update(self):
        for barrier in self.barriers:
            barrier.update()

    def draw(self):
        for barrier in self.barriers:
            barrier.draw()

    def create_barrier(self, n):
        for i in range(n):
            spacing = 400 + 100 * i
            barrier = Barrier(game=self.game, ul=(spacing, 600), wh = (3, 3))
            self.barriers.add(barrier)

class Barrier(Sprite):
    def __init__(self, game, ul, wh):
        super().__init__()
        self.img_list=[pg.image.load(
            f'images/barrier_{n}.png') for n in range(3)]
        self.game=game
        self.barrier_elements=Group()
        self.ship = game.ship
        self.ul=ul
        self.wh=wh
        self.rect = pg.Rect(ul[0], ul[1], wh[0], wh[1])
        self.create_barrier_elements()
        self.lasers = game.alien_lasers.lasers
        

    def update(self):
        collisions = pg.sprite.groupcollide(self.barrier_elements, self.lasers, False, True)
        for be in collisions:
            be.hit()
        
    
    def draw(self):
        for be in self.barrier_elements:
            be.draw()
    
    def create_barrier_elements(self):
        for row in range(3):
            for col in range(3):
                be=BarrierElement(game = self.game, img_list = self.img_list, ul = (
                    self.ul[0] + col, self.ul[1] + row), wh = (1, 1))
                self.barrier_elements.add(be)

class BarrierElement(Sprite):
    def __init__(self, game, img_list, ul, wh):
        super().__init__()
        self.ship = game.ship
        self.lasers = self.ship.lasers
        self.ul=ul
        self.wh=wh
        self.rect = pg.Rect(ul[0], ul[1], wh[0], wh[1])
        self.timer=CommandTimer(image_list = img_list, is_loop = False)
        self.screen=game.screen

    def update(self): pass
        

    def hit(self):
        print("hit")
        self.timer.next_frame()
        if self.timer.is_expired():
            self.kill()
    
    def draw(self):
        image=self.timer.image()
        rect=image.get_rect()
        rect.x, rect.y= self.ul[0], self.ul[1]
        self.screen.blit(image, rect)
