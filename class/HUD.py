import pygame
import mapLoader
from os.path import join
import os
import time
from itertools import cycle


class HUD():
    def __init__(self, game):
        """
        Initializes HUD. Sets default values and loads images for blitting.
        """
        self.game = game

        #chat bar setup
        self.chat_active = 0
        self.text_active = []
        self.body_text = [False, False, False]
        self.prompt_result = 0
        self.chat_message = ''
        self.chat_toggle = cycle(reversed(range(2)))
        self.chat_bar = pygame.Surface([850, 20])
        self.chat_bar.fill((32, 32, 32))
        self.chat_bar.set_alpha(201)

        #daytime state
        self.screen_cover = pygame.Surface(self.game.screen_res)
        self.screen_cover.set_alpha(128)
        self.screen_cover.fill((255, 255, 255))
        self.daytime_start = time.time()
        self.daytime = 0
        self.outside_alpha = 0

        #Map change vars
        self.sheet = pygame.Surface(self.game.screen_res).convert()
        self.sheet.fill(0)
        self.sheet_alpha = 1
        self.fading = False

        self.xpbar = pygame.image.load(join(self.game.main_path, 'rec', 'gui', 'xpbar.png')).convert_alpha()
        self.hpbar = pygame.image.load(join(self.game.main_path, 'rec', 'gui', 'hpbar.png')).convert_alpha()
        self.text_box = pygame.image.load(join(self.game.main_path, 'rec', 'gui', 'text_box.png')).convert_alpha()

        self.items = [f.split('.')[0] for f in os.listdir(join(self.game.main_path, 'rec', 'items'))]
        self.monsters = os.listdir(join(self.game.main_path, 'rec', 'entity'))

    def processCommand(self, message):
        """
        Processes a chat command and spawns an item or monster accordingly.
        """
        if message.startswith("/"):
            # meant to be a command
            message = message.replace('-', '_')
            command = message.split(" ")
            if 'spawn' in message:
                self.game.Monster(self.game, command[1], self.game.unoff(list(pygame.mouse.get_pos())), 1)
            elif 'place' in message:
                self.game.Item(self.game, command[1], self.game.unoff(list(pygame.mouse.get_pos())), world=1)
            elif 'get' in message:
                self.game.Invent.add(command[1], self.game.Invent.nextFreeSlot())
            elif 'map' in message:
                self.game.blit_list = mapLoader.load(command[1], self.game)

    def makePrompt(self, npc_text):
        """
        Create a text prompt. Used when talking to NPCs.
        """
        self.npc_text = npc_text
        self.text_active = []
        self.body_text = [False, False, False]
        self.text_rects = []
        self.text_content = []

        body_text = npc_text.getText(npc_text.current_branch)
        body_render = self.game.speak_font.render(body_text, True, (255, 255, 255))
        self.body_text[0] = body_render
        self.body_text[1] = body_text
        self.body_text[2] = pygame.Rect(body_render.get_rect())
        self.body_text[2].x = 150
        self.body_text[2].y = 400

        options = npc_text.getOptions(npc_text.current_branch)
        self.thumb = npc_text.npc.thumbnail
        for op_no, option in enumerate(options):
            if npc_text.getLabel(option):
                option_text = str(op_no + 1) + ': ' + npc_text.getLabel(option)
                option_render = self.game.speak_font.render(option_text, True, (255, 255, 255))
                self.text_rects.append(option_render.get_rect())
                self.text_active.append(option_render)
                self.text_content.append(option_text)

    def showPrompt(self):
        """
        Shows prompts created by makePrompt()
        """
        text_pos = [150, 400]
        self.game.screen.blit(self.body_text[0], text_pos)
        text_pos[1] += self.body_text[0].get_rect().height
        for index, text in enumerate(self.text_active):
            text_pos[1] += self.text_active[0].get_rect().height
            self.text_rects[index] = self.game.screen.blit(text, text_pos)
        self.promptCollide()

    def delPrompt(self):
        """
        Takes all steps necessary to remove the prompt
        """
        self.text_active = []
        self.body_text = [False, False, False]

    def promptCollide(self):
        """
        Tests for mouse collisions with prompt text.
        """
        mpos = pygame.mouse.get_pos()
        for index, text_rect in enumerate(self.text_rects):
            if text_rect.collidepoint(mpos):
                self.text_active[index] = self.game.speak_font.render(self.text_content[index], True, (75, 90, 210))
                if pygame.mouse.get_pressed()[0]:
                    self.npc_text.pickOption(index)
                    break
            else:
                self.text_active[index] = self.game.speak_font.render(self.text_content[index], True, (255, 255, 255))

    def updateMapTrans(self):
        self.sheet.set_alpha(self.sheet_alpha)
        self.game.screen.blit(self.sheet, (0,0))
        self.game.Player.can_move = 0

        if not self.fading:
            self.sheet_alpha += 8
            if self.sheet_alpha > 270:
                self.fading = True
                mv = self.game.Player.map_vars
                self.game.blit_list =  mapLoader.load(mv[2], self.game, new_pos = mv[3], face = mv[4])
        else:
            self.sheet_alpha -= 8
            if self.sheet_alpha <= 0:
                self.fading = self.game.Player.map_change = False
                self.sheet_alpha = self.game.Player.can_move = 1


    def updateDay(self):
        self.daytime = time.time() - self.daytime_start
        if self.game.shadows:
            if self.daytime < 600:
                self.screen_cover.set_alpha(0)
            # full
            elif self.daytime > 900:
                self.screen_cover.set_alpha(180 - self.daytime + 900)
                if self.daytime >= 1080:
                    self.daytime_start = time.time()
            # decreasing
            elif self.daytime > 780:
            # night
                 pass
            elif self.daytime >= 600:
            # increasing
                self.screen_cover.fill((0, 0, 0))
                self.screen_cover.set_alpha(self.daytime - 600)

    def blitHUD(self):
        """
        Blits all HUD elements to the screen object
        """
        #blit self.daytime cover
        self.game.screen.blit(self.screen_cover, [0, 0])

        #hp bar creation
        blit_surface = pygame.Surface((abs(392 * (float(self.game.Player.stats['hp']) / self.game.Player.stats['maxhp'])), 24), pygame.SRCALPHA)
        blit_surface.fill((234, 0, 0, 213))
        self.game.screen.blit(blit_surface, (254, 589))

        for monster in self.game.EntityHandler.monsters:
            if monster.NPC == True and monster.interacting == True:
                self.game.screen.blit(self.text_box, [30, 350])
                self.game.screen.blit(self.thumb,[40, 360])

        #xp bar(s)
        blit_surface = pygame.Surface((497 * (float(self.game.Player.stats['mxp']) / self.game.Player.stats['maxmxp']), 12), pygame.SRCALPHA)
        blit_surface.fill((72, 196, 19, 221))
        self.game.screen.blit(blit_surface, (201, 636))
        blit_surface = pygame.Surface((497 * (float(self.game.Player.stats['pxp']) / self.game.Player.stats['maxpxp']), 12), pygame.SRCALPHA)
        blit_surface.fill((229, 102, 18, 221))
        self.game.screen.blit(blit_surface, (201, 622))

        self.game.screen.blit(self.xpbar, [200, 636])
        self.game.screen.blit(self.xpbar, [200, 622])
        self.game.screen.blit(self.hpbar, [250, 585])

        if self.chat_active:
            #blit the chat bar
            self.game.screen.blit(self.chat_bar, (25, 625))
            self.game.screen.blit(self.game.default_font.render(self.chat_message, True, (255, 255, 255)), [30, 628])

        if self.text_active or self.body_text[0]:
            self.showPrompt()