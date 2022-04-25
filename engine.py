from __future__ import annotations

import json
import os
import random
from enum import Enum, auto
from threading import Timer

import tcod
from playsound import playsound
from pygame import mixer
from tcod.console import Console

from application_path import get_app_path
from effects.melt_effect import MeltWipeEffect, MeltWipeEffectType
from fonts.font_manager import FontManager
from input_handlers import EventHandler, MainGameEventHandler
from sections.confirmation import Confirmation
from sections.intro_section import IntroSection
from utils.delta_time import DeltaTime


class GameState(Enum):
    INTRO = auto()
    MENU = auto()
    IN_GAME = auto()
    GAME_OVER = auto()
    COMPLETE = auto()


class Engine:
    def __init__(self, teminal_width: int, terminal_height: int):

        self.debug_music_disabled = True

        mixer.init()
        if not self.debug_music_disabled:
            mixer.music.set_volume(0.5)
        else:
             mixer.music.set_volume(0)

        self.screen_width = teminal_width
        self.screen_height = terminal_height
        self.delta_time = DeltaTime()

        self.player = None

        self.event_handler: EventHandler = MainGameEventHandler(self)
        self.mouse_location = (0, 0)

        self.setup_effects()
        self.setup_sections()

        self.tick_length = 2
        self.time_since_last_tick = -2

        self.state = GameState.INTRO

        self.font_manager = FontManager()
        #self.font_manager.add_font("number_font")

        self.in_stage_music_queue = False

        self.save_data = None
        if os.path.isfile("game_data/game_save.json"):
            with open("game_data/game_save.json") as f:
                self.save_data = json.load(f)
        else:
            self.save_data = dict()

        with open ( "game_data/levels.json" ) as f:
            data = json.load(f)

            self.intro_sections["introSection"].load_splashes(data["intro_splashes"])

    def render(self, root_console: Console) -> None:
        """ Renders the game to console """
        for section_key, section_value in self.get_active_sections():
            if section_key not in self.disabled_sections:
                section_value.render(root_console)

        if self.state == GameState.IN_GAME or self.state == GameState.GAME_OVER:
            for entity in self.entities:
                root_console.print(entity.x, entity.y,
                                   entity.char, fg=entity.color)

        if self.full_screen_effect.in_effect == True:
            self.full_screen_effect.render(root_console)
        else:
            self.full_screen_effect.set_tiles(root_console.tiles_rgb)

    def update(self):
        """ Engine update tick """
        for _, section in self.get_active_sections():
            section.update()

        self.delta_time.update_delta_time()

        if self.state == GameState.IN_GAME:
            self.time_since_last_tick += self.get_delta_time()

            self.tick_length -= 0.0002
            if self.time_since_last_tick > self.tick_length and self.state == GameState.IN_GAME:
                self.time_since_last_tick = 0

            for entity in self.entities:
                entity.update()

    def handle_events(self, context: tcod.context.Context):
        self.event_handler.handle_events(context, discard_events=self.full_screen_effect.in_effect or self.state == GameState.GAME_OVER)

    def setup_game(self):
        self.player = Player(self, 7, 4)
        self.entities.clear()
        self.entities.append(self.player)
        self.tick_length = 2

    def setup_effects(self):
        self.full_screen_effect = MeltWipeEffect(self, 0, 0, self.screen_width, self.screen_height, MeltWipeEffectType.RANDOM, 40)

    def setup_sections(self):
        self.intro_sections = {}
        self.intro_sections["introSection"] = IntroSection(self,0,0,self.screen_width, self.screen_height)
        
        self.menu_sections = {}
        self.game_sections = {}
        self.completion_sections = {}

        self.disabled_sections = ["confirmationDialog", "notificationDialog"]
        self.solo_ui_section = ""

    def get_active_sections(self):
        if self.state == GameState.INTRO:
            return self.intro_sections.items()
        elif self.state == GameState.MENU:
            return self.menu_sections.items()
        elif self.is_in_game():
            return self.game_sections.items()
        elif self.state == GameState.COMPLETE:
            return self.completion_sections.items()

    def get_active_ui_sections(self):
        if self.state == GameState.INTRO:
            return dict(filter(lambda elem: elem[0] not in self.disabled_sections, self.intro_sections.items())).items()
        elif self.state == GameState.MENU:
            return dict(filter(lambda elem: elem[0] not in self.disabled_sections, self.menu_sections.items())).items()
        elif self.is_in_game():
            return dict(filter(lambda elem: elem[0] not in self.disabled_sections, self.game_sections.items())).items()
        elif self.state == GameState.COMPLETE:
            return dict(filter(lambda elem: elem[0] not in self.disabled_sections, self.completion_sections.items())).items()
    def enable_section(self, section):
        self.disabled_sections.remove(section)

    def disable_section(self, section):
        self.disabled_sections.append(section)

    def close_menu(self):
        self.state = GameState.IN_GAME
        self.setup_game()
        self.full_screen_effect.start()

    def queue_music(self, stage):
        music = self.stage_music[stage]["music"]
        volume = self.stage_music[stage]["music_volume"]
        if len(music) > 0:
            random.shuffle(music)

            if not self.debug_music_disabled:
                mixer.music.set_volume(volume)

            self.current_music_index = 0
            self.music_queue = music
            self.advance_music_queue()
            self.in_stage_music_queue = True
        
    def advance_music_queue(self):
        print("Playing: " + self.music_queue[self.current_music_index])
        mixer.music.load("sounds/music/" + self.music_queue[self.current_music_index])
        self.current_music_index += 1

        if self.current_music_index >= len(self.music_queue):
            self.current_music_index = 0

        self.play_music()

    def play_music(self):
        mixer.music.play()

    def end_music_queue(self, fadeout_time):
        mixer.music.fadeout(fadeout_time)
        self.in_stage_music_queue = False

    def play_music_file(self, file):
        if not self.in_stage_music_queue and os.path.isfile("sounds/music/" + file):
            mixer.music.load("sounds/music/" + file)
            mixer.music.play()
        else:
            print("Tried to play music that doesn't exist!  " + file)

    def play_menu_music(self, file=""):
        if len(file) > 0:
            self.menu_music = file
        if os.path.isfile("sounds/music/" + self.menu_music):
            mixer.music.load("sounds/music/" + self.menu_music)
            mixer.music.play()
        else:
            print("Tried to play music that doesn't exist!  " + self.menu_music)

    def open_menu(self):
        self.change_state(GameState.MENU)
        self.full_screen_effect.start()

    def change_state(self, new_state):
        old_state = self.state

        self.state = new_state

    def game_over(self):
        self.state = GameState.GAME_OVER
        Timer(3, self.open_menu).start()

    def complete_game(self):
        self.state = GameState.COMPLETE
        self.full_screen_effect.start()

    def get_delta_time(self):
        return self.delta_time.get_delta_time()

    def remove_entity(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)

    def play_music(self):
        return
        playsound(get_app_path() + "/sounds/music.wav", False)
        self.music_timer = Timer(77, self.play_music)
        self.music_timer.start()

    def quit(self):
        if self.music_timer.is_alive():
            self.music_timer.cancel()
        raise SystemExit()

    def open_confirmation_dialog(self, text, confirmation_action):
        self.game_sections["confirmationDialog"].setup(
            text, confirmation_action)
        self.enable_section("confirmationDialog")

    def close_confirmation_dialog(self):
        self.disable_section("confirmationDialog")

    def open_notification_dialog(self, text):
        self.game_sections["notificationDialog"].setup(text)
        self.enable_section("notificationDialog")

    def close_notification_dialog(self):
        self.disable_section("notificationDialog")

    def is_ui_paused(self):
        return self.full_screen_effect.in_effect

    def end_intro(self):
        self.change_state(GameState.MENU)
        self.full_screen_effect.start()