## neurod.io 
### Fun iOS game of brain activity

Collect neuro coins by tapping onto the neurons right when they light up -- transient increase of fluorescence as neurons are "firing". Challenge yourself and see how many coins you can get! 

The idea of this game is to make it fun to interact with real-time recordings of neuronal activity in the brain. To learn more about the data, visit [Allen Brain Observatory](http://observatory.brain-map.org/).

<p align="center"> 
<img src="assets/crop_sierra2_15fps_256.gif">
</p>

Soon to be available in iOS App Store. 

The game is developed using [Pythonista 3](http://omz-software.com/pythonista/) and Xcode. 

To run the game in Pythonista 3, 
- Download through UI (easy): Install [Pythonista Tools Installer](https://github.com/ywangd/pythonista-tools-installer). Navigate to `Games/Neuron-IO` and click `install`. 
- Or download through Git: Install [Stash](https://github.com/ywangd/stash) shell and `git clone https://github.com/yueqiw/ophys-game-ios.git`.

Data source: 
© 2016 Allen Institute for Brain Science. Allen Brain Observatory. Available from: http://observatory.brain-map.org/


Notes on movie quality: Currently, the recording movies used in the demo are reconstructed from averaged fluorescent traces of each cell. So the video quality might not look ideal compared to the actual recordings. 

TODO: 
- iOS App submission. 
- Add a drop-down menu to select different experiments.
- Include more recordings. 

