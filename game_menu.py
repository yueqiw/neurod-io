#import pythonista

# This file comes with the Pythonista app. 
# This module implements the menu that is used by all game examples. It doesn't do much by itself.

from scene import *
import ui
import sound
A = Action

class ButtonNode (SpriteNode):
	def __init__(self, title, *args, **kwargs):
		SpriteNode.__init__(self, 'pzl:Button1', *args, **kwargs)
		button_font = ('Helvetica', 20)
		self.title_label = LabelNode(title, font=button_font, color='#202020', position=(0, 1), parent=self)
		self.title = title

class MenuScene (Scene):
	def __init__(self, title, subtitle, button_titles, footnotes=[]):
		Scene.__init__(self)
		self.title = title
		self.subtitle = subtitle
		self.button_titles = button_titles
		self.footnotes = footnotes
		
	def setup(self):
		subtitle_font = ('Helvetica', 20)
		title_font = ('Helvetica', 36)
		footnote_font = ('Helvetica', 8)
		num_buttons = len(self.button_titles)
		num_footnotes = len(self.footnotes)
		self.bg = SpriteNode(color='black', parent=self)
		bg_shape = ui.Path.rounded_rect(0, 0, 240, num_buttons * 64 + 140 + 10 + num_footnotes * 12, 8)
		bg_shape.line_width = 3
		shadow = ((0, 0, 0, 0.35), 0, 0, 24)
		self.menu_bg = ShapeNode(bg_shape, (1,1,1,0.9), '#226DEC', shadow=shadow, parent=self)  # #15a4ff
		self.title_label = LabelNode(self.title, font=title_font, color='#226DEC', 
				position=(0, self.menu_bg.size.h/2 - 50), parent=self.menu_bg) # google blue
		self.title_label.anchor_point = (0.5, 1)
		self.subtitle_label = LabelNode(self.subtitle, font=subtitle_font, 
				position=(0, self.menu_bg.size.h/2 - 110), color='black', parent=self.menu_bg)
		self.subtitle_label.anchor_point = (0.5, 1)

		self.buttons = []
		for i, title in enumerate(reversed(self.button_titles)):
			btn = ButtonNode(title, parent=self.menu_bg)
			btn.position = 0, i * 64 - (num_buttons-1) * 32 - 45 + num_footnotes * 12 / 2
			self.buttons.append(btn)
		
		self.footnote_list = []
		for i, title in enumerate(reversed(self.footnotes)):
			ftn = LabelNode(title, font=footnote_font, color='#404040', parent=self.menu_bg)
			ftn.anchor_point = (0.5, 1)
			ftn.position = 0, i * 12 - (num_footnotes-1) * 6 - 70 - num_footnotes * 12 #- self.menu_bg.size.h/2 + i * 16 + 10
			self.footnote_list.append(ftn)

		self.did_change_size()
		self.menu_bg.scale = 0
		self.bg.alpha = 0
		self.bg.run_action(A.fade_to(0.4))
		self.menu_bg.run_action(A.scale_to(1, 0.3, TIMING_EASE_OUT_2))
		self.background_color = 'black'
		
	def did_change_size(self):
		self.bg.size = self.size + (2, 2)
		self.bg.position = self.size/2
		self.menu_bg.position = self.size/2
	
	def touch_began(self, touch):
		touch_loc = self.menu_bg.point_from_scene(touch.location)
		for btn in self.buttons:
			if touch_loc in btn.frame:
				sound.play_effect('8ve:8ve-tap-resonant')
				btn.texture = Texture('pzl:Button2')
	
	def touch_ended(self, touch):
		touch_loc = self.menu_bg.point_from_scene(touch.location)
		for btn in self.buttons:
			btn.texture = Texture('pzl:Button1')
			if self.presenting_scene and touch_loc in btn.frame:
				new_title = self.presenting_scene.menu_button_selected(btn.title)
				if new_title:
					btn.title = new_title
					btn.title_label.text = new_title

if __name__ == '__main__':
	run(MenuScene('Title', 'Subtitle', ['Foo', 'Bar', 'Baz']))
