from math import ceil

import tcod
from actions.actions import Action
from ui.confirmation_ui import ConfirmationUI

from sections.section import Section
from sections.section_layouts import confirmation_dialog_info

class Confirmation(Section):
    def __init__(self, engine, x: int, y: int, width: int, height: int, name:str):
        super().__init__(engine, x, y, width, height, "buttons.xp", name)

        self.text = ""
        self.ui = None
        
    def setup(self, text, confirmation_action, section, enable_ui_on_confirm):
        self.text = text

        self.render_width = min(len(self.text), confirmation_dialog_info["max_width"])
        self.render_height = ceil(len(self.text) / self.render_width)
        self.render_width += 4
        self.render_height += 10

        self.render_width += self.width % 2

        self.render_width = max(self.render_width, (confirmation_dialog_info["button_width"] * 2) + 7)

        self.x = int(self.width / 2) - int(self.render_width / 2)
        self.y = int(self.height / 2) - int(self.render_height / 2)
        self.render_x = self.x
        self.render_y = self.y

        self.ui = ConfirmationUI(self, self.x, self.y, self.positive_button_x(), self.negative_button_x(), self.button_y(), confirmation_dialog_info["button_width"],confirmation_dialog_info["button_height"])
        button_mask = [[False,False,False],[False,True,False,],[False,False,False]]
        self.ui.reset(confirmation_action, section, enable_ui_on_confirm, button_mask)

    def render(self, console):
        self.draw_dialog(console)
        self.draw_button(console, x=self.x+self.positive_button_x(),y=self.y+self.button_y(), text="Y")
        self.draw_button(console, x=self.x+self.negative_button_x(),y=self.y+self.button_y(), text="N")
       
        self.render_ui(console)

    def draw_dialog(self, console):
        console.draw_frame(x=self.render_x,y=self.render_y,width=self.render_width,height=self.render_height, decoration=confirmation_dialog_info["dialog_decoration"], bg=(0,0,0), fg=(255,255,255))
        console.print_box(x=self.render_x+1,y=self.render_y+2,width=self.render_width-2,height=self.render_height-2,string=self.text,alignment=tcod.CENTER, bg=(255,255,255), fg=(0,0,0))

    def draw_button(self, console, x, y, text):
        console.draw_frame(x=x,y=y,width=confirmation_dialog_info["button_width"],height=confirmation_dialog_info["button_height"], decoration=confirmation_dialog_info["button_decoration"], bg=confirmation_dialog_info["b_bg_color"], fg=confirmation_dialog_info["b_fg_color"])
        console.print_box(x=x+1,y=y+1,width=confirmation_dialog_info["button_width"]-2,height=confirmation_dialog_info["button_height"]-2,string=text,alignment=tcod.CENTER, bg=confirmation_dialog_info["b_font_bg_color"], fg=confirmation_dialog_info["b_font_fg_color"])

    def positive_button_x(self):
        half_width = int(self.render_width / 2)
        return half_width-confirmation_dialog_info["button_width"]-1

    def negative_button_x(self):
        half_width = int(self.render_width / 2)
        return half_width +1 + (self.render_width % 2)

    def button_y(self):
        return self.render_height - confirmation_dialog_info["button_height"] - 2
