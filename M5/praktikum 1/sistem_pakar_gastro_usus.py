# ============================================================
# KNOWLEDGE BASE — Basis Pengetahuan Sistem Pakar Gastro Usus
# ============================================================

# Daftar gejala (symptom_id: deskripsi pertanyaan)
# Nomor mengacu pada indeks gejala dari soal praktikum
GEJALA = {
    'G01': 'Apakah Anda sering buang air besar (lebih dari 2 kali)?',
    'G02': 'Apakah Anda mengalami berak encer (mencret)?',
    'G03': 'Apakah Anda mengalami berak berdarah?',
    'G04': 'Apakah Anda merasa lesu dan tidak bergairah?',
    'G05': 'Apakah Anda tidak selera makan?',
    'G06': 'Apakah Anda merasa mual dan sering muntah (lebih dari 1 kali)?',
    'G07': 'Apakah Anda merasa sakit di bagian perut?',
    'G08': 'Apakah tekanan darah Anda rendah?',
    'G09': 'Apakah Anda merasa pusing?',
    'G10': 'Apakah Anda pernah pingsan?',
    'G11': 'Apakah suhu badan Anda tinggi (demam)?',
    'G12': 'Apakah Anda memiliki luka di bagian tertentu?',
    'G13': 'Apakah Anda tidak dapat menggerakkan anggota badan tertentu (lumpuh)?',
    'G14': 'Apakah Anda baru saja memakan sesuatu yang mencurigakan?',
    'G15': 'Apakah Anda memakan daging (terutama daging yang tidak dimasak sempurna)?',
    'G16': 'Apakah Anda memakan jamur?',
    'G17': 'Apakah Anda memakan makanan kaleng?',
    'G18': 'Apakah Anda membeli atau meminum susu?',
}

import json
import webbrowser
from pathlib import Path

# ============================================================
# RULES — Aturan Diagnosis (Knowledge Representation)
# Setiap penyakit didefinisikan dengan:
#   - nama: nama penyakit
#   - gejala_utama: gejala yang WAJIB ada (bobot tinggi)
#   - gejala_pendukung: gejala tambahan yang memperkuat diagnosis
#   - total_gejala: total gejala yang dipertimbangkan (untuk menghitung persentase)
# ============================================================

RULES = {
    'P33': {
        'nama': 'Keracunan Staphylococcus aureus',
        'deskripsi': 'Keracunan yang disebabkan oleh toksin bakteri Staphylococcus aureus '
                    'pada makanan. Biasanya terjadi 1-6 jam setelah makan makanan yang terkontaminasi.',
        'gejala_utama':     ['G06', 'G07', 'G14'],   # muntah, sakit perut, makan sesuatu
        'gejala_pendukung': ['G01', 'G02', 'G04', 'G05', 'G08', 'G09'],
        'saran': 'Istirahat, minum banyak cairan untuk cegah dehidrasi. Jika muntah berlebihan, segera ke dokter.'
    },
    'P34': {
        'nama': 'Keracunan Jamur Beracun',
        'deskripsi': 'Keracunan akibat memakan jamur beracun. Gejalanya dapat muncul '
                    'beberapa jam hingga beberapa hari setelah konsumsi.',
        'gejala_utama':     ['G16', 'G06', 'G07'],   # makan jamur, muntah, sakit perut
        'gejala_pendukung': ['G01', 'G02', 'G04', 'G05', 'G08', 'G09', 'G10', 'G11'],
        'saran': 'SEGERA ke UGD rumah sakit! Keracunan jamur bisa berbahaya. Bawa sisa jamur yang dimakan jika ada.'
    },
    'P35': {
        'nama': 'Keracunan Salmonellae',
        'deskripsi': 'Infeksi bakteri Salmonella yang sering berasal dari daging, '
                    'telur, atau produk susu yang tidak matang/tidak higienis.',
        'gejala_utama':     ['G15', 'G01', 'G11'],   # makan daging, mencret, demam
        'gejala_pendukung': ['G02', 'G03', 'G06', 'G07', 'G04', 'G08', 'G12'],
        'saran': 'Konsumsi oralit untuk mencegah dehidrasi, istirahat cukup. Segera ke dokter jika ada darah pada tinja atau demam tinggi.'
    },
    'P36': {
        'nama': 'Keracunan Clostridium botulinum',
        'deskripsi': 'Keracunan serius akibat toksin bakteri Clostridium botulinum '
                    'yang umumnya berasal dari makanan kaleng yang tidak diproses dengan benar.',
        'gejala_utama':     ['G17', 'G13', 'G06'],   # makan kaleng, lumpuh, muntah
        'gejala_pendukung': ['G01', 'G07', 'G08', 'G09', 'G10', 'G04', 'G05'],
        'saran': 'DARURAT MEDIS! Segera ke IGD. Clostridium botulinum dapat menyebabkan kelumpuhan pernapasan yang mengancam jiwa.'
    },
    'P37': {
        'nama': 'Keracunan Campylobacter',
        'deskripsi': 'Infeksi bakteri Campylobacter, umumnya dari produk susu mentah '
                    'atau unggas yang tidak dimasak sempurna.',
        'gejala_utama':     ['G18', 'G03', 'G11'],   # minum susu, berak berdarah, demam
        'gejala_pendukung': ['G01', 'G02', 'G07', 'G04', 'G06', 'G09'],
        'saran': 'Istirahat, jaga hidrasi. Konsultasi dokter untuk pemberian antibiotik jika diperlukan.'
    },
}

