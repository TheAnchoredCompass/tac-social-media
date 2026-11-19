import sys
from playwright.sync_api import sync_playwright
d=sys.argv[1]; times=[float(x) for x in sys.argv[2].split(',')]
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1920})
    pg.goto('file://'+d+'/scene.html'); pg.evaluate('document.fonts.ready')
    for t in times:
        pg.evaluate(f'render({t})'); pg.wait_for_timeout(50)
        pg.screenshot(path=f'{d}/prev_{t:05.1f}.png')
    b.close()
