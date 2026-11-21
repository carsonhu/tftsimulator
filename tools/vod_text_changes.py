"""Frames where a number printed in the inspection panel changes (docs/evidence-method.md).

    python tools/vod_text_changes.py <video> <first frame> <last frame> [--field as|mana] [--out DIR]

Thresholds the field's bright text pixels in every frame and reports each frame where they change, with a 2x crop
of the stats row (or the mana line) at every change saved to DIR for reading the digits. Frame numbers are the
video's own (at its own fps; 60 fps = 2 frames per game tick).

Fields, measured on a 1280x720 recording (Outplayed, PBE 2026-11-17):
    as    the attack-speed number under the sword icon in the stats grid
    ap    the ability power % in the stats grid (top row, third; Titan's Resolve stacks move it 2% at a time)
    ad    the bonus attack damage % in the stats grid (top row, second; Kraken's Fury moves it 3.5% per launch)
    mana  the "current / max" text on the mana bar (the bar itself animates over several frames; the text
          changes on the frame the mana does)
"""
import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vod_panel import video_fps  # noqa: E402

FIELDS = {  # x, y, w, h of the number; crop shown for reading (x, y, w, h); text brightness threshold
    'as': ((1122, 572, 36, 16), (1080, 525, 200, 60), 120),
    'mana': ((1150, 262, 80, 14), (1110, 250, 170, 40), 120),  # text over the bar is dimmer than white: keep 120
    'ap': ((1186, 532, 34, 16), (1080, 505, 200, 60), 120),  # the AP % in the stats grid (top row, third)
    'ad': ((1158, 532, 28, 12), (1080, 505, 200, 60), 150),  # the bonus AD % (top row, second; yellow: 150)
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('video')
    ap.add_argument('first', type=int)
    ap.add_argument('last', type=int)
    ap.add_argument('--field', default='as', choices=FIELDS)
    ap.add_argument('--out', default=None)
    a = ap.parse_args()
    fps = video_fps(a.video)
    (x, y, w, h), (cx, cy, cw, ch), bright = FIELDS[a.field]
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-ss', f'{a.first / fps:.4f}', '-i', a.video, '-frames:v',
                          str(a.last - a.first + 1), '-vf', f'crop={w}:{h}:{x}:{y}', '-f', 'rawvideo', '-pix_fmt',
                          'gray', '-'], stdout=subprocess.PIPE)
    prev, n, changes = None, 0, []
    while True:
        buf = p.stdout.read(w * h)
        if len(buf) < w * h:
            break
        sig = bytes(1 if v > bright else 0 for v in buf)  # text pixels
        if prev is not None and sum(u != v for u, v in zip(sig, prev)) > 6:
            changes.append(a.first + n)
        prev = sig
        n += 1
    p.wait()
    for k, f in enumerate(changes):
        print(f'f{f}  t={f / fps:.3f}  +{f - changes[k - 1] if k else 0}')
        if a.out:
            os.makedirs(a.out, exist_ok=True)
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{f / fps:.4f}', '-i', a.video, '-frames:v', '1',
                            '-vf', f'crop={cw}:{ch}:{cx}:{cy},scale={2 * cw}:{2 * ch}:flags=neighbor',
                            os.path.join(a.out, f'{a.field}_{f}.png')])
    print(f'{len(changes)} changes, {a.first}-{a.last} at {fps:g} fps')
    return 0


if __name__ == '__main__':
    sys.exit(main())
