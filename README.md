## Neuron I/O (beta)
### An iOS game of in vivo neuronal activity in the brain

The idea of this game is to make it fun to interact with real-time recordings of neuronal activity in the brain. On a touch screen (iPhone/iPad), players tap onto these neurons right when they are "firing" (transient increase of fluorescence as individual neurons are being activated). To learn more about the data, visit [Allen Brain Observatory](http://observatory.brain-map.org/).

<p align="center"> 
<img src="assets/crop_sierra2_15fps_256.gif">
</p>

The game is written in Python using [Pythonista 3](http://omz-software.com/pythonista/), and can be run on iOS devices under the [Pythonista 3](http://omz-software.com/pythonista/) App. 

Two methods to install the game in Pythonista 3, 
- Download through UI (easy): Install [Pythonista Tools Installer](https://github.com/ywangd/pythonista-tools-installer). Navigate to `Games/Neuron-IO` and click `install`. 
- Download through Git: Install [Stash](https://github.com/ywangd/stash) shell and `git clone https://github.com/yueqiw/ophys-game-ios.git`.

Data source: 
© 2016 Allen Institute for Brain Science. Allen Brain Observatory. Available from: http://observatory.brain-map.org/


Notes on movie quality: Currently, the recording movies used in the demo are reconstructed from averaged fluorescent traces of each cell. So the video quality might not look ideal compared to the actual recordings. 

TODO: 
- Add a drop-down menu to select different experiments.
- Include more recordings.
- Package into an App. 
