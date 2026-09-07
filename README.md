# Pipeline Data Mobil (Automobile Dataset)

## 1. Tentang Dataset
Dataset yang dipakai di sini (`automobileEDA_dirty_training.csv`) berisi 205 baris data mobil dengan 30 kolom — mulai dari spesifikasi mobil (merek, tipe bodi, mesin, dimensi) sampai performa dan harga (horsepower, konsumsi bahan bakar, price). Ini versi "dikotori" dari dataset automobileEDA yang biasa dipakai di course data analysis, ditambah satu kolom baru, `transaction_date`, yang formatnya sengaja dibikin berantakan.

## 2. Sumber Dataset
Dari mentor bootcamp, lewat link `https://s.id/dataset-sesi-3` (file `Dataset_Sesi_3.zip`).

## 3. Struktur Folder
```
data-pipeline-assignment/
├── data/
│   ├── raw/automobileEDA_dirty_training.csv
│   └── processed/automobileEDA_processed.csv
├── src/pipeline.py
├── documentation/data-flow-diagram.png
├── README.md
└── requirements.txt
```

## 4. Kondisi Awal Dataset
Pas pertama kali dicek pakai `df.info()`, `df.isnull().sum()`, dan `df.duplicated()`, ketahuan ada beberapa masalah. Ukuran awalnya 205 baris x 30 kolom, dengan total 17 missing values tersebar di beberapa kolom:

| Kolom | Jumlah missing |
|---|---|
| transaction_date | 2 |
| make | 2 |
| num-of-doors | 2 |
| stroke | 4 |
| horsepower | 3 |
| price | 3 |
| horsepower-binned | 1 |

Selain itu ada 4 baris yang isinya persis sama di semua kolom (duplikat murni) — kelihatannya baris ke-5, 60, 100, dan 25 masing-masing kegandain satu kali di bagian akhir file.

Kolom `transaction_date` jadi masalah tersendiri karena formatnya beda-beda tiap baris: ada yang gaya ISO (`2025-01-01`), ada yang pakai slash (`06/01/2025`), ada yang dash tapi angka semua (`01-07-2025`), sampai yang pakai nama bulan (`04-Jan-2025`). Empat gaya format nyampur jadi satu kolom yang sama.

Penulisan kategori juga nggak konsisten:
- `make`: ada `ALFA-ROMERO` dan `alfa-romero`, ada juga yang kesangkut spasi di belakang kayak `"dodge  "`
- `body-style`: campur `SEDAN`, `Sedan`, `sedan`
- `drive-wheels`: `AWD`, `RWD`, `4wd`, `fwd`, `rwd` — semuanya sebenarnya cuma 4 kategori, beda kapitalisasi doang
- `fuel-system`: `MPFI`, `Mpfi`, `mpfi`

Satu hal menarik lagi: `num-of-doors` dan `num-of-cylinders` isinya kata bahasa Inggris ("two", "four", "six"), padahal itu sebenarnya angka biasa. Jadi ini juga masuk kategori "data kategorikal yang sebenarnya numerik".

## 5. Data Cleaning
Ini bagian yang paling banyak makan waktu. Berikut yang dilakukan dan alasannya:

**Merapikan penulisan kategori** (`make`, `body-style`, `drive-wheels`, `fuel-system`)
`strip()` dulu buat buang spasi nyasar, lalu `lower()` semua supaya "ALFA-ROMERO" dan "alfa-romero" dianggap sama. Simpel, tapi cukup untuk kasus di dataset ini.

**Standarisasi format tanggal** (`transaction_date`)
Pakai `pd.to_datetime(..., format="mixed", dayfirst=True)` biar pandas nebak format tiap baris otomatis. Jujur, ini nggak sempurna — untuk format yang isinya angka semua (kayak `01-07-2025`), nggak ada cara pasti buat tahu itu tanggal-dulu atau bulan-dulu tanpa konteks tambahan. Diasumsikan dayfirst (format non-US) karena itu yang lebih umum dipakai di luar Amerika, dan ini ditulis sebagai asumsi, bukan fakta yang pasti benar. Tanggal yang beneran nggak bisa diparse dibiarkan jadi missing (NaT) daripada ditebak asal.

