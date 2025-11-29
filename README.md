# Sistem Deteksi Penyakit (Gejala → Penyakit)

Deskripsi singkat
-----------------
Aplikasi Streamlit ini membantu mendeteksi kemungkinan penyakit berdasarkan gejala yang dimasukkan pengguna. Aplikasi ini ditujukan untuk eksperimen dan referensi — bukan pengganti diagnosis medis profesional.

Fitur utama
-----------
- Deteksi penyakit berdasarkan gejala (pilihan checkbox atau input bebas / batch)
- Fuzzy matching untuk memetakan input teks bebas ke gejala yang sudah ada
- Opsi konfirmasi mapping sebelum gejala bebas dipetakan otomatis
- Rekomendasi pencegahan (jika tersedia di dataset)
- Hasil prediksi dapat diunduh: XLSX, CSV, JSON, TXT

Struktur proyek
---------------
- `app.py` — aplikasi utama Streamlit
- `assets/` — stylesheet, gambar, dan file mapping (`med_images.csv`)
- `data/` — dataset yang dipakai (mis. `DiseaseAndSymptoms.csv`, `Disease precaution.csv`)
- `requirements.txt` — daftar dependensi Python

Prasyarat
---------
- Python 3.8+ (direkomendasikan 3.10+)
- pip
- Disarankan menggunakan virtual environment

Instalasi (Windows PowerShell)
------------------------------
1. Buka PowerShell dan pindah ke folder proyek:

```powershell
cd 'C:\Users\ASUS\Documents\SEMESTER 5\Sistem Pendukung Keputusan\project'
```

2. (Opsional tapi disarankan) Buat virtual environment dan aktifkan:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

3. Instal dependensi:

```powershell
python -m pip install -r requirements.txt
```

4. Jalankan aplikasi:

```powershell
streamlit run app.py
```

Cara penggunaan singkat
-----------------------
1. Buka aplikasi di browser (biasanya http://localhost:8502).
2. Pilih gejala dari daftar atau masukkan beberapa gejala sekaligus di kotak teks (pisahkan dengan koma atau baris baru).
3. (Opsional) Di sidebar, atur "Ambang kecocokan fuzzy" dan aktifkan "Minta konfirmasi..." jika ingin memeriksa mapping manual.
4. Klik tombol "🔮 Prediksi Penyakit Saya".
5. Hasil akan tampil di bagian bawah. Gunakan tombol unduh untuk menyimpan hasil sebagai XLSX/CSV/JSON/TXT.

Format hasil unduhan
---------------------
File unduhan berisi kolom utama berikut:
- `Disease` — nama penyakit
- `Matched Symptoms` — jumlah gejala yang cocok
- `Matched Symptom Names` — daftar nama gejala yang cocok (dipisah `; `)
- `Total Symptoms` — total gejala yang ada di dataset untuk penyakit tersebut
- `Match Score` — skor kecocokan (0..1)

Catatan tentang data
--------------------
- Dataset utama berada di folder `data/`. Contoh file yang digunakan:
	- `DiseaseAndSymptoms.csv` — relasi penyakit → beberapa kolom `Symptom_1..Symptom_N`
	- `Disease precaution.csv` — rekomendasi pencegahan untuk beberapa penyakit
- Hindari menaruh file dataset yang sangat besar ke dalam folder `data/` karena dapat menyebabkan MemoryError pada mesin dengan RAM terbatas.

Troubleshooting (masalah umum)
-----------------------------
- Streamlit tidak mau jalan atau port sudah dipakai: jalankan `streamlit run app.py --server.port 8503` atau hentikan proses yang memakai port tersebut.
- Ekspor `.xlsx` gagal: pastikan `openpyxl` terpasang (`python -m pip install openpyxl`).
- CSV gagal dimuat: periksa encoding (UTF-8) dan format kolom pada file.

Kontribusi
----------
- Untuk menambah dataset, ikuti struktur kolom `Symptom_1..Symptom_N` seperti pada file contoh.
- Untuk menambah gambar obat/obat mapping, simpan file gambar di `assets/images/` dan tambahkan entri di `assets/med_images.csv`.
- Gunakan Git: buat branch baru, lakukan perubahan, dan buka Pull Request.

Lisensi
-------
Tentukan lisensi yang Anda kehendaki (misal: MIT). Jika belum yakin, saya bisa menambahkan teks lisensi MIT.

Kontak
------
Tambahkan alamat email atau username jika ingin menyediakan kontak dukungan.

-----

Jika mau, saya bisa menambahkan screenshot, contoh isi file `data/` atau menyesuaikan README agar cocok untuk presentasi tugas/praktikum — beri tahu detail yang ingin ditambahkan (mis. lisensi, kontak, atau screenshot). 

