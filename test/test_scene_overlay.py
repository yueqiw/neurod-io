from scene import *
import ui, os
import sys
sys.path.append(os.path.abspath('../'))
from game_menu import MenuScene, ButtonNode
from objc_util import ObjCInstance, ObjCClass
from objc_util import *
import ctypes

A = Action
rec_filepath = '../data/530958091/natural_movie_one_38757-39661.mp4'
html_path = "../"

w, h = ui.get_window_size()
frame = (0,0,w,h)

glClearColor = c.glClearColor
glClearColor.restype = None
glClearColor.argtypes = [c_float, c_float, c_float, c_float]
glClear = c.glClear
glClear.restype = None
glClear.argtypes = [c_uint]
GL_COLOR_BUFFER_BIT = 0x00004000

def replace_str(text, dic):
    for x in dic:
        text = text.replace(x, str(dic[x]))
    return text

class Game(Scene):
    def __init__(self, movie):
        self.movie = movie 
        
    def setup(self):
        self.root_node = Node(parent=self)
        objv = ObjCInstance(self.view)
        objv.glkView().setOpaque_(False)
        
        self.highscore = 0
        self.run_action(A.sequence(A.wait(2), A.call(self.initialize),
                        A.call(self.show_start_menu)))

    def initialize(self):
        self.movie.eval_js("initVideo(rec);")

    def touch_began(self, touch):
        self.movie.eval_js('rec.play();')
    
    #def did_change_size(self):
    #    self.movie.frame = (self.size.w/2 - self.movie_w/2, self.size.h/2 - self.movie_h/2, \
    #                        self.movie_w, self.movie_h)
    
    def show_start_menu(self):
        self.paused = True
        self.menu = MenuScene('Match3', 'Highscore: %i' % self.highscore, ['New Game'])
        #self.root_node.add_child(self.menu)
        self.present_modal_scene(self.menu)
    
    def draw(self):
        glClearColor(0,0,0, 0)
        glClear(GL_COLOR_BUFFER_BIT)

def setup_view():
    movie = ui.WebView()
    
    movie_filepath = "file://" + os.path.abspath(rec_filepath)
    #print(rec_filepath)
    #print(self.size.w, self.size.h)
    movie_w, movie_h = 512, 768
    html_dic = {'{{VID_FPATH}}': movie_filepath, '{{VID_NAME}}': 'recording', \
                    '{{VID_WIDTH}}': movie_w, '{{VID_HEIGHT}}': movie_h}
    html_file = os.path.join(os.path.abspath(html_path), 'webview.html')
    with open(html_file) as f:
        HTML_TEMPLATE = f.read()
    movie_html = replace_str(HTML_TEMPLATE, html_dic)
    #print(movie_html)
    
    movie = ui.WebView(name='movie')
    movie.scales_page_to_fit = False
    
    game = SceneView()
    game.frame = (0,0,1000,400)
    game.scene = Game(movie)
    game.frame_interval = 2
    game.shows_fps = True
    game.scene.fixed_time_step = True

    game.add_subview(movie)
    movie.load_html(movie_html)
    
    #print(v.bounds)
    
    movie.frame = (game.width/2 - movie_w/2, 0, \
                        movie_w, movie_h)
    movie.touch_enabled = False
    #objgameview = ObjCInstance(game)
    #objgameview.bringSubviewToFront(objgameview.glkView())
    movie.send_to_back()
    game.present('full_screen', hide_title_bar=True)

                        
if __name__ == '__main__':
    setup_view()
    