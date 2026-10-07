# ResizeIt

Ubah resolusi video dengan mudah, tanpa mengunggah file ke server mana pun.

Ada dua cara pakai:

| | Versi HP (web) | Versi komputer (FFmpeg) |
|---|---|---|
| File | `index.html` | `resizeit.py` |
| Jalan di | Browser HP/komputer | Komputer |
| Kecepatan | Real-time (durasi video = waktu proses) | Cepat, bisa pakai GPU |
| Cocok untuk | Video pendek, praktis | Video panjang, banyak file |

## Versi HP (web)

1. Buka halaman ResizeIt di Chrome.
2. Pilih video, lalu pilih resolusi tujuan dan kualitas.
3. Ketuk **Konversi**, tunggu selesai, lalu **Simpan video**.

Tips:
- Jangan pindah aplikasi atau kunci layar saat proses berjalan.
- Hasil berformat MP4 jika didukung browser, selain itu WebM.
- Resolusi tujuan hanya menampilkan pilihan yang lebih kecil dari video asli.
- Untuk dipasang seperti aplikasi: menu **⋮ → Tambahkan ke layar utama**.

### Aktifkan lewat GitHub Pages

1. Pastikan file HTML bernama `index.html`.
2. Buka **Settings → Pages**.
3. Pilih **Deploy from a branch**, branch `main`, folder `/ (root)`, lalu **Save**.
4. Alamatnya: `https://USERNAME.github.io/NAMA-REPO/`

## Versi komputer (FFmpeg)

Syarat: [FFmpeg](https://ffmpeg.org/download.html) dan Python 3 terpasang, dan `ffmpeg` bisa dipanggil dari terminal.

```bash
# satu video ke 720p
python resizeit.py video.mp4 -r 720

# beberapa video, kualitas lebih hemat
python resizeit.py video1.mp4 video2.mov -r 480 --crf 26

# semua video di sebuah folder
python resizeit.py folder_video/ -r 720

# pakai GPU NVIDIA
python resizeit.py video.mp4 -r 1080 -e h264_nvenc
```

Opsi:

| Opsi | Fungsi |
|---|---|
| `-r`, `--height` | Tinggi tujuan, mis. 480, 720, 1080 (bawaan 720) |
| `--crf` | Kualitas. Makin kecil makin bagus dan besar (bawaan 23) |
| `--preset` | Kecepatan x264/x265, `ultrafast` sampai `veryslow` (bawaan `medium`) |
| `-e`, `--encoder` | `libx264`, `libx265`, `h264_nvenc`, `hevc_nvenc` |
| `-o`, `--output-dir` | Folder hasil (bawaan: di samping file asli) |
| `--overwrite` | Timpa file hasil yang sudah ada |
| `--allow-upscale` | Izinkan memperbesar resolusi |

Hasil disimpan sebagai `namafile_720p.mp4`. Video yang sudah lebih kecil dari target akan dilewati.
