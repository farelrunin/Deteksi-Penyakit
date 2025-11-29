import pandas as pd
import streamlit as st
import os
import urllib.parse
import difflib
import re
import io
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Configure page
st.set_page_config(
    page_title="Sistem Deteksi Penyakit",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load external CSS
def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load CSS dari folder assets
load_css('assets/styles.css')

# Fungsi untuk membersihkan nama gejala (ubah underscore jadi spasi, capitalize)
def clean_symptom_name(symptom):
    """Ubah format gejala dari 'abdominal_pain' menjadi 'Abdominal Pain'"""
    return symptom.replace('_', ' ').title() if isinstance(symptom, str) else symptom


# Helper: normalisasi nama penyakit menjadi nama file yang mungkin
def normalize_filename(name: str) -> str:
    """Lowercase, replace spaces with underscore, remove non-alnum except underscore"""
    if not isinstance(name, str):
        return ''
    fn = name.lower().strip()
    fn = fn.replace(' ', '_')
    # keep alnum and underscore
    fn = ''.join(c for c in fn if c.isalnum() or c == '_')
    return fn


# Cari file gambar untuk penyakit di folder assets/images
def find_image_file(disease_name: str):
    images_dir = os.path.join('assets', 'images')
    base = normalize_filename(disease_name)
    if not os.path.isdir(images_dir):
        return None
    for ext in ('.png', '.jpg', '.jpeg', '.webp', '.svg'):
        candidate = os.path.join(images_dir, base + ext)
        if os.path.isfile(candidate):
            return candidate
    return None


# Load optional mapping CSV (Disease -> ImageFile) to allow custom med images
@st.cache_data
def load_med_image_map():
    mapping_file = os.path.join('assets', 'med_images.csv')
    if not os.path.isfile(mapping_file):
        return {}
    try:
        df = pd.read_csv(mapping_file, encoding='utf-8')
        mp = {}
        for _, r in df.iterrows():
            if pd.isna(r.get('Disease')) or pd.isna(r.get('ImageFile')):
                continue
            mp[str(r['Disease']).strip().lower()] = os.path.join('assets', 'images', str(r['ImageFile']).strip())
        return mp
    except Exception:
        return {}


MED_IMAGE_MAP = load_med_image_map()


def get_image_for_disease(disease_name: str):
    """Return path to image: first check mapping, then disease-named file, else None"""
    if not isinstance(disease_name, str):
        return None
    key = disease_name.strip().lower()
    # mapping lookup
    if key in MED_IMAGE_MAP and os.path.isfile(MED_IMAGE_MAP[key]):
        return MED_IMAGE_MAP[key]
    # fallback to disease-named image
    return find_image_file(disease_name)


# Render results helper: accepts matching_diseases list and displays them
def render_results(matching_diseases):
    st.markdown(f'### ✅ Hasil Prediksi')
    st.markdown(f'**Ditemukan {len(matching_diseases)} penyakit yang mungkin**')
    st.write('---')
    for idx, result in enumerate(matching_diseases[:5], 1):
        disease_name = result['Disease']
        match_pct = result['Match Score'] * 100
        matched = result['Matched Symptoms']
        total = result['Total Symptoms']

        # Tentukan warna berdasarkan persentase
        if match_pct >= 75:
            color = "🔴"  # Tinggi
        elif match_pct >= 50:
            color = "🟠"  # Sedang
        else:
            color = "🟡"  # Rendah

        with st.container():
            col_rank, col_info, col_pct = st.columns([0.5, 3, 1])

            with col_rank:
                st.markdown(f"### {idx}")

            with col_info:
                img_file = get_image_for_disease(disease_name)
                if img_file:
                    try:
                        st.image(img_file, width=96)
                    except Exception:
                        placeholder = svg_placeholder_data_url(disease_name)
                        st.markdown(f"<img src=\"{placeholder}\" width=96 style=\"border-radius:8px\">", unsafe_allow_html=True)
                else:
                    placeholder = svg_placeholder_data_url(disease_name)
                    st.markdown(f"<img src=\"{placeholder}\" width=96 style=\"border-radius:8px\">", unsafe_allow_html=True)

                st.markdown(f"**{color} {disease_name}**")
                st.markdown(f"<small>Kecocokan: {matched}/{total} gejala</small>", unsafe_allow_html=True)

            with col_pct:
                st.markdown(f"<h3 style='text-align: center; color: #667eea;'>{match_pct:.0f}%</h3>", unsafe_allow_html=True)

            # Tampilkan pencegahan
            if not df_precaution.empty:
                precaution = df_precaution[df_precaution['Disease'].str.lower() == disease_name.lower()]
                if not precaution.empty:
                    st.markdown("**📋 Rekomendasi Pencegahan:**")
                    precautions = []
                    for col in ['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']:
                        if pd.notna(precaution.iloc[0][col]):
                            precautions.append(f"• {precaution.iloc[0][col]}")
                    st.markdown("\n".join(precautions))


# Jika tidak ada gambar file, buat SVG placeholder (data URL) dengan teks penyakit
def svg_placeholder_data_url(text: str, width=160, height=100):
    safe_text = urllib.parse.quote(text)
    svg = f"""
    <svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}' viewBox='0 0 {width} {height}'>
      <defs>
        <linearGradient id='g' x1='0' x2='1'>
          <stop stop-color='#667eea' offset='0'/>
          <stop stop-color='#764ba2' offset='1'/>
        </linearGradient>
      </defs>
      <rect width='100%' height='100%' rx='12' fill='url(#g)' opacity='0.95'/>
      <text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' font-family='Segoe UI, Roboto, Arial' font-size='14' fill='white'>{text}</text>
    </svg>
    """
    return 'data:image/svg+xml;utf8,' + urllib.parse.quote(svg)

# Fungsi untuk memuat data dari file CSV
@st.cache_data
def load_data():
    # Path file dataset penyakit
    try:
        # Hanya gunakan file yang tidak terlalu besar
        df_disease_symptoms = pd.read_csv('data/DiseaseAndSymptoms.csv', encoding='utf-8')
        df_precaution = pd.read_csv('data/Disease precaution.csv', encoding='utf-8')
        
        return df_disease_symptoms, df_precaution
    except Exception as e:
        st.error(f'Error loading data: {str(e)}')
        return pd.DataFrame(), pd.DataFrame()

# Memuat data
df_symptoms, df_precaution = load_data()

# Menampilkan informasi awal data — hero banner
st.markdown(f"""
<div class="hero">
    <div class="hero-inner">
        <div class="hero-brand">
            <div class="logo">🏥</div>
            <div>
                <h1>Sistem Deteksi Penyakit</h1>
                <p class="subtitle">Berdasarkan gejala yang Anda alami — pilih gejala, klik Prediksi, dapatkan rekomendasi pencegahan.</p>
            </div>
        </div>
        <div class="hero-metrics">
            <div class="metric-card"><h4>Total Data</h4><strong>{len(df_symptoms) if not df_symptoms.empty else 0}</strong></div>
            <div class="metric-card"><h4>Penyakit Unik</h4><strong>{df_symptoms['Disease'].nunique() if not df_symptoms.empty else 0}</strong></div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.write("---")

# Deskripsi singkat
col1, col2, col3 = st.columns(3)
with col1:
        st.markdown("### 📋 Fitur Utama")
        st.write("✓ Deteksi penyakit dari gejala")
        st.write("✓ Rekomendasi pencegahan")
        st.write("✓ Database 4900+ data gejala")

with col2:
        st.markdown("### ⚠️ Disclaimer")
        st.write("Aplikasi ini adalah untuk referensi saja.")
        st.write("Silakan konsultasi dengan dokter untuk diagnosis resmi.")

with col3:
        st.markdown("### 💡 Cara Penggunaan")
        st.write("1. Pilih gejala yang Anda alami")
        st.write("2. Klik tombol Prediksi")
        st.write("3. Lihat hasil dan pencegahan")

st.write("---")

if df_symptoms.empty:
    st.error('Tidak ada data yang dapat dimuat. Periksa file di folder data/')
else:
    # Tampilkan informasi dataset
    st.write('**Dataset yang digunakan:**')
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Data Gejala-Penyakit", len(df_symptoms))
    with col2:
        st.metric("Total Penyakit Unik", df_symptoms['Disease'].nunique())
    
    # Ekstrak semua gejala unik dari dataset
    all_symptoms = []
    for col in df_symptoms.columns:
        if col.startswith('Symptom_'):
            symptoms = df_symptoms[col].dropna().unique()
            all_symptoms.extend(symptoms)
    
    # Hapus duplikat
    all_symptoms = list(set(all_symptoms))
    
    # Bersihkan nama gejala dan sorting alfabet
    symptoms_clean = {clean_symptom_name(s): s for s in all_symptoms}  # Map clean name -> original
    all_symptoms_sorted = sorted(symptoms_clean.keys())
    
    st.write(f'**Total gejala yang dikenali: {len(all_symptoms_sorted)}**')

    # Kontrol di sidebar: ambang fuzzy dan konfirmasi sebelum mapping
    fuzzy_cutoff = st.sidebar.slider('Ambang kecocokan fuzzy', min_value=0.50, max_value=0.95, value=0.70, step=0.05)
    confirm_before_map = st.sidebar.checkbox('Minta konfirmasi sebelum memetakan otomatis', value=False)
    
    # Section untuk input gejala dengan styling
    st.write('---')
    st.markdown("## 🔍 Pilih Gejala Anda")
    st.markdown("**Centang semua gejala yang Anda rasakan:**")
    
    # Buat container dengan background
    # selected_symptoms didefinisikan di sini agar dapat digunakan juga untuk input manual di bawah
    selected_symptoms = []
    with st.container():
        # Buat multiple checkbox untuk gejala
        # Tampilkan gejala dalam kolom untuk kemudahan
        num_cols = 4
        cols = st.columns(num_cols)
        
        for idx, symptom_clean in enumerate(all_symptoms_sorted):
            col_idx = idx % num_cols
            with cols[col_idx]:
                if st.checkbox(symptom_clean, key=f"symptom_{symptom_clean}"):
                    # Simpan nama asli gejala (dengan underscore) untuk proses
                    selected_symptoms.append(symptoms_clean[symptom_clean])

    # Input manual untuk gejala yang tidak ada di daftar (boleh banyak, pisahkan dengan koma)
    st.markdown("---")
    st.markdown("**Gejala lain (tidak ada di daftar)?**")
    bulk_input = st.text_area('Masukkan satu atau lebih gejala, pisahkan dengan koma atau baris baru (mis. flu, pusing, demam ringan)')
    add_manual = st.button('Tambah Daftar Gejala')
    if add_manual and bulk_input.strip():
        # split by comma, semicolon or newline
        tokens = [t.strip() for t in re.split('[,;\n]+', bulk_input) if t.strip()]
        # pending entries used when confirm_before_map == True
        pending = []
        auto_mapped = []
        added = []
        ambiguous = []

        for tok in tokens:
            tok_clean_display = clean_symptom_name(tok)
            matches = difflib.get_close_matches(tok_clean_display, all_symptoms_sorted, n=5, cutoff=float(fuzzy_cutoff))
            entry = {
                'token': tok,
                'display': tok_clean_display,
                'matches': matches
            }
            pending.append(entry)

        if confirm_before_map:
            # simpan pending di session_state agar bisa dikonfirmasi
            st.session_state['pending_mappings'] = pending
            st.markdown('**Pratinjau mapping — pilih tindakan untuk setiap input:**')
            selections = []
            for i, e in enumerate(pending):
                label = f"Input: {e['token']}"
                options = ['__TAMBAHKAN_MANUAL__'] + e['matches'] if e['matches'] else ['__TAMBAHKAN_MANUAL__']
                choice = st.selectbox(label, options, index=1 if len(options) > 1 else 0, key=f"pending_choice_{i}")
                selections.append((e, choice))

            if st.button('Konfirmasi mapping dan tambahkan ke gejala terpilih'):
                for e, choice in selections:
                    tok = e['token']
                    if choice == '__TAMBAHKAN_MANUAL__':
                        manual_key = tok.lower().replace(' ', '_')
                        selected_symptoms.append(manual_key)
                        added.append((tok, manual_key))
                    else:
                        original = symptoms_clean.get(choice)
                        if original:
                            selected_symptoms.append(original)
                            auto_mapped.append((tok, choice))
                        else:
                            manual_key = tok.lower().replace(' ', '_')
                            selected_symptoms.append(manual_key)
                            added.append((tok, manual_key))

                if auto_mapped:
                    st.success(f"Mapped {len(auto_mapped)} input ke gejala yang dikenal: {', '.join(f'{a}→{b}' for a,b in auto_mapped)}")
                if added:
                    st.info(f"Ditambahkan {len(added)} gejala manual: {', '.join(a for a,_ in added)}")
                # clear pending
                st.session_state.pop('pending_mappings', None)

        else:
            # langsung lakukan mapping otomatis berdasarkan ambang fuzzy_cutoff
            for e in pending:
                tok = e['token']
                matches = e['matches']
                if matches:
                    top = matches[0]
                    original = symptoms_clean.get(top)
                    if original:
                        selected_symptoms.append(original)
                        auto_mapped.append((tok, top))
                    else:
                        manual_key = tok.lower().replace(' ', '_')
                        selected_symptoms.append(manual_key)
                        added.append((tok, manual_key))
                    if len(matches) > 1:
                        ambiguous.append((tok, matches))
                else:
                    manual_key = tok.lower().replace(' ', '_')
                    selected_symptoms.append(manual_key)
                    added.append((tok, manual_key))

            # feedback ke user
            if auto_mapped:
                st.success(f"Mapped {len(auto_mapped)} input ke gejala yang dikenal: {', '.join(f'{a}→{b}' for a,b in auto_mapped)}")
            if added:
                st.info(f"Ditambahkan {len(added)} gejala manual: {', '.join(a for a,_ in added)}")
            if ambiguous:
                st.warning('Beberapa input memiliki kemungkinan kecocokan lain:')
                for tok, options in ambiguous:
                    st.write(f"- {tok}: kemungkinan -> {', '.join(options)}")
    
    # Tombol untuk prediksi dengan styling
    st.write('---')
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button('🔮 Prediksi Penyakit Saya', use_container_width=True, type='primary'):
            if len(selected_symptoms) == 0:
                st.warning('⚠️ Silakan pilih minimal 1 gejala terlebih dahulu!')
            else:
                # Tampilkan gejala yang dipilih dengan nama yang bersih
                selected_symptoms_clean = [clean_symptom_name(s) for s in selected_symptoms]
                st.markdown(f'**Gejala yang dipilih:** {", ".join(selected_symptoms_clean)}')
                st.write('---')
                
                # Cari penyakit yang cocok dengan gejala
                # Agregasi per penyakit: gabungkan semua baris yang sama menjadi satu set gejala
                disease_symptom_map = {}
                for _, row in df_symptoms.iterrows():
                    disease = row.get('Disease')
                    if pd.isna(disease):
                        continue
                    disease = str(disease).strip()
                    if disease not in disease_symptom_map:
                        disease_symptom_map[disease] = set()
                    for col in df_symptoms.columns:
                        if col.startswith('Symptom_') and pd.notna(row[col]):
                            disease_symptom_map[disease].add(row[col])

                matching_diseases = []
                for disease, disease_symptoms in disease_symptom_map.items():
                    if not disease_symptoms:
                        continue
                    matches = set(selected_symptoms).intersection(disease_symptoms)
                    if not matches:
                        continue
                    match_count = len(matches)
                    total_count = len(disease_symptoms)
                    match_score = match_count / total_count if total_count > 0 else 0
                    # buat list nama gejala yang match (dalam bentuk bersih)
                    matched_names = [clean_symptom_name(s) for s in matches]
                    matching_diseases.append({
                        'Disease': disease,
                        'Matched Symptoms': match_count,
                        'Matched Symptom Names': '; '.join(sorted(matched_names)),
                        'Total Symptoms': total_count,
                        'Match Score': match_score
                    })
                
                if matching_diseases:
                    # Sort by match score
                    matching_diseases = sorted(matching_diseases, key=lambda x: x['Match Score'], reverse=True)
                    # Render results (selalu tampil di bawah)
                    render_results(matching_diseases)

                    # Siapkan DataFrame hasil untuk diunduh
                    try:
                        df_results = pd.DataFrame(matching_diseases)
                    except Exception:
                        df_results = None

                    if df_results is not None and not df_results.empty:
                        st.markdown('---')
                        st.markdown('**Unduh hasil prediksi**')
                        # Excel (.xlsx)
                        try:
                            to_xlsx = io.BytesIO()
                            with pd.ExcelWriter(to_xlsx, engine='openpyxl') as writer:
                                df_results.to_excel(writer, index=False, sheet_name='Hasil')
                            to_xlsx.seek(0)
                            st.download_button(label='Unduh Excel (.xlsx)', data=to_xlsx, file_name='hasil_prediksi.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                        except Exception:
                            st.warning('Ekspor .xlsx gagal (mungkin dependency openpyxl tidak terpasang). Gunakan CSV sebagai alternatif.')

                        # CSV
                        csv_bytes = df_results.to_csv(index=False).encode('utf-8')
                        st.download_button(label='Unduh CSV', data=csv_bytes, file_name='hasil_prediksi.csv', mime='text/csv')

                        # JSON
                        json_str = df_results.to_json(orient='records', force_ascii=False)
                        st.download_button(label='Unduh JSON', data=json_str, file_name='hasil_prediksi.json', mime='application/json')

                        # Plain text summary (termasuk nama-nama gejala yang cocok)
                        txt_lines = []
                        for i, r in enumerate(matching_diseases, 1):
                            matched_names = r.get('Matched Symptom Names', '')
                            txt_lines.append(f"{i}. {r['Disease']} - {r['Matched Symptoms']}/{r['Total Symptoms']} ({r['Match Score']:.2f})\n    Gejala cocok: {matched_names}")
                        txt = '\n\n'.join(txt_lines)
                        st.download_button(label='Unduh TXT (ringkasan)', data=txt, file_name='hasil_prediksi.txt', mime='text/plain')
                else:
                    st.warning('⚠️ Tidak ada penyakit yang cocok dengan gejala yang dipilih. Silakan coba gejala lain.')
