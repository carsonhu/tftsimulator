# Replay mana/attack-speed extraction

Pulls mana(t) and attack-speed(t) time series for whichever champion has
their detail panel open (right-click held) in a TFT replay recording, by
OCR-reading the "current / max" mana readout and the current-AS stat every
sampled frame.

## Setup

```
pip install -r requirements.txt
```

Also needs on `PATH`:
- `ffmpeg` (frame extraction)
- `tesseract` (OCR) -- on Windows, install from the
  [UB-Mannheim build](https://github.com/UB-Mannheim/tesseract/wiki); it's
  usually at `C:\Program Files\Tesseract-OCR\tesseract.exe`, which the
  installer adds to `PATH` for you.

## Usage

```
python extract_mana_curve.py path/to/replay.mkv --fps 5 --out mana.csv --plot
```

- `--fps` is the extraction sampling rate. 5 is a reasonable default; mana
  regen ticks every 0.5s in-game, so going much above ~10fps mostly buys
  smoother plots, not new information, at the cost of longer OCR time.
- `--out` writes a CSV with columns `time_s, panel_open, champion,
  cur_mana, max_mana, aspd`. Rows where `panel_open` is `False` have all of
  those empty -- that's a gap, not a zero.
- `--plot` also writes a PNG with mana and attack speed over time stacked on
  shared time axes, each split into one line segment per contiguous
  champion-selection block.
- `--keep-frames DIR` saves the extracted (small, cropped) frames instead of
  deleting them -- useful for debugging a bad OCR read on a specific frame.

## How it works

Rather than decoding full 1920x1080 frames, `ffmpeg` crops down to just the
champion-detail-panel region during extraction (`ROI` in the script), which
is what makes OCR-per-frame fast enough to run over a whole replay. `ROI` is
tall (covers from the name row down to the attack-speed stat near the
bottom of the panel, with a lot of dead ability-icon space skipped over in
between) but still narrow, so it stays cheap. Within that crop:

- **Panel-open detection**: sample one pixel (`HP_CHECK_PIXEL`) that's
  reliably inside the green HP bar whenever a champion is selected. No HP
  bar there -> panel closed -> the frame is recorded as a gap.
- **Mana**: OCR the `cur / max` text (`MANA_BOX`) with a digit+`/`
  whitelist.
- **Attack speed**: OCR the first stat in the panel's second stat row
  (`AS_BOX`) with a digit+`.` whitelist. Reads outside `[ASPD_MIN,
  ASPD_MAX]` are treated as OCR misreads and dropped rather than kept.
- **Champion**: OCR the name row (`NAME_BOX`), then regex out everything
  after the first run of letters -- the crop's right edge catches part of
  the star-cost icon, which otherwise OCRs as junk trailing the name.

All constants (`ROI`, `NAME_BOX`, `MANA_BOX`, `AS_BOX`, `HP_CHECK_PIXEL`)
were measured by hand against a 1920x1080 recording (see calibration notes
below). **If your replays are a different resolution, these will be wrong**
and need re-measuring the same way before you trust any output.

### Re-calibrating for a different resolution

1. Extract one frame where a champion panel is open:
   `ffmpeg -ss <timestamp> -i replay.mkv -frames:v 1 frame.png`
2. Open it and find the champion-panel region's pixel bounds (HP bar, mana
   bar, name text, and the attack-speed stat near the bottom of the panel --
   it's the first icon/number in the second stat row). A quick way: crop
   candidate regions with `ffmpeg -vf crop=W:H:X:Y` and
   `scale=W*3:H*3:flags=neighbor` to zoom in, iterating on `X,Y,W,H` until
   the crop tightly frames what you want. For pixel-exact box edges, load
   the frame with PIL/numpy and scan for where a text/HP-bar color's pixels
   start and stop, rather than eyeballing it (see the `git log` for this
   file's diff that added `AS_BOX` for a worked example).
3. Update `ROI` to cover name+HP+mana+attack-speed, and
   `NAME_BOX`/`MANA_BOX`/`AS_BOX`/`HP_CHECK_PIXEL` to their positions
   *relative to* `ROI`'s top-left corner.

## Known limitations

- OCR isn't perfect -- expect an occasional misread digit (e.g. a `120`
  max-mana read as `1202` on a single frame). `clean_rows()` corrects
  `max_mana`/`cur_mana` using the fact that max mana can't change within a
  champion-selection block; `aspd` reads are just bounds-checked
  (`ASPD_MIN`/`ASPD_MAX`) since AS genuinely changes every frame and can't
  be corrected the same way. Don't trust any single row blindly.
- Only tracks whichever unit is currently right-clicked; it can't see
  everyone's stats at once.
- Cast-time estimation isn't implemented yet. The mana curve already makes
  casts visible as a sharp drop, and `verify_varus_mana.py` (in the parent
  `set18/` directory) shows how to compare a simulated champion's mana/AS
  curve against an extracted real one.
