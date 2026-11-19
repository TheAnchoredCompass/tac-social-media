import sys,subprocess
from playwright.sync_api import sync_playwright
d,out=sys.argv[1],sys.argv[2]; fps=30
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1920})
    pg.goto('file://'+d+'/scene.html'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(300)
    total=pg.evaluate('window.TOTAL'); n=int(total*fps)
    ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','image2pipe','-framerate',str(fps),'-c:v','mjpeg','-i','-',
        '-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
    for i in range(n):
        pg.evaluate(f'render({i/fps})')
        ff.stdin.write(pg.screenshot(type='jpeg',quality=93))
    ff.stdin.close(); ff.wait(); b.close(); print('frames',n)
