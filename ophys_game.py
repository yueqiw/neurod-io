from scene import *
import ui, os
import numpy as np
from game_menu import MenuScene, ButtonNode
from objc_util import *
import ctypes
import sound
import time
A = Action
from config import *


def replace_str(text, dic):
    for x in dic:
        text = text.replace(x, str(dic[x]))
    return text

class Game(Scene):
    def __init__(self):
        Scene.__init__(self)
        self.mode = None

    def setup(self):
        movie_filepath = "file://" + os.path.abspath(FILEPATH + '.mp4')
        data_filepath = os.path.abspath(FILEPATH + '/rec_data.npz')
        self.set_scale()
        self.load_webview()
        self.load_movie(movie_filepath=movie_filepath, duration=30)
        self.fps = FPS
        self.setup_clear_background()
        self.movie_playing = False
        self.root_node = Node(parent=self, z_position=0.5)
        self.highscore = self.load_highscore()
        self.last_captured = -1
        self.data_ready = False
        self.load_data(data_filepath)
        self.run_action(A.sequence(A.wait(0.1), A.call(self.movie_init), \
                        A.wait(0.5),  A.call(self.show_start_menu)))
        #self.add_helper_buttons()
        self.add_buttons()
        self.did_change_size()

    def add_buttons(self):
        scoretext_font = ('Avenir Next Bold', 30)
        score_font = ('Avenir Next', 42)
        time_font = ('Avenir Next Condensed', 36)
        self.scoretext_label = LabelNode('Neuro Coins', font=scoretext_font, color='#00e20b', parent=self)
        self.scoretext_label.anchor_point = (0.5, 1)
        self.score_label = LabelNode('0', font=score_font, parent=self)
        self.score_label.anchor_point = (0.5, 1)

        self.time_label = LabelNode('00:00', font=time_font, parent=self)
        self.time_label.anchor_point = (0, 1)
        self.pause_button = SpriteNode('iow:pause_32', position=(32, self.size.h-36), parent=self)

    def set_scale(self):
        self.movie_scale = min(self.size.w / (MOVIE_W/ZOOM), self.size.h / (MOVIE_H/ZOOM))
        self.frame_w = MOVIE_W / ZOOM * self.movie_scale
        self.frame_h = MOVIE_H / ZOOM * self.movie_scale
        self.movie_w = MOVIE_W * self.movie_scale 
        self.shift_h = SHIFT_H * self.movie_scale
        self.top = TOP * self.movie_scale
        self.left = LEFT * self.movie_scale

    def did_change_size(self):
        self.set_scale()
        self.movie.frame = (self.view.width/2 - self.frame_w/2, self.view.height/2 - self.frame_h/2, \
                            self.frame_w, self.frame_h)
        self.movie.eval_js('rec.width = "' + str(self.movie_w) + '";')

        self.root_node.position = (0.0, 0.0)
        self.scoretext_label.position = (self.size.w - 110, self.size.h - 20)
        self.score_label.position = (self.size.w - 110, self.size.h - 60)
        self.time_label.position = (60, self.size.h - 10)
        self.pause_button.position = (32, self.size.h-32)

    def load_webview(self):
        self.movie = ui.WebView(name='movie')

        self.movie.background_color = None
        self.movie.scales_page_to_fit = False
        self.movie.touch_enabled = False

        self.view.add_subview(self.movie)
        objwebview = ObjCInstance(self.movie)
        objwebview.webView().allowsInlineMediaPlayback = True
        #objgameview = ObjCInstance(self.view)
        #objgameview.bringSubviewToFront(objgameview.glkView())
        self.movie.send_to_back()

    def load_movie(self, movie_filepath=None, duration=None):
        self.game_duration = 30
        self.sec_left = self.game_duration
        
        #print(rec_filepath)
        html_dic = {'{{VID_FPATH}}': movie_filepath, '{{VID_NAME}}': 'recording', \
                        '{{VID_WIDTH}}': self.movie_w, \
                        '{{VID_TOP}}': str(self.shift_h - self.top) + "px", \
                        '{{VID_LEFT}}': str(-self.left) + "px"}
        html_file = os.path.join(os.path.abspath(html_path), 'webview.html')
        with open(html_file) as f:
            HTML_TEMPLATE = f.read()
        movie_html = replace_str(HTML_TEMPLATE, html_dic)
        #print(movie_html)
        self.movie.load_html(movie_html)

    def reload_webview(self):
        self.view.remove_subview(self.movie)
        self.load_subview()
        self.load_movie(movie_filepath)

    #@ui.in_background
    def load_data(self, filepath):
        self.data_ready = False
        tstart = time.time()
        data = np.load(filepath)
        self.cell_specimen_ids = data['cell_specimen_ids']
        # a 1d array that maps the index of each cell to it's ID. 
        # can be used to extract meta data. 
        all_cell_dff = data['slice_all_dff']
        # a (n_cell, n_frame) array of the average dF/F fluorescence level for each cell at each frame.
        self.xy2cellidx = data['xy2cellidx']  
        # a (512, 512) array with each pixel assigned to the index (0,1,2...) of the nearest ROI. 
        # pixels not in any ROI are assigned to -1. 
        self.cell_xyones = data['cell_xyones']
        # a list of (n_px, 2) arrays. Each arrays is the (x,y) coordinates of 1's for a cell's mask. 
        self.cell_centroids = data['cell_centroids']
        # a (n_cell, 2) array of the centroids for each cell
        self.all_cell_fire = all_cell_dff > DFF_THRESHOLD
        del all_cell_dff
        
        self.data_ready = True
        tend = time.time()
        #print(tend - tstart)
        #print(len(self.cell_specimen_ids))
        #print(len(self.slice_all_dff))
        #print(len(self.xy2cellidx))
        #print(len(self.cell_xyones))

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
        del self.all_cell_fire
        del self.xy2cellidx
        del self.cell_xyones
        del self.cell_centroids

    def new_game(self):
        # remove webview
        # add webview
        # set root node
        self.score = 0
        self.cell_touched_ntimes = np.zeros_like(self.cell_specimen_ids)
        #self.start_time = self.t
        self.paused = False
        self.movie.eval_js('rec.currentTime=0;')
        self.movie_play()
        self.start_time = self.t

    def end_game(self):
        if self.score > self.highscore:
            with open('.OphysHighscore', 'w') as f:
                f.write(str(self.score))
            self.highscore = self.score
        sound.play_effect('digital:ZapTwoTone2')
        self.show_game_over_menu()

    def movie_init(self):
        self.movie.eval_js("initVideo(rec);")
        self.movie_playing = False

    def movie_play(self):
        self.movie.eval_js('rec.play();')
        self.movie_playing = True

    def movie_pause(self):
        self.movie.eval_js("rec.pause();")
        self.movie_playing = False

    def show_start_menu(self):
        self.paused = True
        self.menu = MenuScene('Neuron I/O', 'Highscore: %i' % self.highscore, ['New Game'])
        #self.menu.view.bring_to_front()
        self.present_modal_scene(self.menu)

    def show_pause_menu(self):
        self.movie_pause()
        self.paused = True

        self.menu = MenuScene('Paused', 'Highscore: %i' % self.highscore, ['Continue', 'New Game'])
        self.present_modal_scene(self.menu)

    def show_game_over_menu(self):
        self.movie_pause()
        self.paused = True
        self.menu = MenuScene('Finished!', 'Score: %i' % (self.score), ['New Game'])
        self.present_modal_scene(self.menu)

    def touch_began(self, touch):
        if self.paused or not self.movie_playing:
            return
        if touch.location.x < 48 and touch.location.y > self.size.h - 48:
            self.show_pause_menu()
            return
        x, y = touch.location
        #scene_time = self.t - self.start_time
        frame_idx = int(self.movie_time * self.fps)
        img_x, img_y = self.transform_touch(x, y)
        cell_captured = self.evaluate_touch(img_x, img_y, frame_idx, \
                                        method=EVAL_TOUCH_METHOD, radius=EVAL_TOUCH_RADIUS)
        self.evaluate_reward(cell_captured, touch.location)

        #print self.root_node.children
        #print x, y
        #print img_x, img_y
        #print cell_captured
        #print current_time
        #print time_elapsed
        #print frame_idx
        #print ""

    def transform_touch(self, x, y):
        img_y = int(round((x - self.movie.x) / float(self.movie_scale)))
        img_y += LEFT
        #print(img_y, x, self.movie.x)
        img_x = MOVIE_W / ZOOM - int(round((y - self.movie.y) / float(self.movie_scale)))
        img_x += TOP
        #print(img_x, y, self.movie.y, self.movie_scale)
        # in the image, img_x is n_row from top-left corner, and img_y is n_column
        return img_x, img_y
    
    def reverse_transform_touch(self, img_x, img_y):
        x = img_y - LEFT
        x = int(x * float(self.movie_scale)) + self.movie.x
        y = img_x - TOP
        y = int((MOVIE_W / ZOOM - y) * float(self.movie_scale)) + self.movie.y 
        return x, y
    
    def evaluate_touch(self, x, y, frame_idx, method, radius):
        if x < TOP or y < LEFT or x >= MOVIE_W - TOP or y >= MOVIE_W - LEFT:
            return 'outside'
        #print x, y
        curr_fire_idx = self.all_cell_fire[:, frame_idx].nonzero()[0]
        if method == "mask":
            return self.evaluate_touch_by_mask(x, y, curr_fire_idx)
        elif method == "distance":
            return self.evaluate_touch_by_distance(x, y, curr_fire_idx, radius)
        else: 
            raise StandardError("need to specify touch evaluation method.")
            
    
    def evaluate_touch_by_distance(self, x, y, curr_fire_idx, radius):
        fire_centroids = self.cell_centroids[curr_fire_idx]
        distance = np.sum((fire_centroids - np.array([[x, y]]))**2, axis=1)**0.5
        min_dist_idx = distance.argmin()
        if distance[min_dist_idx] <= radius:
            return curr_fire_idx[min_dist_idx]
        else:
            return None
        
    def evaluate_touch_by_mask(self, x, y, curr_fire_idx):
        cell_touched_idx = self.xy2cellidx[x, y]  # the cell index if in an cell ROI, else -1. 
        
        if cell_touched_idx in curr_fire_idx:
            return cell_touched_idx
        else:
            return None # when idx is either -1 or wrong index

    def evaluate_reward(self, cell_captured, location):
        score_location = location
        if cell_captured == 'outside':
            # no penalty. just skip the evaluation. 
            return
        if cell_captured is not None:
            added_score = REWARD
            if cell_captured == self.last_captured:
                added_score /= 2.0
            if self.cell_touched_ntimes[cell_captured] == 0:
                added_score *= 2.0
            self.last_captured = cell_captured
            score_location = self.cell_centroids[cell_captured].astype('int')
            score_location = self.reverse_transform_touch(*score_location)
            self.cell_touched_ntimes[cell_captured] += 1
            sound.play_effect('arcade:Coin_5')
        else:
            added_score = -PENALTY
            sound.play_effect('arcade:Jump_5')
        self.score += added_score
        self.score_label.text = str(int(self.score))
        if self.score > 0:
            self.score_label.color = '#00ff00'
        else:
            self.score_label.color = '#ff0000'
        self.show_points(added_score, score_location)
        #self.score_label.text = str(self.score)

    def show_points(self, points, pos):
        if points > 0:
            points_label = '+%i' % (points,)
            if points > REWARD:
                label_color = '#ffff00'
            else:
                label_color = '#00ff00'
        else:
            points_label = '%i' % (points,)
            label_color = '#ff0000'
        label = LabelNode(points_label, font=('Avenir Next Condensed', 40), color=label_color, position=pos, z_position=1)
        label.run_action(A.sequence(A.wait(0.5), A.fade_to(0, 0.5)))
        label.run_action(A.sequence(A.move_by(0, 100, 1), A.remove()))
        self.root_node.add_child(label)

    def update(self):
        if self.movie_playing is True:
            self.movie_time = float(self.movie.eval_js('rec.currentTime'))
            self.sec_left = max(0, self.game_duration - self.movie_time)
        self.time_label.text = '%02d:%02d' % (self.sec_left/60, self.sec_left%60)
        if self.sec_left == 0:
            self.end_game()
        pass

    def draw(self):
        self.clear_background()

    def menu_button_selected(self, title):
        if title == 'Continue':
            self.dismiss_modal_scene()
            self.menu = None
            self.paused = False
            self.movie_play()
        elif title == 'New Game':
            self.dismiss_modal_scene()
            self.menu = None
            self.new_game()

    def load_highscore(self):
        try:
            with open('.OphysHighscore', 'r') as f:
                return int(float(f.read()))
        except:
            return 0

    def button_pause(self, sender):
        self.movie_pause()

    def button_play(self, sender):
        self.movie_play()

    def button_init(self, sender):
        self.movie_init()

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
    #main_view = ui.View()
    w, h = ui.get_window_size()
    frame = (0,0,w,h)
    #main_view.frame = frame
    game = SceneView()
    game.scene = Game()
    game.frame = frame
    game.frame_interval = 2
    game.shows_fps = True
    game.scene.fixed_time_step = True
    #main_view.add_subview(game)
    game.present('full_screen', hide_title_bar=True)
    #print movie.frame

if __name__ == '__main__':
    setup_view()

