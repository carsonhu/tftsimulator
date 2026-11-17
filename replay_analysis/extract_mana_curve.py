"""Extract mana(t) and attack-speed(t) curves for a right-clicked champion
from a TFT replay video.

Reads frames from an OBS replay via ffmpeg, and for each frame where the
champion detail panel is open (right-click held), OCRs the "current / max"
mana readout, the current attack speed stat, and the champion name.
Panel-closed stretches are recorded as gaps rather than guessed.

Calibrated against 1920x1080 recordings of the TFT client. If your replays
are a different resolution, the ROI/NAME_BOX/MANA_BOX/AS_BOX/
HP_CHECK_PIXEL constants below need to be re-measured first -- see
README.md.

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
# enough to run at several fps over a long replay. Tall enough to cover the
# name/HP/mana rows near the top of the panel *and* the attack-speed stat
# near the bottom, with a lot of dead space (ability icons) in between.
ROI = {"x": 1650, "y": 345, "w": 270, "h": 545}

# Sub-regions within the ROI crop (relative pixel coords).
NAME_BOX = (20, 4, 250, 28)
MANA_BOX = (30, 55, 250, 78)
AS_BOX = (38, 513, 80, 535)  # first stat in the second row: current AS
HP_CHECK_PIXEL = (32, 44)  # must read as green whenever the panel is open

MANA_RE = re.compile(r"(\d+)\s*/\s*(\d+)")
ASPD_RE = re.compile(r"(\d+\.\d+)")
# Champion name only: the crop's right edge catches part of the star-cost
# icon, which OCRs as trailing junk ("Veigar )", "Varus 32", ...).
NAME_RE = re.compile(r"^[A-Za-z' ]+")

# Sanity bounds for the AS OCR read; anything outside this is a misread, not
# a real in-game attack speed.
ASPD_MIN, ASPD_MAX = 0.1, 6.0


def is_panel_open(frame: np.ndarray) -> bool:
    x, y = HP_CHECK_PIXEL
    r, g, b = frame[y, x]
    return int(g) > 140 and int(g) - int(r) > 40 and int(g) - int(b) > 40


def _ocr_digits(frame_img: Image.Image, box, whitelist: str) -> str:
    crop = frame_img.crop(box)
    crop = crop.resize((crop.width * 3, crop.height * 3), Image.LANCZOS)
    return pytesseract.image_to_string(
        crop, config=f"--psm 7 -c tessedit_char_whitelist={whitelist}"
    )


def ocr_mana(frame_img: Image.Image) -> tuple[int, int] | None:
    text = _ocr_digits(frame_img, MANA_BOX, "0123456789/")
    m = MANA_RE.search(text)
    return (int(m.group(1)), int(m.group(2))) if m else None


def ocr_aspd(frame_img: Image.Image) -> float | None:
    text = _ocr_digits(frame_img, AS_BOX, "0123456789.")
    m = ASPD_RE.search(text)
    if not m:
        return None
    value = float(m.group(1))
    return value if ASPD_MIN <= value <= ASPD_MAX else None


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
        row = {
            "t": t, "open": open_, "champ": "",
            "cur": None, "mx": None, "aspd": None,
        }
        if open_:
            row["champ"] = ocr_name(img)
            parsed = ocr_mana(img)
            if parsed:
                row["cur"], row["mx"] = parsed
            row["aspd"] = ocr_aspd(img)
        rows.append(row)

    rows = clean_rows(rows)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("time_s,panel_open,champion,cur_mana,max_mana,aspd\n")
        for r in rows:
            cur_s = "" if r["cur"] is None else str(r["cur"])
            mx_s = "" if r["mx"] is None else str(r["mx"])
            aspd_s = "" if r["aspd"] is None else f"{r['aspd']:.3f}"
            f.write(f"{r['t']:.3f},{r['open']},{r['champ']},{cur_s},{mx_s},{aspd_s}\n")
    print(f"Wrote {args.out}")

    if args.plot:
        plot_curve(rows, args.out.with_suffix(".png"))

    if args.keep_frames is None:
        import shutil
        shutil.rmtree(frame_dir, ignore_errors=True)


def clean_rows(rows):
    """Fix OCR misreads using the fact that max_mana can't change while the
    same champion stays selected.

    Tesseract occasionally sticks an extra digit onto a reading (120 ->
    1202), and when an ability tooltip overlaps the panel it can misread
    cur_mana as garbage (seen in testing: 60 max mana read as cur_mana=7410).
    Within each contiguous panel-open block, max_mana is corrected to the
    block's most common reading, and any cur_mana wildly outside that
    max_mana is dropped (set back to a gap) rather than guessed at.

    aspd doesn't get the same block-invariant treatment (it genuinely
    changes every attack/stack) -- out-of-range reads are already dropped
    at OCR time by ocr_aspd's sanity bounds.
    """
    cleaned = [dict(r) for r in rows]
    block_start = None
    sentinel = {"t": None, "open": False, "champ": "", "cur": None, "mx": None, "aspd": None}
    for i, r in enumerate(cleaned + [sentinel]):
        if r["open"] and block_start is None:
            block_start = i
        elif not r["open"] and block_start is not None:
            block = cleaned[block_start:i]
            mx_counts = {}
            for b in block:
                if b["mx"] is not None:
                    mx_counts[b["mx"]] = mx_counts.get(b["mx"], 0) + 1
            if mx_counts:
                true_mx = max(mx_counts, key=mx_counts.get)
                for j in range(block_start, i):
                    if cleaned[j]["cur"] is not None and cleaned[j]["cur"] > true_mx * 1.5:
                        cleaned[j]["cur"] = None
                    cleaned[j]["mx"] = true_mx
            block_start = None
    return cleaned


def plot_curve(rows, out_path: Path):
    import matplotlib.pyplot as plt

    mana_rows = [r for r in rows if r["cur"] is not None]
    aspd_rows = [r for r in rows if r["aspd"] is not None]

    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)
    _plot_segmented(axes[0], mana_rows, "cur", "mana")
    _plot_segmented(axes[1], aspd_rows, "aspd", "attack speed")
    axes[1].set_xlabel("time (s)")
    axes[0].set_title(str(Path(out_path).stem))
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f"Wrote {out_path}")


def _plot_segmented(ax, rows, value_key, ylabel):
    # Break the line at champion-selection changes so segments aren't
    # connected across a different unit's stats.
    seg_t, seg_v = [], []
    prev_champ = None
    for r in rows:
        if r["champ"] != prev_champ and seg_t:
            ax.plot(seg_t, seg_v, marker=".", markersize=2)
            seg_t, seg_v = [], []
        seg_t.append(r["t"])
        seg_v.append(r[value_key])
        prev_champ = r["champ"]
    if seg_t:
        ax.plot(seg_t, seg_v, marker=".", markersize=2)
    ax.set_ylabel(ylabel)


if __name__ == "__main__":
    main()
