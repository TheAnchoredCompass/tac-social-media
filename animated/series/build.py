"""Build the TAC story-video series from scenarios.json.
Usage: python3 build.py <name|all> [preview]
Each video: dynamic timing from text length, narration s1..s5.mp3 placed by story beat,
Calm Mind bed under the voice, loudnorm to -16 LUFS."""
import json, os, subprocess, sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '_src')
FPS = 30
S = json.load(open(os.path.join(HERE, 'scenarios.json')))


def dur(p):
    return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                          '-of', 'csv=p=0', p]).decode())


def timeline(c, d):
    T = {}
    T['bad0'] = 0.9
    T['bad1'] = T['bad0'] + len(c['bad']) * 0.065
    T['del0'] = T['bad1'] + 1.3
    T['del1'] = T['del0'] + 1.0
    T['s1a'] = T['del1'] + 0.4
    T['s1b'] = T['s1a'] + 0.6
    T['q0'] = T['s1b'] + 0.3
    T['q1'] = T['q0'] + len(c['question']) * 0.042
    T['qsend'] = T['q1'] + 0.2
    T['dot0'] = T['qsend'] + 0.3
    T['a0'] = T['dot0'] + 1.1
    words = len((c['answerLead'] + ' ' + c['answerTry']).split())
    T['a1'] = T['a0'] + words * 0.09
    s2a = T['a1'] + 1.2
    # narration 1-3
    starts = [0.2]
    starts.append(max(T['del0'] - 0.1, starts[0] + d[0] + 0.15))
    starts.append(max(T['s1a'], starts[1] + d[1] + 0.15))
    # keep the TAC answer on screen until line 3 has finished
    s2a = max(s2a, starts[2] + d[2] + 0.3)
    T['s2a'] = s2a
    T['s2b'] = s2a + 0.6
    T['g0'] = T['s2b'] + 0.3
    T['g1'] = T['g0'] + len(c['good']) * 0.036
    T['gsend'] = T['g1'] + 0.2
    T['sd0'] = T['gsend'] + 0.4
    T['sr'] = T['sd0'] + 1.0
    starts.append(max(T['s2a'], starts[2] + d[2] + 0.15))
    end0 = max(T['sr'] + 2.0, starts[3] + d[3] + 0.2)
    T['end0'] = end0
    T['end1'] = end0 + 0.6
    starts.append(max(end0 + 0.4, starts[3] + d[3] + 0.15))
    T['total'] = round(starts[4] + d[4] + 1.2, 2)
    return {k: round(v, 3) for k, v in T.items()}, [round(s, 3) for s in starts]


def build(name, preview=False):
    c = S[name]
    out = os.path.join(HERE, name)
    vo = [os.path.join(out, f's{i}.mp3') for i in range(1, 6)]
    d = [dur(p) for p in vo]
    T, starts = timeline(c, d)
    cfg = dict(c); cfg['T'] = T
    open(os.path.join(SRC, 'cfg.js'), 'w').write('window.CFG=' + json.dumps(cfg, ensure_ascii=False) + ';')
    silent = os.path.join(out, 'silent.mp4')
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        pg.goto('file://' + SRC + '/scene.html'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(300)
        if preview:
            for k in ['bad1', 'a1', 'g1', 'sr']:
                t = T[k] + (0.6 if k == 'sr' else -0.05)
                pg.evaluate(f'render({t})'); pg.screenshot(path=os.path.join(out, f'prev_{k}.png'))
            b.close(); return T, starts
        n = int(T['total'] * FPS)
        ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg',
                               '-i', '-', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', silent],
                              stdin=subprocess.PIPE)
        for i in range(n):
            pg.evaluate(f'render({i / FPS})')
            ff.stdin.write(pg.screenshot(type='jpeg', quality=93))
        ff.stdin.close(); ff.wait(); b.close()
    total = T['total']
    music = os.path.join(SRC, 'track_calmmind.m4a')
    inputs = ['-i', silent]
    for p in vo: inputs += ['-i', p]
    inputs += ['-i', music, '-i', music, '-i', music]
    fl = []
    for i, s in enumerate(starts):
        ms = int(s * 1000)
        fl.append(f'[{i + 1}:a]aformat=sample_rates=44100:channel_layouts=stereo,adelay={ms}|{ms}[v{i}]')
    fl.append('[6:a][7:a]acrossfade=d=2[m01];[m01][8:a]acrossfade=d=2,'
              f'atrim=0:{total},afade=t=in:d=0.8,afade=t=out:st={total - 2.2}:d=2.2,volume=0.20,'
              'aformat=sample_rates=44100:channel_layouts=stereo[mus]')
    fl.append('[v0][v1][v2][v3][v4]amix=inputs=5:normalize=0:duration=longest[vox]')
    fl.append(f'[vox][mus]amix=inputs=2:normalize=0:duration=longest,atrim=0:{total},loudnorm=I=-16:TP=-1.5:LRA=11[a]')
    final = os.path.join(out, f'TAC_anim_{name}.mp4')
    subprocess.check_call(['ffmpeg', '-v', 'error', '-y'] + inputs +
                          ['-filter_complex', ';'.join(fl), '-map', '0:v', '-map', '[a]', '-c:v', 'copy',
                           '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', final])
    lines = c['narration']
    md = [f'# {name}: narration (My Cloned Voice 2, eleven_v4, one take each)', '| Starts | Line |', '|---|---|']
    md += [f'| {s:.2f}s | {l} |' for s, l in zip(starts, lines)]
    md.append(f'\nVideo {total:.1f}s, 1080x1920, 30 fps. Music: Calm Mind (Pixabay license), lowered under the voice; mix -16 LUFS.')
    md.append('Line 5 reuses the approved draft 3 take of the same line.')
    open(os.path.join(out, 'NARRATION.md'), 'w').write('\n'.join(md) + '\n')
    os.remove(silent)
    return T, starts


if __name__ == '__main__':
    names = list(S) if sys.argv[1] == 'all' else [sys.argv[1]]
    for n in names:
        T, st = build(n, preview=len(sys.argv) > 2)
        print(n, 'total', T['total'], 'starts', st)
