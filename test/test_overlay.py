from objc_util import *
import time
import colorsys
from scene import *
import ui

glClearColor = c.glClearColor
glClearColor.restype = None
glClearColor.argtypes = [c_float, c_float, c_float, c_float]
glClear = c.glClear
glClear.restype = None
glClear.argtypes = [c_uint]
GL_COLOR_BUFFER_BIT = 0x00004000

class ChristmasScene(Scene):
    def setup(self):
        objv = ObjCInstance(self.view)
        objv.glkView().setOpaque_(False)
        sp = SpriteNode('emj:Christmas_Tree', anchor_point=(0,0), position=(500,300), parent=self)
        
    def draw(self):
        glClearColor(0,0,0, 0)
        glClear(GL_COLOR_BUFFER_BIT)
        
w, h = ui.get_window_size()
frame = (0,0,w,h)

webview = ui.WebView(frame=(w/4, 0, w/2, h))
webview.load_url('http://google.com')

gameview = SceneView()
gameview.scene = ChristmasScene()
gameview.add_subview(webview)
webview.send_to_back()
#objgameview = ObjCInstance(gameview)
#objgameview.bringSubviewToFront(objgameview.glkView())

gameview.present('full_screen')
print("")