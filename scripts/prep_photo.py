"""Prep a photo for ASCII conversion.

Removes the background, boosts local contrast with CLAHE, composites onto pure
white, and writes a grayscale `source-prepped.png`. Run this once per photo.

    python scripts/prep_photo.py source-photo.jpg
"""

import argparse
import os
import sys
from pathlib import Path

# rembg pulls in pymatting, which JIT-compiles alpha-matting kernels at import
# time. We never ask for alpha matting, and the compile can blow up with a
# MemoryError, so skip it.
os.environ.setdefault("NUMBA_DISABLE_JIT", "1")
# onnxruntime + OpenBLAS both spin up thread pools sized to the core count and
# can fail their allocations on a many-core box. One thread is plenty here.
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def cut_out_subject(img: Image.Image, use_rembg: bool) -> np.ndarray:
    """Return an HxW float alpha mask in 0..1 for the subject."""
    if use_rembg:
        try:
            from rembg import remove
        except ImportError:
            print("rembg not installed; falling back to --no-rembg", file=sys.stderr)
        else:
            cut = remove(img.convert("RGBA"))
            return np.asarray(cut.split()[-1], dtype=np.float32) / 255.0

    # Fallback: knock out a roughly-uniform background sampled from the border.
    rgb = np.asarray(img.convert("RGB"), dtype=np.float32)
    h, w = rgb.shape[:2]
    border = np.concatenate(
        [rgb[:8].reshape(-1, 3), rgb[-8:].reshape(-1, 3),
         rgb[:, :8].reshape(-1, 3), rgb[:, -8:].reshape(-1, 3)]
    )
    bg = np.median(border, axis=0)
    dist = np.linalg.norm(rgb - bg, axis=2)
    mask = (dist > 42).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    # Keep only the largest blob so stray background speckle does not print.
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    if n > 1:
        biggest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
        mask = np.where(labels == biggest, 255, 0).astype(np.uint8)
    mask = cv2.GaussianBlur(mask, (0, 0), 2.0)
    return mask.astype(np.float32) / 255.0


def crop_to_subject(gray: np.ndarray, alpha: np.ndarray, pad: float):
    ys, xs = np.where(alpha > 0.35)
    if ys.size == 0:
        return gray, alpha
    h, w = gray.shape
    py = int((ys.max() - ys.min()) * pad)
    px = int((xs.max() - xs.min()) * pad)
    y0, y1 = max(0, ys.min() - py), min(h, ys.max() + py + 1)
    x0, x1 = max(0, xs.min() - px), min(w, xs.max() + px + 1)
    return gray[y0:y1, x0:x1], alpha[y0:y1, x0:x1]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("photo", nargs="?", default="source-photo.jpg")
    ap.add_argument("-o", "--out", default="source-prepped.png")
    ap.add_argument("--no-rembg", action="store_true", help="skip the ML cutout")
    ap.add_argument("--clip", type=float, default=2.6, help="CLAHE clip limit")
    ap.add_argument("--tiles", type=int, default=8, help="CLAHE tile grid size")
    ap.add_argument("--gamma", type=float, default=1.0, help=">1 brightens midtones")
    ap.add_argument("--pad", type=float, default=0.04, help="crop padding, fraction")
    args = ap.parse_args()

    src = Path(args.photo)
    if not src.is_absolute():
        src = ROOT / src
    if not src.exists():
        print(f"photo not found: {src}", file=sys.stderr)
        return 1

    img = Image.open(src)
    alpha = cut_out_subject(img, use_rembg=not args.no_rembg)

    gray = cv2.cvtColor(np.asarray(img.convert("RGB")), cv2.COLOR_RGB2GRAY)
    gray, alpha = crop_to_subject(gray, alpha, args.pad)

    # Neutralise the background before CLAHE so it cannot skew the histogram.
    subject_mean = float(gray[alpha > 0.5].mean()) if (alpha > 0.5).any() else 128.0
    flat = np.where(alpha > 0.5, gray, subject_mean).astype(np.uint8)

    clahe = cv2.createCLAHE(clipLimit=args.clip, tileGridSize=(args.tiles, args.tiles))
    boosted = clahe.apply(flat).astype(np.float32)

    if args.gamma != 1.0:
        boosted = 255.0 * np.power(boosted / 255.0, 1.0 / args.gamma)

    # Composite onto pure white: background -> 255 -> the blank end of the ramp.
    out = boosted * alpha + 255.0 * (1.0 - alpha)
    out = np.clip(out, 0, 255).astype(np.uint8)

    dst = Path(args.out)
    if not dst.is_absolute():
        dst = ROOT / dst
    Image.fromarray(out, mode="L").save(dst)
    print(f"wrote {dst}  ({out.shape[1]}x{out.shape[0]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