print("✅ Knowledge base berhasil dimuat.")
print(f"   - Jumlah gejala  : {len(GEJALA)} gejala")
print(f"   - Jumlah penyakit: {len(RULES)} penyakit")

# ============================================================
# INFERENCE ENGINE — Mesin Inferensi Forward Chaining
# ============================================================

def hitung_confidence(fakta_user: set, rule: dict) -> float:
    """
    Menghitung confidence score suatu penyakit berdasarkan fakta user.
    
    Metode:
    - Gejala utama yang cocok  → bobot 2
    - Gejala pendukung cocok   → bobot 1
    - Skor maksimum = (len(utama) * 2) + len(pendukung)
    
    Args:
        fakta_user (set): Kumpulan kode gejala yang dimiliki user
        rule (dict): Rule penyakit dari knowledge base
    
    Returns:
        float: Persentase confidence (0.0 - 100.0)
    """
    gejala_utama     = set(rule['gejala_utama'])
    gejala_pendukung = set(rule['gejala_pendukung'])
    
    # Skor maksimum yang bisa diraih
    skor_max = len(gejala_utama) * 2 + len(gejala_pendukung) * 1
    
    # Hitung skor aktual berdasarkan fakta user
    skor_utama     = len(fakta_user & gejala_utama) * 2
    skor_pendukung = len(fakta_user & gejala_pendukung) * 1
    skor_aktual    = skor_utama + skor_pendukung
    
    if skor_max == 0:
        return 0.0
    
    return round((skor_aktual / skor_max) * 100, 2)


def inferensi(fakta_user: set, threshold: float = 30.0) -> tuple[list[dict], list[dict]]:
    """
    Melakukan inferensi forward chaining terhadap seluruh rules.
    
    Args:
        fakta_user (set): Kumpulan kode gejala yang dimiliki user
        threshold (float): Batas minimum confidence untuk ditampilkan (%)
    
    Returns:
        list: Daftar tuple (nama_penyakit, confidence, saran) diurutkan descending
    """
    hasil = []
    
    for kode, rule in RULES.items():
        confidence = hitung_confidence(fakta_user, rule)
        hasil.append({
            'kode'       : kode,
            'nama'       : rule['nama'],
            'deskripsi'  : rule['deskripsi'],
            'confidence' : confidence,
            'saran'      : rule['saran'],
        })
    
    # Urutkan dari confidence tertinggi
    hasil.sort(key=lambda x: x['confidence'], reverse=True)
    
    # Filter hanya yang melewati threshold
    hasil_filtered = [h for h in hasil if h['confidence'] >= threshold]
    
    return hasil_filtered, hasil  # kembalikan juga semua untuk keperluan debug


print("✅ Inference engine berhasil dimuat.")
# ============================================================
# USER INTERFACE — Antarmuka Interaktif
# ============================================================

