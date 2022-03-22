
from venv import create
import pygame as pg
from Vector import Vector
from laser import Lasers
from pygame.sprite import Sprite, Group
from timer import Timer
from random import randint
import random




class AlienFleet:
    alien_exploding_images = [pg.image.load(f'images/explosion_0{n}.png') for n in range(8)]
    alien_one_imgs = [pg.image.load(f'images/Alien1_{n}.png') for n in range(2)]
    alien_two_imgs = [pg.image.load(f'images/Alien2_{n}.png') for n in range(2)]
    alien_three_imgs = [pg.image.load(f'images/Alien3_{n}.png') for n in range(2)]
    ufo_imgs = [pg.image.load(f'images/Alien4_{n}.png') for n in range(2)]
    score_imgs = [pg.image.load(f'images/100_{n}.png') for n in range(2)]

    def __init__(self, game, v=Vector(1, 0)):
        self.game = game
        self.ship = self.game.ship
        self.settings = game.settings
        self.screen = self.game.screen
        self.screen_rect = self.screen.get_rect()
        self.v = v

        self.alien_one = Alien(game=game, image_list=AlienFleet.alien_one_imgs, v=Vector(), points=10)
        self.alien_two = Alien(game=game, image_list=AlienFleet.alien_two_imgs, v=Vector(), points=20)
        self.alien_three = Alien(game=game, image_list=AlienFleet.alien_three_imgs, v=Vector(), points=40)
        self.ufo = UFO(game=game, ul=(400, 50), image_list=AlienFleet.ufo_imgs, v=self.v, points = 100)

        self.aliens = [self.alien_one, self.alien_two, self.alien_three]

        self.alien_w = pg.image.load("images/Alien1_0.png").get_rect().width
        self.alien_h = pg.image.load("images/Alien1_0.png").get_rect().height
        self.lasers = None

        self.center = Vector(0,0)

        self.fleet = Group()
        self.create_fleet()


    def create_fleet(self):
        self.fleet.add(UFO(game=self.game, ul=(400, 50), v=Vector(1, 0), image_list=AlienFleet.ufo_imgs, points=100))
        row = 0
        i = 0
        while row < 6:
            self.create_row_of_aliens(row, self.aliens[i])
            row+=1
            if row%2 == 0:
                i+=1

    def set_lasers(self, lasers):
        self.lasers = lasers

    def get_random_location(self):
        random_alien = random.randint(0, len(self.fleet) - 1)
        self.center = self.fleet.sprites()[random_alien].center

    def create_row_of_aliens(self, row, alien):
        for col in range(8):
            self.create_alien(row, col, alien)

    def create_alien(self, row, col, alien):
        x = self.alien_w * (1.2 * col + 1)
        y = 50 + self.alien_h * (0.8 * row + 1)

        alien = Alien(game=self.game, ul=(x, y), v=self.v, image_list=alien.image_list, points=alien.points)
        self.fleet.add(alien)


    def set_ship(self, ship): self.ship = ship

    def empty(self): self.fleet.empty()

    def empty_lasers(self):
        for alien in self.fleet:
            alien.empty_lasers()

    def length(self): return len(self.fleet.sprites())

    def change_v(self, v):
        for alien in self.fleet.sprites():
            alien.change_v(v)

    def check_bottom(self):
      for alien in self.fleet.sprites():
        if alien.check_bottom():
            self.ship.hit()
            break

    def check_edges(self):
      for alien in self.fleet.sprites():
        if alien.check_edges() and type(alien) is Alien:
            return True
      return False

    def update(self):
        delta_s = Vector(0, 0)    # don't change y position in general
        if self.check_edges():
            self.v.x *= -1
            self.change_v(self.v)
            delta_s = Vector(0, self.settings.fleet_drop_speed)
        if pg.sprite.spritecollideany(self.ship, self.fleet) or self.check_bottom():
            if not self.ship.is_dying(): self.ship.hit()
        for alien in self.fleet.sprites():
            alien.update(delta_s=delta_s)
        self.get_random_location()
        if random.randint(0, 100) < 1:
            self.lasers.fire()

    def draw(self):
        for alien in self.fleet.sprites():
            alien.draw()


class Alien(Sprite):
    def __init__(self, game, image_list, start_index=0, ul=(0, 100), v=Vector(1, 0),
                 points=1211):
        super().__init__()
        self.game = game
        self.screen = game.screen
        self.settings = game.settings
        self.points = points
        self.stats = game.stats

        self.image = pg.image.load('images/Alien1_0.png')
        self.screen_rect = self.screen.get_rect()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = ul
        self.ul = Vector(ul[0], ul[1])   # position
        self.v = v                       # velocity
        self.image_list = image_list
        self.exploding_timer = Timer(image_list=AlienFleet.alien_exploding_images, delay=200,
                                     start_index=start_index, is_loop=False)
        self.normal_timer = Timer(image_list=image_list, delay=1000, is_loop=True)
        self.timer = self.normal_timer
        self.dying = False
        self.center = Vector(0,0)


    def change_v(self, v): self.v = v
    def check_bottom(self): return self.rect.bottom >= self.screen_rect.bottom
    def check_edges(self):
        r = self.rect
        return r.right >= self.screen_rect.right or r.left <= 0


    def hit(self):
        self.stats.alien_hit(alien=self)
        self.timer = self.exploding_timer
        self.dying = True

    def empty_lasers(self):
        self.lasers.empty()

    def update(self, delta_s=Vector(0, 0)):
        if self.dying and self.timer.is_expired():
          self.kill()
        self.ul += delta_s
        self.ul += self.v * self.settings.alien_speed_factor
        self.rect.x, self.rect.y = self.ul.x, self.ul.y
        self.center = self.ul



    def draw(self):
      image = self.timer.image()
      rect = image.get_rect()
      rect.x, rect.y = self.rect.x, self.rect.y
      self.screen.blit(image, rect)
      # self.screen.blit(self.image, self.rect)

class UFO(Sprite):
    def __init__(self, game, image_list, start_index=0, ul=(0, 100), v=Vector(1, 0), points=1211):
        super().__init__()
        self.game = game
        self.screen = game.screen
        self.settings = game.settings
        self.points = points
        self.stats = game.stats

        self.image = pg.image.load('images/Alien4_0.png')
        self.screen_rect = self.screen.get_rect()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = ul
        self.ul = Vector(ul[0], ul[1])
        self.v = v
        self.image_list = image_list
        self.exploding_timer = Timer(image_list=AlienFleet.score_imgs, delay=10, start_index=start_index, is_loop=False)
        self.normal_timer = Timer(image_list=image_list, delay=1000, is_loop=True)
        self.timer = self.normal_timer
        self.dying = False

        self.center = Vector(0,0)

    def change_v(self, v): pass


    def check_bottom(self):
        return self.rect.bottom >= self.screen_rect.bottom

    def check_edges(self):
        r = self.rect
        return r.right >= self.screen_rect.right or r.left <= 0

    def hit(self):
        self.stats.alien_hit(alien=self)
        self.timer = self.exploding_timer
        self.dying = True

    def update(self, delta_s):
        if self.check_edges() or random.randrange(0, 150) < 1:
            self.v *=-1
        if self.dying and self.timer.is_expired():
            self.kill()
        self.ul += self.v * self.settings.UFO_speed_factor
        self.rect.x, self.rect.y = self.ul.x, self.ul.y
        self.center = self.ul

    def draw(self):
      image = self.timer.image()
      rect = image.get_rect()
      rect.x, rect.y = self.rect.x, self.rect.y
      self.screen.blit(image, rect)


