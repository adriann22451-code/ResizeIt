#!/usr/bin/env python3
"""ResizeIt (versi komputer): ubah resolusi video dengan FFmpeg (jauh lebih cepat dari konversi di browser).

Contoh:
  python resizeit.py video.mp4 -r 720
  python resizeit.py video1.mp4 video2.mov -r 480 --crf 26
  python resizeit.py folder_video/ -r 720            # semua video di folder
  python resizeit.py video.mp4 -r 1080 -e h264_nvenc # GPU NVIDIA

Syarat: FFmpeg + ffprobe terpasang dan ada di PATH (https://ffmpeg.org/download.html).
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v", ".flv", ".wmv", ".3gp", ".ts"}


def need(tool):
    if not shutil.which(tool):
        sys.exit(f"'{tool}' tidak ditemukan. Pasang FFmpeg dulu dan pastikan ada di PATH.")


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "json", str(path)],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip() or "ffprobe gagal")
    s = json.loads(out.stdout)["streams"][0]
    return int(s["width"]), int(s["height"])


def quality_args(encoder, crf, preset):
    if encoder in ("libx264", "libx265"):
        return ["-c:v", encoder, "-crf", str(crf), "-preset", preset]
    if encoder in ("h264_nvenc", "hevc_nvenc"):
        return ["-c:v", encoder, "-rc", "vbr", "-cq", str(crf), "-b:v", "0"]
    sys.exit(f"Encoder '{encoder}' belum didukung. Pilih: libx264, libx265, h264_nvenc, hevc_nvenc.")


def collect(inputs):
    files = []
    for item in inputs:
        p = Path(item)
        if p.is_dir():
            files += sorted(f for f in p.iterdir() if f.suffix.lower() in VIDEO_EXT)
        elif p.is_file():
            files.append(p)
        else:
            print(f"! Lewati (tidak ada): {item}")
    return files


def human(n):
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024 or u == "GB":
            return f"{n:.1f} {u}" if u != "B" else f"{n} B"
        n /= 1024


def convert(src, height, args):
    w, h = probe(src)
    if height >= h and not args.allow_upscale:
        print(f"- Lewati {src.name}: sudah {h}p (target {height}p). Pakai --allow-upscale untuk memperbesar.")
        return False
    dst = src.with_name(f"{src.stem}_{height}p.mp4")
    if args.output_dir:
        out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        dst = out_dir / dst.name
    if dst.exists() and not args.overwrite:
        print(f"- Lewati {src.name}: {dst.name} sudah ada (pakai --overwrite untuk menimpa).")
        return False

    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-stats",
           "-y" if args.overwrite else "-n", "-i", str(src),
           "-vf", f"scale=-2:{height}", *quality_args(args.encoder, args.crf, args.preset),
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", f"{args.audio_kbps}k",
           "-movflags", "+faststart", str(dst)]
    print(f"> {src.name}: {w}x{h} -> {height}p")
    r = subprocess.run(cmd)
    if r.returncode != 0:
        print(f"! Gagal: {src.name}")
        dst.unlink(missing_ok=True)
        return False
    a, b = src.stat().st_size, dst.stat().st_size
    print(f"  Selesai: {dst}  ({human(a)} -> {human(b)}, {100 - b * 100 // a}% lebih kecil)\n")
    return True


def main():
    ap = argparse.ArgumentParser(description="Ubah resolusi video dengan FFmpeg.")
    ap.add_argument("inputs", nargs="+", help="file video atau folder")
    ap.add_argument("-r", "--height", type=int, default=720, help="tinggi tujuan, mis. 480, 720, 1080 (default 720)")
    ap.add_argument("--crf", type=int, default=23, help="kualitas: makin kecil makin bagus/besar (default 23)")
    ap.add_argument("--preset", default="medium", help="kecepatan x264/x265: ultrafast..veryslow (default medium)")
    ap.add_argument("-e", "--encoder", default="libx264", help="libx264, libx265, h264_nvenc, hevc_nvenc")
    ap.add_argument("--audio-kbps", type=int, default=128)
    ap.add_argument("-o", "--output-dir", help="folder hasil (default: di samping file asli)")
    ap.add_argument("--overwrite", action="store_true", help="timpa file hasil yang sudah ada")
    ap.add_argument("--allow-upscale", action="store_true", help="izinkan memperbesar resolusi")
    args = ap.parse_args()

    need("ffmpeg")
    need("ffprobe")
    files = collect(args.inputs)
    if not files:
        sys.exit("Tidak ada video yang ditemukan.")
    ok = 0
    for f in files:
        try:
            ok += convert(f, args.height, args)
        except Exception as e:  # noqa: BLE001
            print(f"! {f.name}: {e}")
    print(f"Selesai: {ok}/{len(files)} video dikonversi.")


if __name__ == "__main__":
    main()
