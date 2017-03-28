from scene import *
import ui, os
import numpy as np
from game_menu import MenuScene, ButtonNode
from objc_util import *
import ctypes
import sound
import time
A = Action
rec_filepath = './data/530958091/natural_movie_one_38757-39661.mp4'
data_filepath = './data/530958091/natural_movie_one_38757-39661/rec_data.npz'
html_path = "./"
IMG_SIZE = 512
DFF_THRESHOLD = 0.2
REWARD = 100
PENALTY = 50


def replace_str(text, dic):
    for x in dic:
        text = text.replace(x, str(dic[x]))
    return text


class Game(Scene):
    def __init__(self, movie_view):
        Scene.__init__(self)
        self.movie = movie_view

    def setup(self):
        
        self.scale = 1.0
        self.fps = 30
        self.setup_clear_background()
        #self.clear_background()
        #
        self.root_node = Node(parent=self)
        
        #self.movie.frame = (self.size.w/2 - self.movie_w/2, self.size.h/2 - self.movie_h/2, \
        #                    self.movie_w, self.movie_h)

        self.highscore = 0
        self.allow_touch = False
        self.load_data(data_filepath)
        self.run_action(A.sequence(A.wait(0.1), A.call(self.movie_init), \
                        A.wait(1),  A.call(self.show_start_menu)))
        self.add_helper_buttons()
        #self.paused = True
        self.data_ready = False
        
        print(self.data_ready)
        #self.did_change_size()
    
    #@ui.in_background
    def load_data(self, filepath):
        self.data_ready = False
        tstart = time.time()
        data = np.load(filepath)
        self.cell_specimen_ids = data['cell_specimen_ids']
        all_cell_dff = data['slice_all_dff']
        self.xy2cellids = data['xy2cellids']  # (512, 512, 3) with 3 layers for overlap ROIs
        self.list_xyones = data['list_xyones']
        self.all_cell_fire = all_cell_dff > DFF_THRESHOLD
        del all_cell_dff
        self.data_ready = True
        tend = time.time()
        print(tend - tstart)
        #print(len(self.cell_specimen_ids))
        #print(len(self.slice_all_dff))
        #print(len(self.xy2cellids))
        #print(len(self.list_xyones))

    def setup_clear_background(self):
        self.glClearColor = c.glClearColor
        self.glClearColor.restype = None
        self.glClearColor.argtypes = [c_float, c_float, c_float, c_float]
        self.glClear = c.glClear
        self.glClear.restype = None
        self.glClear.argtypes = [c_uint]
        self.GL_COLOR_BUFFER_BIT = 0x00004000
        objv = ObjCInstance(self.view)
        objv.glkView().setOpaque_(False)

    def clear_background(self):
        self.glClearColor(0,0,0,0)
        self.glClear(self.GL_COLOR_BUFFER_BIT)
    
    def scene_pause(self):
        self.paused = True

    def stop(self):
        del self.cell_specimen_ids 
        del self.slice_all_dff
        del self.xy2cellids
        del self.list_xyones
    
    def update(self):
        #update time
        #update loading
        pass
        
    def new_game(self):
        self.root_node.run_action(A.sequence(A.fade_to(0, 0.35), A.remove()))
        # remove webview
        # add webview
        # set root node
        self.score = 0
        #self.start_time = self.t
        self.paused = False
        self.allow_touch = True
        self.movie_play()
        self.start_time = self.t

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
        if self.allow_touch is False:
            return
        #print self.paused
        #self.paused = True
        x, y = touch.location
        #print x, y
        #print self.movie.frame
        time_elapsed = self.t - self.start_time
        current_time = float(self.movie.eval_js('rec.currentTime'))
        frame_idx = current_time * self.fps
        #frame_idx = int(current_time * self.fps)
        # need to add scale factor
        img_x, img_y = self.transform_touch(x, y)
        #print img_x, img_y
        
        print ""
        cell_captured = self.evaluate_touch(img_x, img_y, frame_idx)
        #print cell_captured
        self.evaluate_reward(cell_captured)
        
        print current_time
        print time_elapsed
        #print frame_idx
    
    def transform_touch(self, x, y):
        img_x = int(round((x - self.movie.x) / float(self.scale)))
        img_y = IMG_SIZE - int(round((y - self.movie.y) / float(self.scale)))
        return img_x, img_y
    
    def evaluate_touch(self, x, y, frame_idx):
        if x < 0 or y < 0 or x >= IMG_SIZE or y >= IMG_SIZE:
            return None
        print x, y
        cells_touched = self.xy2cellids[x, y]  # (3,) array, e.g. (aaaaaaa, bbbbbbb, 0)
        print cells_touched
        if not cells_touched.any():
            capture = None
        else:
            curr_fire_idx = self.all_cell_fire[:, frame_idx].nonzero()
            print frame_idx
            print curr_fire_idx
            cells_firing = self.cell_specimen_ids[curr_fire_idx]
            print cells_firing
            cells_firing_touched = np.intersect1d(cells_touched, cells_firing)
            if not cells_firing_touched.any():
                capture = None
            else:
                capture = cells_firing_touched[0]
        return capture
    
    def evaluate_reward(self, cell_id):
        if cell_id:
            self.score += REWARD
            sound.play_effect('arcade:Coin_5')
        else:
            self.score -= PENALTY
            sound.play_effect('arcade:Jump_5')
        #self.score_label.text = str(self.score)
    
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
    main_view = ui.View()
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
    main_view.add_subview(game)
    main_view.present('full_screen', hide_title_bar=True)


if __name__ == '__main__':
    setup_view()

