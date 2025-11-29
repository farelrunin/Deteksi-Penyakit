# Deployment ke Streamlit Share

Panduan lengkap cara deploy aplikasi ke Streamlit Cloud (Streamlit Share).

## Prasyarat

- GitHub account (sudah ada: farelrunin)
- Repository di GitHub (sudah ada: Deteksi-Penyakit)
- Streamlit account (bisa login dengan GitHub)

## Langkah Deployment

### 1. Login ke Streamlit Community Cloud

1. Buka: https://streamlit.io/cloud
2. Klik "Sign in with GitHub"
3. Autentikasi dengan akun GitHub kamu (farelrunin)

### 2. Deploy Repository

1. Di Streamlit Community Cloud, klik "Create app"
2. Pilih:
   - **Repository:** farelrunin/Deteksi-Penyakit
   - **Branch:** main
   - **Main file path:** app.py
3. Klik "Deploy!"

Tunggu proses build selesai (biasanya 2-5 menit). URL app kamu akan seperti:
```
https://deteksi-penyakit.streamlit.app
```

### 3. Otomatis Update dari GitHub

**Bagus kabarnya: Streamlit Share otomatis pull perubahan terbaru dari GitHub!**

Setiap kali kamu:
1. Edit file lokal
2. Push ke GitHub (`git push origin main`)

Streamlit Cloud **otomatis akan rebuild dan update** aplikasi di server.

Waktu deploy ulang biasanya 30 detik - 5 menit tergantung ukuran perubahan.

## Monitoring Deployment

1. Buka https://streamlit.io/cloud
2. Pilih app kamu "Deteksi-Penyakit"
3. Lihat status build dan log di tab "Logs"

## Environment Variables & Secrets

Jika app butuh API key atau password:

1. Buka settings app di Streamlit Cloud
2. Tambah secrets di "Secrets" section
3. Gunakan di `app.py`:
   ```python
   import streamlit as st
   api_key = st.secrets["api_key"]
   ```

Untuk project ini, tidak perlu secrets.

## Troubleshooting Deployment

**Error: "ModuleNotFoundError: No module named 'openpyxl'"**
- File `requirements.txt` belum ter-update
- Solusi: Pastikan `requirements.txt` berisi `openpyxl`, push ke GitHub, maka akan rebuild

**Error: "FileNotFoundError: assets/styles.css"**
- Streamlit tidak menemukan file CSS
- Solusi: Pastikan file ada di repository dan `load_css('assets/styles.css')` path benar

**App hang/timeout saat prediksi**
- Mungkin dataset CSV terlalu besar untuk di-load
- Solusi: Gunakan `@st.cache_data` untuk caching (sudah diterapkan)

## Monitoring & Analytics

Di dashboard Streamlit Cloud, kamu bisa lihat:
- Jumlah viewers
- App health status
- Runtime memory & CPU usage
- Browser compatibility

## Redeploy Manual

Jika perlu force redeploy tanpa perubahan kode:
1. Buka settings app
2. Klik "Reboot app"

## Membatalkan/Menghapus Deployment

1. Di Streamlit Cloud dashboard
2. Pilih app kamu
3. Klik "Settings" → "Delete app"

## Tips & Best Practices

1. **Test lokal dulu** sebelum push ke GitHub
   ```bash
   streamlit run app.py
   ```

2. **Update requirements.txt** jika install package baru
   ```bash
   pip freeze > requirements.txt
   ```

3. **Gunakan Git LFS** untuk file besar (sudah diterapkan untuk CSV 181 MB)

4. **Monitor app logs** untuk error production

5. **Set app privacy** di Streamlit Cloud settings (public/private)

## Jika Ada Update ke Aplikasi

**Flow update otomatis:**
```
Edit lokal → git add . → git commit → git push origin main
                                              ↓
                        Streamlit Cloud detect perubahan
                                              ↓
                        Auto rebuild & deploy (30 sec - 5 min)
                                              ↓
                        App live dengan versi terbaru!
```

Kamu tidak perlu melakukan apa-apa lagi — semuanya otomatis!

---

**Dokumentasi lengkap Streamlit Community Cloud:**
https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app
