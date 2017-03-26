from scene import *
import ui, os
from game_menu import MenuScene, ButtonNode
A = Action
rec_filepath = './data/530958091/natural_movie_one_38757-39661_ffmpeg_sepia_crf22_gs3_main31.mp4'
html_path = "./"


def replace_str(text, dic):
    for x in dic:
        text = text.replace(x, str(dic[x]))
    return text

class Game(Scene):
    def setup(self):
        self.root_node = Node(parent=self)
        self.background_color = None
        self.bounds = (0,0,800,600)
        movie_filepath = "file://" + os.path.abspath(rec_filepath)
        #print(rec_filepath)
        #print(self.size.w, self.size.h)
        self.movie_w, self.movie_h = 512, 768
        html_dic = {'{{VID_FPATH}}': movie_filepath, '{{VID_NAME}}': 'recording', \
                        '{{VID_WIDTH}}': self.movie_w, '{{VID_HEIGHT}}': self.movie_h}
        html_file = os.path.join(os.path.abspath(html_path), 'webview.html')
        with open(html_file) as f:
            HTML_TEMPLATE = f.read()
        movie_html = replace_str(HTML_TEMPLATE, html_dic)
        #print(movie_html)
        
        self.movie = ui.WebView(name='movie')
        self.movie.background_color = '#ff0000'
        self.movie.alpha = 1
        self.movie.scales_page_to_fit = False
        self.view.add_subview(self.movie)
        
        #self.movie.send_to_back()
        #self.bring_to_front()
        #self.view.send_to_back()
        
        #self.view.background_color = '#ff0000'
        self.movie.load_html(movie_html)
        
        #print(self.view)
        print(self.view.bounds)
        
        self.movie.frame = (self.size.w/2 - self.movie_w/2, self.size.h/2 - self.movie_h/2, \
                            self.movie_w, self.movie_h)
        
        print(self.movie.bounds)
        self.movie.touch_enabled = False
        self.highscore = 0
        #print(self.paused)
        self.run_action(A.sequence(A.wait(0.1), A.call(self.initialize), \
                        A.wait(2),  A.call(self.show_start_menu)))
        self.add_helper_buttons()
        #self.did_change_size()
    
    def initialize(self):
        self.movie.eval_js("initVideo(rec);")
    
    def did_change_size(self):
        self.movie.frame = (self.size.w/2 - self.movie_w/2, self.size.h/2 - self.movie_h/2, \
                            self.movie_w, self.movie_h)
    
    def show_start_menu(self):
        self.paused = True
        self.menu = MenuScene('Match3', 'Highscore: %i' % self.highscore, ['New Game'])
        #self.menu.view.bring_to_front()
        self.present_modal_scene(self.menu)
        
    def button_pause(self, sender):
        self.movie.eval_js("rec.pause();")
    
    def button_play(self, sender):
        self.movie.eval_js('rec.play();')

    def button_init(self, sender):
        self.movie.eval_js("initVideo(rec);")
    
    def touch_began(self, touch):
        #self.recording.eval_js('document.querySelector("video").style.filter="sepia(100%)";')
        #style = self.recording.eval_js('document.querySelector("video").style.filter;')
        print self.paused
        
        if self.paused is True:
            self.paused = False
        else:
            self.movie.eval_js('update_t();')
    def draw(self):
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

if __name__ == '__main__':
    run(Game(), PORTRAIT, frame_interval=2, show_fps=True)
