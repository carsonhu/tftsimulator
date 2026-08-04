"""Extract a mana(t) curve for a right-clicked champion from a TFT replay video.

Reads frames from an OBS replay via ffmpeg, and for each frame where the
champion detail panel is open (right-click held), OCRs the "current / max"
mana readout and the champion name. Panel-closed stretches are recorded as
gaps rather than guessed.

Calibrated against 1920x1080 recordings of the TFT client. If your replays
are a different resolution, the ROI/NAME_BOX/MANA_BOX/HP_CHECK_PIXEL
constants below need to be re-measured first -- see README.md.

Requires ffmpeg on PATH and Tesseract OCR installed (see requirements.txt).

Usage:
    python extract_mana_curve.py path/to/replay.mkv --fps 5 --out mana.csv --plot
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytesseract
from PIL import Image

# Panel region-of-interest, calibrated at 1920x1080 (see README.md).
# Crop is [x, y, w, h] in source-video pixels; extraction only decodes this
# small region instead of the full frame, which is what makes this fast
# enough to run at several fps over a long replay.
ROI = {"x": 1650, "y": 345, "w": 270, "h": 80}

# Sub-regions within the ROI crop (relative pixel coords).
NAME_BOX = (20, 4, 250, 28)
MANA_BOX = (30, 55, 250, 78)
HP_CHECK_PIXEL = (32, 44)  # must read as green whenever the panel is open

MANA_RE = re.compile(r"(\d+)\s*/\s*(\d+)")
# Champion name only: the crop's right edge catches part of the star-cost
# icon, which OCRs as trailing junk ("Veigar )", "Varus 32", ...).
NAME_RE = re.compile(r"^[A-Za-z' ]+")


def is_panel_open(frame: np.ndarray) -> bool:
    x, y = HP_CHECK_PIXEL
    r, g, b = frame[y, x]
    return int(g) > 140 and int(g) - int(r) > 40 and int(g) - int(b) > 40


def ocr_mana(frame_img: Image.Image) -> tuple[int, int] | None:
    box = frame_img.crop(MANA_BOX)
    box = box.resize((box.width * 3, box.height * 3), Image.LANCZOS)
    text = pytesseract.image_to_string(
        box, config="--psm 7 -c tessedit_char_whitelist=0123456789/"
    )
    m = MANA_RE.search(text)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def ocr_name(frame_img: Image.Image) -> str:
    box = frame_img.crop(NAME_BOX)
    box = box.resize((box.width * 3, box.height * 3), Image.LANCZOS)
    text = pytesseract.image_to_string(box, config="--psm 7")
    m = NAME_RE.match(text.strip())
    return m.group().strip() if m else ""


def extract_frames(video_path: Path, fps: float, out_dir: Path) -> list[Path]:
    crop = f"crop={ROI['w']}:{ROI['h']}:{ROI['x']}:{ROI['y']}"
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-vf", f"fps={fps},{crop}",
        str(out_dir / "frame_%06d.png"),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise RuntimeError("ffmpeg extraction failed")
    return sorted(out_dir.glob("frame_*.png"))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("video", type=Path)
    ap.add_argument(
        "--fps", type=float, default=5.0, help="sampling rate for extraction"
    )
    ap.add_argument("--out", type=Path, default=Path("mana_curve.csv"))
    ap.add_argument("--plot", action="store_true")
    ap.add_argument(
        "--keep-frames",
        type=Path,
        default=None,
        help="also save extracted ROI frames here (for debugging crop/OCR)",
    )
    args = ap.parse_args()

    frame_dir = args.keep_frames or Path(tempfile.mkdtemp(prefix="mana_frames_"))
    frame_dir.mkdir(parents=True, exist_ok=True)

    print(f"Extracting frames at {args.fps} fps...")
    frame_paths = extract_frames(args.video, args.fps, frame_dir)
    print(f"{len(frame_paths)} frames extracted, running OCR...")

    rows = []
    for i, fp in enumerate(frame_paths):
        t = i / args.fps
        img = Image.open(fp).convert("RGB")
        arr = np.array(img)
        open_ = is_panel_open(arr)
        champ, cur, mx = "", None, None
        if open_:
            champ = ocr_name(img)
            parsed = ocr_mana(img)
            if parsed:
                cur, mx = parsed
        rows.append((t, open_, champ, cur, mx))

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("time_s,panel_open,champion,cur_mana,max_mana\n")
        for t, open_, champ, cur, mx in rows:
            cur_s = "" if cur is None else str(cur)
            mx_s = "" if mx is None else str(mx)
            f.write(f"{t:.3f},{open_},{champ},{cur_s},{mx_s}\n")
    print(f"Wrote {args.out}")

    if args.plot:
        plot_curve(rows, args.out.with_suffix(".png"))

    if args.keep_frames is None:
        import shutil
        shutil.rmtree(frame_dir, ignore_errors=True)


def plot_curve(rows, out_path: Path):
    import matplotlib.pyplot as plt

    ts = [r[0] for r in rows if r[3] is not None]
    manas = [r[3] for r in rows if r[3] is not None]
    champs = [r[2] for r in rows if r[3] is not None]

    fig, ax = plt.subplots(figsize=(14, 5))
    # Break the line at champion-selection changes so segments aren't
    # connected across a different unit's mana pool.
    seg_t, seg_m = [], []
    prev_champ = None
    for t, m, c in zip(ts, manas, champs):
        if c != prev_champ and seg_t:
            ax.plot(seg_t, seg_m, marker=".", markersize=2)
            seg_t, seg_m = [], []
        seg_t.append(t)
        seg_m.append(m)
        prev_champ = c
    if seg_t:
        ax.plot(seg_t, seg_m, marker=".", markersize=2)

    ax.set_xlabel("time (s)")
    ax.set_ylabel("mana")
    ax.set_title(str(Path(out_path).stem))
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