def tampilkan_header():
    """Menampilkan header/judul sistem pakar."""
    print("=" * 65)
    print("  SISTEM PAKAR IDENTIFIKASI INFEKSI SISTEM GASTRO-USUS")
    print("  Berbasis Rule-Based Expert System | Forward Chaining")
    print("=" * 65)
    print()
    print("Sistem ini akan menanyakan beberapa gejala yang Anda alami.")
    print("Jawab dengan: y (ya) atau n (tidak)")
    print()


def kumpulkan_gejala() -> set:
    """
    Mengumpulkan fakta dari user melalui sesi tanya-jawab interaktif.
    
    Returns:
        set: Himpunan kode gejala yang dialami user
    """
    fakta = set()
    total = len(GEJALA)
    
    print(f"📋 Silakan jawab {total} pertanyaan berikut:")
    print("-" * 65)
    
    for i, (kode, pertanyaan) in enumerate(GEJALA.items(), start=1):
        while True:
            jawaban = input(f"[{i:02d}/{total}] {pertanyaan} (y/n): ").strip().lower()
            if jawaban in ('y', 'n', 'ya', 'tidak', 'yes', 'no'):
                break
            print("       ⚠️  Masukkan hanya 'y' atau 'n'")
        
        if jawaban in ('y', 'ya', 'yes'):
            fakta.add(kode)
    
    return fakta


def tampilkan_hasil(hasil_filtered: list, semua_hasil: list, threshold: float):
    """
    Menampilkan hasil diagnosis kepada pengguna.
    
    Args:
        hasil_filtered : Hasil diagnosis yang melewati threshold
        semua_hasil    : Semua hasil (untuk menampilkan rekap)
        threshold      : Nilai threshold yang digunakan
    """
    print()
    print("=" * 65)
    print("  📊 HASIL DIAGNOSIS")
    print("=" * 65)
    
    # Tampilkan semua persentase (ringkasan)
    print("\n📈 Rekap Confidence Semua Penyakit:")
    print("-" * 45)
    for h in semua_hasil:
        bar_len  = int(h['confidence'] / 5)  # max 20 karakter
        bar      = '█' * bar_len + '░' * (20 - bar_len)
        marker   = ' ✅' if h['confidence'] >= threshold else ''
        print(f"  {h['nama']:<40} : {h['confidence']:5.1f}%{marker}")
        print(f"  {bar}")
    
    print()
    print(f"  (Threshold: {threshold}%)")
    print("-" * 65)
    
    if not hasil_filtered:
        print()
        print("  ℹ️  Tidak ada diagnosis yang memenuhi threshold.")
        print("     Kemungkinan gejala yang Anda alami tidak spesifik.")
        print("     Disarankan untuk berkonsultasi langsung dengan dokter.")
    else:
        # Diagnosis utama (confidence tertinggi)
        utama = hasil_filtered[0]
        print()
        print(f"  🏆 Diagnosis Utama:")
        print(f"     ➤ {utama['nama']}")
        print(f"     Confidence: {utama['confidence']}%")
        print()
        print(f"  📖 Deskripsi:")
        # Wrap teks agar rapi
        import textwrap
        desc_wrapped = textwrap.fill(utama['deskripsi'], width=58,
                                     initial_indent='     ',
                                     subsequent_indent='     ')
        print(desc_wrapped)
        print()
        print(f"  💡 Saran:")
        saran_wrapped = textwrap.fill(utama['saran'], width=58,
                                      initial_indent='     ',
                                      subsequent_indent='     ')
        print(saran_wrapped)
        
        # Tampilkan kemungkinan lain jika ada
        if len(hasil_filtered) > 1:
            print()
            print("  ⚠️  Kemungkinan penyakit lain yang perlu dipertimbangkan:")
            for h in hasil_filtered[1:]:
                print(f"     • {h['nama']} ({h['confidence']}%)")
    
    print()
    print("=" * 65)
    print("  ⚕️  PERHATIAN: Hasil ini hanya bersifat informatif.")
    print("      Konsultasikan dengan dokter untuk diagnosis resmi.")
    print("=" * 65)


print("✅ User interface berhasil dimuat.")
# ============================================================
# MAIN PROGRAM — Jalankan Sistem Pakar
# ============================================================