**Hapus baris duplikat**
`drop_duplicates()` — 4 baris yang sama persis dibuang, karena nggak nambah informasi apa pun dan malah bisa bikin bias kalau datanya dipakai buat analisis lanjutan.

**Isi missing values numerik** (`stroke`, `horsepower`, `price`)
Diisi pakai median kolom masing-masing. Median dipilih karena harga mobil di dataset ini range-nya lebar banget (dari yang murah sampai yang mahal), jadi kalau pakai mean, hasilnya bisa ketarik ke arah outlier.

**Isi missing values kategorikal** (`make`, `num-of-doors`, `horsepower-binned`)
Diisi pakai modus (nilai yang paling sering muncul). Karena cuma 1-2 data yang hilang di tiap kolom ini, risikonya kecil kalau diisi dengan nilai paling umum.

**`transaction_date` yang masih missing**
Dibiarkan NaT (kosong). Nggak ada cara masuk akal buat nebak tanggal transaksi spesifik, jadi lebih baik jujur dibiarkan kosong daripada dipaksa isi.

**Hasil:** 205 baris jadi 201 (4 duplikat kebuang), missing values dari 17 jadi 2 (2 sisanya ya tanggal yang memang nggak bisa diselamatkan itu).

## 6. Data Transformation

**Min-Max Scaling di `horsepower`**
Kolom baru `horsepower_scaled` dibuat pakai rumus (x - min) / (max - min), biar skalanya jadi 0-1, sama seperti kolom lain yang sudah ternormalisasi di dataset ini (misalnya `city-L/100km`).

**Encoding di `num-of-doors` dan `num-of-cylinders`**
Karena isinya kata angka ("two", "four", dst), dibuat mapping manual ke integer beneran (`num-of-doors_encoded`, `num-of-cylinders_encoded`). Alasannya simpel: biar bisa langsung dipakai untuk hitung-hitungan numerik nanti, tanpa perlu decode kata dulu.

Contoh sebelum-sesudah:

| Kolom | Sebelum | Sesudah |
|---|---|---|
| `make` (baris 3) | `ALFA-ROMERO` | `alfa-romero` |
| `body-style` | campuran `SEDAN`/`Sedan` | `sedan` |
| `transaction_date` (baris 2) | `02/01/2025` | `2025-01-02` |
| `horsepower` (baris 2) | `111.0` | `horsepower_scaled` = `0.294393` |
| `num-of-doors` (baris 2) | `two` | `num-of-doors_encoded` = `2` |
| `num-of-cylinders` (baris 4) | `six` | `num-of-cylinders_encoded` = `6` |

## 7. Jumlah Data Sebelum/Sesudah Diproses
- Sebelum: 205 baris, 30 kolom
- Sesudah: 201 baris, 33 kolom (nambah 3 kolom baru hasil transformasi)

## 8. Cara Install Dependency
```bash
pip install -r requirements.txt
```

## 9. Cara Menjalankan Pipeline
Dari root folder project:
```bash
python src/pipeline.py
```
Proses inspeksi, cleaning, dan transformasi akan tampil di terminal, dan hasil akhirnya otomatis tersimpan di `data/processed/automobileEDA_processed.csv`.

## 10. Alur ETL
- **Extract** → `load_data()` baca CSV mentah dari `data/raw/`
- **Transform** → `inspect_data()` buat lihat masalah apa aja yang ada, `clean_data()` buat beresin, `transform_data()` buat scaling & encoding
- **Load** → `save_data()` simpan hasil akhir ke `data/processed/`, sementara dataset mentahnya sendiri nggak pernah diubah atau ditimpa.

## 11. Lokasi Processed Dataset
`data/processed/automobileEDA_processed.csv`
