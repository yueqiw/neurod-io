import numpy as np
from scene import *
import sound
import os
import pickle

sample_name = '530958091_9200-9700'
file_dir = './data/old'
data_dir = file_dir
img_dir = os.path.join(file_dir, sample_name)
#img_dir = './530958091_59500-60300'
img_suffix = 'jpeg'
w = 512
h = 512``
img_size = 512
reward = 100
punish = -10

class Game (Scene):
    def setup(self):
        self.img_files = [f for f in os.listdir(img_dir) if f.endswith(img_suffix)]
        self.img_names = [load_image_file(os.path.join(img_dir, f)) for f in self.img_files]
        self.nframe = len(self.img_names)
        with open(os.path.join(data_dir, sample_name + '_id2maskones.p'), 'rb') as f:
            self.id2maskones = pickle.load(f)
        self.cell_specimen_ids = np.loadtxt(os.path.join(data_dir, sample_name + '_cell_specimen_ids.txt'))
        # self.all_dff = np.loadtxt(img_dir + '_slice_all_dff.txt')
        self.all_fire = np.loadtxt(os.path.join(data_dir, sample_name + '_slice_all_fire.txt'))
        
        score_font = ('Futura', 40)
        self.score_label = LabelNode('0', score_font, parent=self)
        self.score_label.position = (self.size.w * 0.8, self.size.h - 70)
        self.score_label.z_position = 1
        self.new_game()
        

    def new_game(self):
        self.paused = False
        self.img_idx = 0
        self.game_end = False
        self.score = 0
        self.score_label.text = '0'
    
    def draw(self):
        if self.game_end is True:
            self.draw_frame()
            return
        self.draw_frame()
        
        self.img_idx += 1
        if self.img_idx >= self.nframe:
            self.img_idx = self.nframe - 1
            self.game_end = True
            self.paused = True
            #self.empty_cache()
    
    def draw_frame(self):
        image(self.img_names[self.img_idx], self.size.w/2 - w/2, self.size.h/2 - h/2, w, h)
    
    def update(self):
        pass
        
    def touch_began(self, touch):
        x, y = touch.location
        print('touch')
        print((x,y))
        img_x = int((x + w/2 - self.size.w/2) * img_size / w)
        img_y = int((y + h/2 - self.size.h/2) * img_size / h)
        print((img_x, img_y))
        
        frame_idx = self.img_idx - 1
        print(frame_idx)
        correct = self.evaluate_touch(img_x, img_y, frame_idx)
        if correct:
            self.score += reward
            sound.play_effect('arcade:Coin_5')
        else:
            self.score += punish
            sound.play_effect('arcade:Jump_5')
        self.score_label.text = str(self.score)
    
    def evaluate_touch(self, x, y, frame_idx):
        curr_fire_idx = self.all_fire[:, frame_idx].nonzero()
        curr_fire_cells = self.cell_specimen_ids[curr_fire_idx]
        print curr_fire_cells
        
        print((x,y))
        print((img_size - y, x))
        for cid in curr_fire_cells:
            pixel_ones = self.id2maskones[cid]
            # print(pixel_ones)
            
            print(pixel_ones[0])
            has_match = np.all((img_size - y, x) == pixel_ones, axis=1).any()
            if has_match:
                print('match')
                return True
        
        return False
    
    def empty_cache(self):
        for k in self.img_names[:-1]:
            unload_image(k)
    


if __name__ == '__main__':
    run(Game(), LANDSCAPE, frame_interval=4, show_fps=True)