def jalankan_sistem_pakar(threshold: float = 30.0):
    """
    Fungsi utama untuk menjalankan sistem pakar secara interaktif.
    
    Args:
        threshold (float): Batas minimum confidence untuk ditampilkan (%)
    """
    tampilkan_header()
    
    # Fase 1: Kumpulkan gejala dari user
    fakta_user = kumpulkan_gejala()
    
    print()
    print(f"  📝 Gejala yang Anda tandai: {len(fakta_user)} dari {len(GEJALA)}")
    if fakta_user:
        gejala_terpilih = [GEJALA[k][:50] + '...' if len(GEJALA[k]) > 50 else GEJALA[k]
                           for k in sorted(fakta_user)]
        for g in gejala_terpilih:
            print(f"     ✓ {g}")
    
    # Fase 2: Inferensi (forward chaining)
    print()
    print("  🔄 Memproses inference engine...")
    hasil_filtered, semua_hasil = inferensi(fakta_user, threshold)
    
    # Fase 3: Tampilkan hasil
    tampilkan_hasil(hasil_filtered, semua_hasil, threshold)


# ============================================================
# UNIT TESTING — Pengujian Skenario Gejala (opsional)
# ============================================================

def jalankan_pengujian_skenario() -> None:
    skenario_uji = [
        {
            'nama': 'Skenario A - Dugaan Staphylococcus',
            'gejala': {'G06', 'G07', 'G14', 'G04', 'G05'},
            'ekspektasi': 'P33'
        },
        {
            'nama': 'Skenario B - Dugaan Clostridium botulinum',
            'gejala': {'G17', 'G13', 'G06', 'G09', 'G08'},
            'ekspektasi': 'P36'
        },
        {
            'nama': 'Skenario C - Dugaan Campylobacter',
            'gejala': {'G18', 'G03', 'G11', 'G01', 'G07'},
            'ekspektasi': 'P37'
        },
        {
            'nama': 'Skenario D - Dugaan Salmonellae',
            'gejala': {'G15', 'G01', 'G11', 'G02', 'G06'},
            'ekspektasi': 'P35'
        },
        {
            'nama': 'Skenario E - Gejala Minim (tidak spesifik)',
            'gejala': {'G04'},
            'ekspektasi': None
        },
    ]

    print("=" * 65)
    print("  HASIL PENGUJIAN SKENARIO")
    print("=" * 65)

    for skenario in skenario_uji:
        hasil_filtered, semua_hasil = inferensi(skenario['gejala'], threshold=30.0)
        print(f"\n- {skenario['nama']}")
        if hasil_filtered:
            top = hasil_filtered[0]
            status = "BENAR" if top['kode'] == skenario['ekspektasi'] else "BERBEDA"
            print(f"  Top: {top['kode']} - {top['nama']} ({top['confidence']}%) [{status}]")
        else:
            status = "BENAR" if skenario['ekspektasi'] is None else "BERBEDA"
            print(f"  Top: Tidak ada diagnosis [{status}]")


