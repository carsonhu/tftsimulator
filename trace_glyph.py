"""Trace a flat glyph image into the SVG paths app.js draws.

    python trace_glyph.py damageamp.png
    python trace_glyph.py damageamp.png --invert     # dark glyph on light
    python trace_glyph.py damageamp.png --preview out.png

Prints path strings ready to paste into STAT_ICONS in app.js, fitted to the
same 24x24 box the other glyphs use.

This exists because eyeballing a 24px reference and redrawing it by hand got
Attack Speed and Damage Amp wrong twice. Tracing the actual pixels is not a
better guess, it is not a guess.

How it reads an image: the alpha channel when there is a real one, otherwise
luminance against the median, so a screenshot crop of a light glyph on a dark
background works as-is. Every separate blob becomes its own path -- three
blades stay three paths -- and holes inside a blob become subpaths wound the
other way, which is what makes SVG's even-odd fill cut them out.

The outline itself is a Moore-neighbourhood boundary walk (no scipy or skimage
in this venv, and one traced glyph is not worth a dependency), then
Douglas-Peucker to drop the pixel staircase. --tolerance trades fidelity for
node count; the default is tuned for a glyph a few dozen pixels across.
"""

import argparse
import sys

import numpy as np
from PIL import Image

BOX = 24.0  # the viewBox app.js uses
MIN_BLOB_FRACTION = 0.004  # ignore specks: JPEG noise, anti-aliasing crumbs


def lift_mask(image):
    """Separate a pale glyph from the coloured plate it is printed on.

    Riot's Booster icons are a cream glyph on a saturated gold square. Neither
    brightness nor saturation splits them cleanly -- the glyph is shaded, so
    its dark corners are dimmer than the plate's lit ones -- but hue does: the
    glyph is near-neutral (blue about 0.7 of red) and the gold is not (about
    0.2). The plate's own rim catches the light and reads as glyph, so the
    border is trimmed; no glyph runs to the edge of its own icon.
    """
    pixels = np.array(image.convert("RGB")).astype(float)
    red, blue = pixels[..., 0], pixels[..., 2]
    mask = (blue / (red + 1) > 0.35) & (red > 90)
    pad = int(0.13 * mask.shape[0])
    mask[:pad, :] = mask[-pad:, :] = False
    mask[:, :pad] = mask[:, -pad:] = False
    return mask


def load_mask(path, invert, lift=False):
    """A boolean array, True where the glyph is."""
    image = Image.open(path).convert("RGBA")
    if lift:
        return lift_mask(image)
    alpha = np.array(image.getchannel("A"))
    if alpha.min() < 250:
        # A real alpha channel: the glyph is what is opaque.
        mask = alpha > 128
    else:
        grey = np.array(image.convert("L")).astype(float)
        # Halfway between the darkest and lightest, which separates a flat
        # glyph from a flat background without assuming which is which.
        cut = (grey.min() + grey.max()) / 2
        mask = grey > cut
        if invert:
            mask = ~mask
        # A glyph is the minority of a cropped icon; if "above the cut" is
        # most of the image, the background is the light half.
        if mask.mean() > 0.5:
            mask = ~mask
    return mask


def label_blobs(mask):
    """Split the mask into connected components (4-connected), largest first."""
    height, width = mask.shape
    labels = np.zeros((height, width), dtype=int)
    blobs = []
    for y in range(height):
        for x in range(width):
            if not mask[y, x] or labels[y, x]:
                continue
            index = len(blobs) + 1
            stack, cells = [(y, x)], []
            labels[y, x] = index
            while stack:
                cy, cx = stack.pop()
                cells.append((cy, cx))
                for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                    if 0 <= ny < height and 0 <= nx < width:
                        if mask[ny, nx] and not labels[ny, nx]:
                            labels[ny, nx] = index
                            stack.append((ny, nx))
            blobs.append(cells)
    blobs.sort(key=len, reverse=True)
    return blobs


def trace_outline(cells):
    """Moore-neighbourhood walk around one blob, returning pixel corners.

    Walks the *corners* between pixels rather than pixel centres, so the
    outline sits on the shape's edge instead of half a pixel inside it.
    """
    filled = set(cells)
    start = min(cells)  # topmost, then leftmost: guaranteed on the boundary
    # 8 directions, clockwise from east.
    steps = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
    outline = [start]
    current = start
    backtrack = 4  # came from the west
    guard = 8 * len(cells) + 16
    while guard:
        guard -= 1
        found = False
        for offset in range(1, 9):
            direction = (backtrack + offset) % 8
            dy, dx = steps[direction]
            nxt = (current[0] + dy, current[1] + dx)
            if nxt in filled:
                backtrack = (direction + 4) % 8
                current = nxt
                found = True
                break
        if not found:
            break  # a single isolated pixel
        if current == start and len(outline) > 2:
            break
        outline.append(current)
    return outline


