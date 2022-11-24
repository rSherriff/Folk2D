from math import ceil

import tcod
from actions.actions import CloseNotificationDialog
from ui.notification_ui import NotificationUI

from sections.section import Section
from sections.section_layouts import notification_dialog_info

class Notification(Section):
    def __init__(self, engine, x: int, y: int, width: int, height: int, name:str):
        super().__init__(engine, x, y, width, height, "buttons.xp", name)

        self.text = ""
        
    def setup(self, text, section):
        self.text = text

        self.render_width = min(len(self.text), notification_dialog_info["max_width"]) 
        self.render_height = ceil(len(self.text) / self.render_width)
        self.render_width += 4
        self.render_height += 8
        
        self.render_width += self.width % 2

        self.render_width = max(self.render_width, (notification_dialog_info["button_width"] * 2) + 7)

        self.x = int(self.width / 2) - int(self.render_width / 2)
        self.y = int(self.height / 2) - int(self.render_height / 2)
        self.render_x = self.x
        self.render_y = self.y

        close_action = CloseNotificationDialog(self.engine, section)

        self.ui = NotificationUI(self, self.x, self.y, self.button_x(), self.button_y(), notification_dialog_info["button_width"], notification_dialog_info["button_height"])
        button_mask = [[False,False,False,False,False,False,False],[False,True,True,True,True,True,False,],[False,False,False,False,False,False,False,]]
        self.ui.reset(close_action, button_mask)


    def render(self, console):
        self.draw_dialog(console)
        self.draw_button(console, x=self.x+self.button_x(),y=self.y+self.button_y(), text="CLOSE")

        self.render_ui(console) 

    def draw_dialog(self, console):
        console.draw_frame(x=self.render_x,y=self.render_y,width=self.render_width,height=self.render_height, decoration=notification_dialog_info["dialog_decoration"], bg=(0,0,0), fg=(255,255,255))
        console.print_box(x=self.render_x+1,y=self.render_y+2,width=self.render_width-2,height=self.render_height-2,string=self.text,alignment=tcod.CENTER, bg=(255,255,255), fg=(0,0,0))

    def draw_button(self, console, x, y, text):
        console.draw_frame(x=x,y=y,width=notification_dialog_info["button_width"],height=notification_dialog_info["button_height"], decoration=notification_dialog_info["button_decoration"], bg=notification_dialog_info["b_bg_color"], fg=notification_dialog_info["b_fg_color"])
        console.print_box(x=x+1,y=y+1,width=notification_dialog_info["button_width"]-2,height=notification_dialog_info["button_height"]-2,string=text,alignment=tcod.CENTER, bg=notification_dialog_info["b_font_bg_color"], fg=notification_dialog_info["b_font_fg_color"])


    def button_x(self):
        half_width = int(self.render_width / 2)
        return half_width-int(notification_dialog_info["button_width"]/2)

    def button_y(self):
        return self.render_height - notification_dialog_info["button_height"] - 2
