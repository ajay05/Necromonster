import sys
sys.path.append('class')

from globals import *
from player import *

class Necro():
    def __init__(self):
        self.Player = Player(self)
        # initiate the clock and screen
        self.clock = pygame.time.Clock()
        self.last_tick = pygame.time.get_ticks()
        self.screen_res = [900, 650]
        self.screen = pygame.display.set_mode(self.screen_res, 0, 32)
        self.DEBUG = 1

        # load fonts
        self.default_font = pygame.font.SysFont(None, 20)

        # get the map that you are on
        self.blit_list = mapLoader.load('home', self)

        while 1:
            self.Loop()

    def Loop(self):
        # main game loop
        self.eventLoop()
        if pygame.time.get_ticks() - self.last_tick > 20:
            self.Tick()
            self.Draw()
        pygame.display.update()

    def eventLoop(self):
        # the main event loop, detects keypresses
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()

    def Tick(self):
        # updates to player location and animation frame
        self.keys_pressed = pygame.key.get_pressed()
        self.clock.tick()
        self.Player.update()

        self.last_tick = pygame.time.get_ticks()

    def off(self, coords):
        newx = coords[0] - self.Player.player_r.x + 450
        newy = coords[1] - self.Player.player_r.y + 325
        return [newx, newy]

    def Draw(self):
        tile_width = self.tile[1][0]
        tile_height = self.tile[1][1]
        tile_extrax = self.Player.player_r.x % tile_width
        tile_extray = self.Player.player_r.y % tile_height
        y = 0

        for i in xrange(self.screen_res[1] / tile_height + 3):
            for i in xrange(self.screen_res[0] / tile_width + 3):
                self.screen.blit(self.tile[0], [i * tile_width - tile_width - tile_extrax, y - tile_height - tile_extray])
            y += self.tile[1][1]
        for surf in self.blit_list:
            if 'player' in surf:
                self.Player.blitPlayer()
            else:
                self.screen.blit(surf[0], self.off(surf[1]))
        if self.DEBUG:
            self.screen.blit(self.default_font.render(str(round(self.clock.get_fps())), True, (255, 255, 255)), [0, 0])
            self.screen.blit(self.default_font.render(str('%s, %s' % (self.Player.player_r.x, self.Player.player_r.y)), True, (255, 255, 255)), [0, 12])

Necro()