def simplify(points, tolerance):
    """Douglas-Peucker."""
    if len(points) < 3:
        return points
    start, end = np.array(points[0], float), np.array(points[-1], float)
    line = end - start
    length = np.hypot(*line)
    worst, index = -1.0, 0
    for i in range(1, len(points) - 1):
        point = np.array(points[i], float)
        if length == 0:
            distance = np.hypot(*(point - start))
        else:
            # 2-D cross product by hand: numpy 2 dropped it for 2-vectors.
            offset = point - start
            distance = abs(line[0] * offset[1] - line[1] * offset[0]) / length
        if distance > worst:
            worst, index = distance, i
    if worst <= tolerance:
        return [points[0], points[-1]]
    left = simplify(points[: index + 1], tolerance)
    right = simplify(points[index:], tolerance)
    return left[:-1] + right


def to_path(outlines, origin, scale):
    """Pixel outlines -> one SVG path string in the 24x24 box."""
    parts = []
    for outline in outlines:
        coords = []
        for y, x in outline:
            px = (x - origin[1]) * scale
            py = (y - origin[0]) * scale
            coords.append(f"{px:.2f} {py:.2f}")
        parts.append("M" + " L".join(coords) + " Z")
    return " ".join(parts)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image")
    parser.add_argument("--invert", action="store_true", help="dark glyph on light")
    parser.add_argument(
        "--lift",
        action="store_true",
        help="pull a pale glyph off a coloured plate (Riot's framed icons)",
    )
    parser.add_argument("--tolerance", type=float, default=0.6, help="in source pixels")
    parser.add_argument(
        "--top",
        type=int,
        help="keep only the N largest shapes -- lifting a glyph off a framed "
        "icon leaves rim highlights behind, and they are always the small ones",
    )
    parser.add_argument("--preview", help="write the traced shape back out as a PNG")
    args = parser.parse_args()

    mask = load_mask(args.image, args.invert, args.lift)
    if not mask.any():
        print("nothing above the threshold -- try --invert", file=sys.stderr)
        return 1

    floor = mask.sum() * MIN_BLOB_FRACTION
    blobs = [b for b in label_blobs(mask) if len(b) >= floor]
    if args.top:
        blobs = blobs[: args.top]
        # Re-fit the box to what survived: a rim highlight left in the corner
        # would otherwise stretch the bounds and squash the real glyph.
        mask = np.zeros_like(mask)
        for blob in blobs:
            for y, x in blob:
                mask[y, x] = True

    ys, xs = np.nonzero(mask)
    origin = (ys.min(), xs.min())
    span = max(ys.max() - ys.min(), xs.max() - xs.min()) + 1
    scale = BOX / span
    # Centre the shorter axis, so a tall glyph is not left-aligned in the box.
    pad_x = (BOX - (xs.max() - xs.min() + 1) * scale) / 2
    pad_y = (BOX - (ys.max() - ys.min() + 1) * scale) / 2

    print(f"# {args.image}: {len(blobs)} shape(s), {span}px across", file=sys.stderr)

    for blob in blobs:
        outline = simplify(trace_outline(blob), args.tolerance)
        path = to_path([outline], origin, scale)
        # Apply the centring offset after scaling, which is why it is not
        # folded into to_path.
        path = shift(path, pad_x, pad_y)
        print(f'      {{ d: "{path}" }},')

    if args.preview:
        preview(mask, args.preview)
    return 0


def shift(path, dx, dy):
    out, tokens = [], path.split(" ")
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token in ("Z",):
            out.append(token)
            index += 1
            continue
        head = token[0] if token[0] in "ML" else ""
        x = float(token[len(head):])
        y = float(tokens[index + 1])
        out.append(f"{head}{x + dx:.2f}")
        out.append(f"{y + dy:.2f}")
        index += 2
    return " ".join(out)


def preview(mask, path):
    Image.fromarray((mask * 255).astype("uint8")).save(path)
    print(f"# threshold preview: {path}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
