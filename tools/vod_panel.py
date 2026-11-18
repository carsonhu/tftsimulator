"""Read the inspected unit's HP and mana bars from a TFT VOD, frame by frame (docs/evidence-method.md).

    python tools/vod_panel.py <video> <out.csv> [--start s] [--end s]

Right-clicking a unit in game keeps its panel open on the right of the screen; the panel's HP bar (green) and mana
bar (blue) fill from the left in proportion to current / max. This reads, for every frame:

    frame (the video's own frame number, at its own fps), t (s), hp_px, mana_px, portrait (a 16-value signature of the unit portrait, to split the video by which
    unit is inspected)

Layout measured on a 1280x720 recording (Outplayed, PBE 2026-11-17): both bars span x 1120-1279 (160 px); HP rows
252-266, mana rows 268-278. Mana = mana_px / 160 x max mana. At max 60 one pixel is 0.375 mana. Other resolutions
need the layout re-measured (scale the constants). The bar may animate between values; check before reading a
single frame as an exact value.
"""
import argparse
import csv
import subprocess
import sys

W, H = 1280, 720
BAR_X0, BAR_X1 = 1120, 1279
HP_ROWS = (253, 259, 265)
MANA_ROWS = (268, 269)  # the bar's top rows: the mana text and the blue regen icon sit lower
PORTRAIT = (1170, 125, 110, 110)  # x, y, w, h
CROP_X, CROP_Y, CROP_W, CROP_H = 1120, 120, 160, 160  # one crop holds the bars and the portrait


def fill(row, x0, is_on, max_gap=2):
    """Pixels filled from the left edge: 'on' pixels contiguous from the bar's left end, allowing gaps of up to
    `max_gap` (text crossing the row). Anything after a longer gap (an icon inside the bar) is not fill."""
    last, gap = -1, 0
    for x in range(BAR_X1 - BAR_X0 + 1):
        if is_on(row[x + x0 - CROP_X]):
            last, gap = x, 0
        else:
            gap += 1
            if gap > max_gap:
                break
    return last + 1


def video_fps(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate',
                          '-of', 'default=nw=1:nk=1', path], capture_output=True, text=True, check=True).stdout.strip()
    num, _, den = out.partition('/')
    return float(num) / float(den or 1)


def blue(p):
    return p[2] > 150 and p[0] < 90


def green(p):
    return p[1] > 150 and p[0] < 90


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('video')
    ap.add_argument('out')
    ap.add_argument('--start', type=float, default=0)
    ap.add_argument('--end', type=float, default=None)
    a = ap.parse_args()
    args = ['ffmpeg', '-v', 'error', '-ss', str(a.start), '-i', a.video]
    if a.end is not None:
        args += ['-t', str(a.end - a.start)]
    args += ['-vf', f'crop={CROP_W}:{CROP_H}:{CROP_X}:{CROP_Y}', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    size = CROP_W * CROP_H * 3
    fps = video_fps(a.video)  # 'frame' counts the video's own frames (60 fps: 2 per game tick)
    with open(a.out, 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['frame', 't', 'hp_px', 'mana_px', 'portrait'])
        n = 0
        while True:
            buf = proc.stdout.read(size)
            if len(buf) < size:
                break

            def row(y):
                o = (y - CROP_Y) * CROP_W * 3
                return [buf[o + 3 * i:o + 3 * i + 3] for i in range(CROP_W)]

            hp = max(fill(row(y), BAR_X0, green) for y in HP_ROWS)
            mana = max(fill(row(y), BAR_X0, blue) for y in MANA_ROWS)
            # portrait signature: 4x4 mean brightness
            px, py, pw, ph = PORTRAIT
            sig = []
            for gy in range(4):
                for gx in range(4):
                    tot = cnt = 0
                    for y in range(py + gy * ph // 4, py + (gy + 1) * ph // 4, 4):
                        o = (y - CROP_Y) * CROP_W * 3
                        for x in range(px + gx * pw // 4, px + (gx + 1) * pw // 4, 4):
                            i = o + (x - CROP_X) * 3
                            tot += buf[i] + buf[i + 1] + buf[i + 2]
                            cnt += 3
                    sig.append(tot // max(cnt, 1))
            frame = int(round(a.start * fps)) + n
            w.writerow([frame, f'{frame / fps:.4f}', hp, mana, '-'.join(map(str, sig))])
            n += 1
    proc.wait()
    print(f'{n} frames -> {a.out}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
