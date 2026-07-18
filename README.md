# TKA IX-F — Peta Menuju Sekolah Impian

Prototipe tahap 2. File dipisah per fungsi (bukan satu file besar) supaya gampang
diedit dan tidak perlu scroll panjang tiap update.

## Struktur folder

```
TKA-RAJA-WEB-IX-F/
├── index.html              # HTML utama (semantik + aksesibel)
├── css/
│   ├── base.css             # variabel warna, tipografi, reset, fokus keyboard
│   ├── loading.css          # layar loading (marquee, animasi jatuh)
│   ├── layout.css           # header, nav, hero, benefit grid, footer
│   └── components.css       # panel uji kemampuan, modal
├── js/
│   ├── loading.js            # animasi teks jatuh + transisi ke homepage
│   ├── navigation.js         # perpindahan tab Home / Sistem TKA Kita / Belajar
│   └── test-flow.js          # pilih level -> modal konfirmasi -> kirim ke backend
└── backend/
    ├── app.py                # backend Flask minimal (endpoint backup hasil tes)
    ├── requirements.txt
    └── data/                 # tempat backup hasil tersimpan (JSON per submission)
```

## Cara menjalankan

**Frontend saja (tanpa backend):**
Buka `index.html` langsung di browser. Semua fitur visual & alur dialog jalan;
kalau backend belum aktif, hasil tes otomatis disimpan sebagai cadangan di
`localStorage` browser.

**Dengan backend (biar hasil ke-backup di server):**
```bash
cd backend
pip install -r requirements.txt
python app.py
```
Buka `http://localhost:5000` di browser — Flask sekarang menyajikan frontend
DAN backend dari satu server yang sama, jadi tidak perlu server statis
terpisah lagi.

**Production (bukan dev server):**
```bash
pip install -r backend/requirements.txt
gunicorn --chdir backend app:app --bind 0.0.0.0:$PORT
```
Ini juga sudah ditulis di `Procfile` supaya platform hosting seperti
Render/Railway otomatis tahu cara menjalankannya.

## Catatan keamanan (baca sebelum publish ke internet)

Yang sudah ada:
- Validasi & whitelist input di backend (level/status/waktu ditolak kalau di luar format yang diharapkan)
- Nama file backup dibuat server (uuid), bukan dari input pengguna — mencegah path traversal
- Header keamanan dasar (`X-Content-Type-Options`, `X-Frame-Options`)
- CORS dibatasi ke satu origin, bukan `*`
- Batas ukuran body request

Yang **belum** ada dan wajib ditambah sebelum dipakai publik:
- HTTPS (pasang di belakang reverse proxy — nginx/Caddy — jangan http:// polos)
- Rate limiting per-IP
- Autentikasi akun siswa (kalau nanti perlu login)
- Penyimpanan data yang lebih tahan lama daripada file JSON lokal
- Audit ulang kalau nanti bank soal, kalkulator nilai, dan database sekolah sungguhan sudah masuk — makin banyak data pribadi siswa yang tersimpan, makin ketat keamanannya harus

## Perbaikan keamanan terbaru

Versi sebelumnya sempat menyajikan seluruh folder project (termasuk
`backend/app.py` dan `backend/data/*.json`) lewat static file serving —
artinya siapa pun yang tahu URL-nya bisa buka source code atau hasil tes
siswa lain langsung dari browser. Sudah diperbaiki: sekarang hanya
`css/`, `js/`, dan `index.html` yang bisa diakses publik; folder
`backend/` (termasuk `data/`) tidak lagi ter-expose.

## Fitur baru: Dukung Kami & Testimoni

Section "Dukung Kami" di tengah homepage minta izin share link (bukan
donasi uang — belum ada kanal donasi resmi, jadi tombolnya tidak
berpura-pura ada). Section testimoni sengaja masih kosong / cuma berisi
satu kartu contoh yang ditandai jelas "contoh tampilan" — kartu review
dan rating asli baru boleh muncul kalau memang ada masukan sungguhan dari
pengguna, supaya tidak menampilkan review palsu. Slot Trustpilot juga
masih placeholder: widget resmi baru bisa dipasang setelah situs ini
punya domain sendiri dan didaftarkan sebagai akun Trustpilot Business.

## Yang masih placeholder

- Bank soal TKA asli (belum ada — perlu materi yang tervalidasi, bukan karangan)
- Sistem pendeteksi level otomatis
- Kalkulator nilai rapor (60%) + TKA (40%)
- Database sekolah SMA/SMK per rayon
- Materi belajar 4 mata pelajaran di menu "Belajar"

Semua di atas didesain untuk masuk secara bertahap tanpa perlu bongkar ulang
struktur file yang sudah ada.