def jalankan_visualisasi_browser() -> None:
        gejala_js = json.dumps(GEJALA, ensure_ascii=False)
        rules_js = json.dumps(RULES, ensure_ascii=False)

        html_content = f"""<!doctype html>
<html lang=\"id\">
<head>
    <meta charset=\"utf-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
    <title>Sistem Pakar Gastro Usus</title>
    <style>
        body {{
            margin: 0;
            background: #d9d9d9;
            font-family: Tahoma, Arial, sans-serif;
            color: #111;
        }}
        .window {{
            width: min(1180px, calc(100vw - 24px));
            height: min(760px, calc(100vh - 24px));
            margin: 12px auto;
            border: 1px solid #777;
            background: #f2f2f2;
            display: grid;
            grid-template-columns: 64% 36%;
            grid-template-rows: 1fr auto;
            gap: 0;
        }}
        .left {{
            background: #fff44d;
            border-right: 1px solid #8a8a8a;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}
        .left .list {{
            overflow-y: auto;
            padding: 8px 10px 10px;
        }}
        .right {{
            background: #efefef;
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}
        .right .result {{
            white-space: pre-wrap;
            font-size: 26px;
            line-height: 1.36;
            padding: 10px 12px;
            overflow-y: auto;
            margin: 0;
            font-family: Tahoma, Arial, sans-serif;
        }}
        .bottom {{
            grid-column: 1 / span 2;
            border-top: 1px solid #8a8a8a;
            background: #ddd;
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 6px 10px;
            font-size: 24px;
            flex-wrap: wrap;
        }}
        .spacer {{
            flex: 1;
        }}
        .diagnosis {{
            color: #b10000;
            font-weight: bold;
        }}
        .row {{
            display: flex;
            align-items: center;
            gap: 6px;
            margin: 3px 0;
            font-size: 23px;
        }}
        input[type=\"checkbox\"] {{
            width: 18px;
            height: 18px;
            accent-color: #d9d9d9;
        }}
        input[type=\"number\"] {{
            width: 70px;
            height: 34px;
            font-size: 22px;
            padding: 2px 4px;
        }}
        button {{
            font-size: 22px;
            padding: 4px 14px;
            cursor: pointer;
        }}
        @media (max-width: 900px) {{
            .window {{
                height: auto;
                grid-template-columns: 1fr;
                grid-template-rows: 56vh 32vh auto;
            }}
            .bottom {{
                grid-column: 1;
                font-size: 18px;
            }}
            .row {{ font-size: 16px; }}
            .right .result {{ font-size: 16px; }}
            button, input[type=\"number\"] {{ font-size: 16px; }}
        }}
    </style>
</head>
<body>
    <div class=\"window\">
        <section class=\"left\">
            <div id=\"list\" class=\"list\"></div>
        </section>
        <section class=\"right\">
            <pre id=\"result\" class=\"result\">Pilih gejala lalu klik Proses.</pre>
        </section>
        <section class=\"bottom\">
            <span>Threshold</span>
            <input id=\"threshold\" type=\"number\" min=\"0\" max=\"100\" value=\"30\">
            <span>%</span>
            <button id=\"proses\" type=\"button\">Proses</button>
            <span class=\"spacer\"></span>
            <span>Anda terkena infeksi:</span>
            <span id=\"top\" class=\"diagnosis\">-</span>
        </section>
    </div>

    <script>
        const GEJALA = {gejala_js};
        const RULES = {rules_js};

        const listEl = document.getElementById('list');
        const resultEl = document.getElementById('result');
        const topEl = document.getElementById('top');

        function renderGejala() {{
            Object.entries(GEJALA).forEach(([kode, pertanyaan]) => {{
                const row = document.createElement('label');
                row.className = 'row';
                row.innerHTML = `<input type=\"checkbox\" data-kode=\"${{kode}}\"> <span>${{pertanyaan}}</span>`;
                listEl.appendChild(row);
            }});
        }}

        function hitungConfidence(fakta, rule) {{
            const utama = new Set(rule.gejala_utama);
            const pendukung = new Set(rule.gejala_pendukung);
            const skorMax = (utama.size * 2) + pendukung.size;
            let skor = 0;
            fakta.forEach((kode) => {{
                if (utama.has(kode)) skor += 2;
                else if (pendukung.has(kode)) skor += 1;
            }});
            if (skorMax === 0) return 0;
            return Number(((skor / skorMax) * 100).toFixed(2));
        }}

        function proses() {{
            const threshold = Number(document.getElementById('threshold').value);
            if (Number.isNaN(threshold) || threshold < 0 || threshold > 100) {{
                alert('Threshold harus angka 0-100.');
                return;
            }}

            const fakta = new Set(
                Array.from(document.querySelectorAll('input[data-kode]:checked')).map((el) => el.dataset.kode)
            );

            const hasil = Object.entries(RULES).map(([kode, rule]) => {{
                const confidence = hitungConfidence(fakta, rule);
                return {{ kode, nama: rule.nama, confidence }};
            }}).sort((a, b) => b.confidence - a.confidence);

            const lines = hasil.map((h) => `${{h.nama.replace('Keracunan ', '')}} : ${{h.confidence.toFixed(2)}} %`);
            resultEl.textContent = lines.join('\\n');

            const top = hasil.find((h) => h.confidence >= threshold);
            topEl.textContent = top ? top.nama : 'Tidak terdeteksi';
        }}

        document.getElementById('proses').addEventListener('click', proses);
        renderGejala();
    </script>
</body>
</html>
"""

        output_html = Path(__file__).with_name('sistem_pakar_gui_browser.html')
        output_html.write_text(html_content, encoding='utf-8')

        webbrowser.open(output_html.resolve().as_uri())
        print(f"✅ GUI browser dibuka: {output_html.name}")


if __name__ == '__main__':
    jalankan_visualisasi_browser()