from scene import *
import ui, os
from game_menu import MenuScene, ButtonNode
from objc_util import *
import ctypes
A = Action
rec_filepath = './data/530958091/natural_movie_one_38757-39661.mp4'
html_path = "./"


def replace_str(text, dic):
    for x in dic:
        text = text.replace(x, str(dic[x]))
    return text


class Game(Scene):
    def __init__(self, movie_view):
        Scene.__init__(self)
        self.movie = movie_view

    def setup(self):
        self.setup_clear_color()
        self.root_node = Node(parent=self)
        objv = ObjCInstance(self.view)
        objv.glkView().setOpaque_(False)
        #self.movie.frame = (self.size.w/2 - self.movie_w/2, self.size.h/2 - self.movie_h/2, \
        #                    self.movie_w, self.movie_h)

        self.highscore = 0
        #print(self.paused)
        self.run_action(A.sequence(A.wait(0.1), A.call(self.movie_init), \
                        A.wait(1),  A.call(self.show_start_menu)))
        self.add_helper_buttons()
        #self.did_change_size()

    def setup_clear_color(self):
        self.glClearColor = c.glClearColor
        self.glClearColor.restype = None
        self.glClearColor.argtypes = [c_float, c_float, c_float, c_float]
        self.glClear = c.glClear
        self.glClear.restype = None
        self.glClear.argtypes = [c_uint]
        self.GL_COLOR_BUFFER_BIT = 0x00004000

    def clear_background(self):
        self.glClearColor(0,0,0,0)
        self.glClear(self.GL_COLOR_BUFFER_BIT)
    
    def new_game(self):
        self.score = 0
        self.start_time = self.t
        self.paused = False
        self.movie_play()

    def movie_init(self):
        self.movie.eval_js("initVideo(rec);")
    
    def movie_play(self):
        self.movie.eval_js('rec.play();')
    
    def movie_pause(self):
        self.movie.eval_js("rec.pause();")
    
    def did_change_size(self):
        self.movie.frame = (self.size.w/2 - self.movie_w/2, self.size.h/2 - self.movie_h/2, \
                            self.movie.width, self.movie.height)

    def show_start_menu(self):
        self.paused = True
        self.menu = MenuScene('Match3', 'Highscore: %i' % self.highscore, ['New Game'])
        #self.menu.view.bring_to_front()
        self.present_modal_scene(self.menu)

    def button_pause(self, sender):
        self.movie_pause()

    def button_play(self, sender):
        self.movie_play()

    def button_init(self, sender):
        self.movie_init()

    def touch_began(self, touch):
        print touch.location
        # need to add scale factor

        if self.paused is True:
            self.paused = False

        self.movie.eval_js('update_t();')
    def draw(self):
        self.clear_background()
        #if self.game_end is True:
        #    self.draw_frame()
        #    return
        self.draw_frame()

        #self.img_idx += 1
        #if self.img_idx >= self.nframe:
        #    self.img_idx = self.nframe - 1
        #    self.game_end = True
        #    self.paused = True
            #self.empty_cache()

    def draw_frame(self):
        pass
        #currTime = self.movie.eval_js('document.getElementById("recording").currentTime')
        #print currTime
    
    
    def menu_button_selected(self, title):
        if title in ('Continue', 'New Game'):
            self.dismiss_modal_scene()
            self.menu = None
            self.paused = False
            if title == 'New Game':
                self.new_game()

    def add_helper_buttons(self):
        self.button1 = ui.Button(title='initialize')
        self.button1.action = self.button_init
        self.button1.frame = (20,50,50,50)
        self.view.add_subview(self.button1)
        self.button2 = ui.Button(title='play')
        self.button2.action = self.button_play
        self.button2.frame = (20,100,50,50)
        self.view.add_subview(self.button2)
        self.button3 = ui.Button(title='pause')
        self.button3.action = self.button_pause
        self.button3.frame = (20,150,50,50)
        self.view.add_subview(self.button3)

def setup_view():
    w, h = ui.get_window_size()
    frame = (0,0,w,h)

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
    movie.background_color = None
    movie.scales_page_to_fit = False
    movie.touch_enabled = False

    game = SceneView()
    game.frame = frame
    game.scene = Game(movie)
    game.frame_interval = 2
    game.shows_fps = True
    game.scene.fixed_time_step = True

    game.add_subview(movie)
    movie.load_html(movie_html)

    #print(v.bounds)

    movie.frame = (game.width/2 - movie_w/2, game.height/2 - movie_h/2, \
                        movie_w, movie_h)
    movie.touch_enabled = False
    #objgameview = ObjCInstance(game)
    #objgameview.bringSubviewToFront(objgameview.glkView())
    movie.send_to_back()
    game.present('full_screen', hide_title_bar=True)


if __name__ == '__main__':
    setup_view()

