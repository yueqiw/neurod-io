import ui
import os, urllib

TEMPLATE = '''
<!DOCTYPE html>
<html>
<style>
body {margin:0;}
</style>
<body>

<video id="myvideo" preload loop border="100">
    <source src="{{FPATH}}", type="video/mp4">
</video>

<!--
<button type="button" onclick="vid_play()">Play/Pause</button>
-->

<script>
function vid_play() {
    var vid = document.getElementById("myvideo");
    vid.preload = true;
    vid.play();
    }
</script>

</body>
</html>
'''

JS = '''
var video;
video = document.getElementById('video');
video.src = "{{FPATH}}";
video.loop = true;
#video.play();
video.autoplay=true;
video.load();
'''


def run_html():
    filepath = "file://" + os.path.abspath("./movie.mp4")
    print(filepath)
    html = TEMPLATE.replace('{{FPATH}}', filepath)
    print(html)
    v = ui.View(background_color="black")
    webview = ui.WebView(name='mp4')
    webview.scales_page_to_fit = False
    v.add_subview(webview)
    #webview.frame = (0,0,500,500)
    #webview.present()
    webview.load_html(html)
    #webview.reload()
    #js = JS.replace('{{FPATH}}', filepath)
    #print(js)
    #def button_tapped(sender):
    #    webview.eval_js('document.getElementById("myvideo").play();')
    #button = ui.Button(title='Play')
    #button.action = button_tapped
    #v.add_subview(button)
    v.frame = (0,0,500,500)
    #button.frame = (200,200,250,250)
    webview.frame = (100,100,500,500)
    v.present(orientations=['portrait'])
    webview.eval_js('document.getElementById("myvideo").play();')
    

def run_url():
	
	filepath = "file://" + os.path.abspath("./530958091_2_9200_noise25_scale2000.mp4")
	print(filepath)
	html = TEMPLATE.replace('{{FPATH}}', filepath)
	print(html)
	v = ui.View(background_color="white")
	webview = ui.WebView(name='mp4')
	webview.scales_page_to_fit = False
	v.add_subview(webview)
	#webview.load_html(html)
	webview.load_url(filepath)
	v.frame = (0,0,500,500)
	webview.frame = (0,0,600,600)
	webview.touch_enabled = False
	v.present()
	


if __name__ == '__main__':
	run_html()
	#run_url()
