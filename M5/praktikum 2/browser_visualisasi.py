#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Visualisasi Browser - Sistem Pakar Diagnosa Penyakit Saluran Pernapasan
GUI interaktif berbasis browser dengan HTML + JavaScript
"""

import json
import webbrowser
from pathlib import Path

# ============================================================
# KNOWLEDGE BASE — Gejala dan Penyakit
# ============================================================

GEJALA_MAP = {
    'demam': 'Apakah Anda mengalami demam (suhu > 37.5°C)?',
    'demam_tinggi': 'Apakah demam Anda sangat tinggi (suhu > 39°C)?',
    'menggigil': 'Apakah Anda merasa menggigil?',
    'batuk': 'Apakah Anda mengalami batuk?',
    'batuk_berdahak': 'Apakah batuk Anda berdahak (berwarna kuning/hijau)?',
    'batuk_kering': 'Apakah batuk Anda kering (tanpa dahak)?',
    'batuk_persisten': 'Apakah batuk Anda sudah berlangsung lebih dari 2 minggu?',
    'sesak_napas': 'Apakah Anda merasa sesak napas atau kesulitan bernapas?',
    'sesak_berat': 'Apakah sesak napas terasa sangat berat (sulit berbicara)?',
    'pilek': 'Apakah Anda mengalami pilek atau hidung meler?',
    'hidung_tersumbat': 'Apakah hidung Anda tersumbat?',
    'bersin': 'Apakah Anda sering bersin-bersin?',
    'nyeri_otot': 'Apakah Anda mengalami nyeri atau pegal pada otot/sendi?',
    'sakit_kepala': 'Apakah Anda mengalami sakit kepala?',
    'kelelahan': 'Apakah Anda merasa sangat lelah atau lemas?',
    'sakit_tenggorokan': 'Apakah Anda mengalami sakit atau nyeri tenggorokan?',
    'hilang_penciuman': 'Apakah Anda kehilangan kemampuan mencium bau (anosmia)?',
    'hilang_perasa': 'Apakah Anda kehilangan kemampuan merasakan makanan (ageusia)?',
    'nyeri_dada': 'Apakah Anda merasakan nyeri atau rasa berat di dada?',
    'dahak_berdarah': 'Apakah dahak Anda disertai darah?',
}

RULES_BROWSER = {
    'Common Cold (Pilek Biasa)': {
        'gejala_utama': ['pilek', 'bersin', 'hidung_tersumbat'],
        'gejala_pendukung': ['sakit_tenggorokan', 'demam'],
        'deskripsi': 'Infeksi virus ringan pada saluran pernapasan atas. Biasanya sembuh sendiri dalam 7–10 hari.'
    },
    'Flu (Influenza)': {
        'gejala_utama': ['demam', 'batuk', 'nyeri_otot', 'sakit_kepala'],
        'gejala_pendukung': ['kelelahan', 'pilek', 'sakit_tenggorokan'],
        'deskripsi': 'Infeksi virus influenza yang menyerang saluran pernapasan atas. Biasanya berlangsung 5–7 hari.'
    },
    'Bronkitis': {
        'gejala_utama': ['batuk_berdahak', 'batuk_persisten', 'sesak_napas'],
        'gejala_pendukung': ['batuk', 'nyeri_dada', 'demam'],
        'deskripsi': 'Peradangan pada saluran bronkus yang menyebabkan batuk berdahak persisten.'
    },
    'COVID-19': {
        'gejala_utama': ['demam', 'batuk_kering', 'hilang_penciuman', 'hilang_perasa'],
        'gejala_pendukung': ['sesak_napas', 'kelelahan', 'sakit_kepala'],
        'deskripsi': 'Infeksi virus SARS-CoV-2. Gejala khas mencakup demam, batuk kering, dan hilang penciuman/perasa.'
    },
    'Pneumonia': {
        'gejala_utama': ['demam_tinggi', 'sesak_napas', 'sesak_berat', 'nyeri_dada'],
        'gejala_pendukung': ['menggigil', 'batuk_berdahak', 'dahak_berdarah'],
        'deskripsi': 'Infeksi serius pada jaringan paru-paru yang menyebabkan peradangan.'
    }
}

INFO_PENYAKIT = {
    'Common Cold (Pilek Biasa)': {
        'deskripsi': 'Infeksi virus ringan. Biasanya sembuh dalam 7-10 hari.',
        'saran': '• Istirahat cukup\n• Minum vitamin C\n• Obat pereda gejala\n• Ke dokter jika tidak membaik >10 hari',
        'urgensi': '🟢 Ringan'
    },
    'Flu (Influenza)': {
        'deskripsi': 'Infeksi virus influenza. Berlangsung 5-7 hari dengan gejala lebih parah dari pilek.',
        'saran': '• Istirahat 2-3 hari\n• Banyak minum air\n• Paracetamol untuk demam\n• Dokter jika demam >3 hari',
        'urgensi': '🟡 Sedang'
    },
    'Bronkitis': {
        'deskripsi': 'Peradangan bronkus. Bisa akut (viral) atau kronis.',
        'saran': '• Istirahat, kelembapan\n• Hindari asap rokok\n• Minum air hangat+madu\n• Dokter untuk antibiotik',
        'urgensi': '🟡 Sedang'
    },
    'COVID-19': {
        'deskripsi': 'Infeksi SARS-CoV-2 dengan variasi keparahan.',
        'saran': '• TES PCR/Antigen\n• Isolasi 5 hari\n• Pantau oksigen >95%\n• Hubungi dokter jika sesak berat',
        'urgensi': '🔴 Tinggi'
    },
    'Pneumonia': {
        'deskripsi': 'Infeksi paru yang serius. Darurat medis!',
        'saran': '• KE RUMAH SAKIT/IGD\n• Foto rontgen dada\n• Antibiotik/antiviral\n• Pantau saturasi O2',
        'urgensi': '🔴 DARURAT'
    }
}

def buat_html_browser():
    """Generate HTML file for browser visualization."""
    
    gejala_json = json.dumps(GEJALA_MAP, ensure_ascii=False)
    rules_json = json.dumps(RULES_BROWSER, ensure_ascii=False)
    info_json = json.dumps(INFO_PENYAKIT, ensure_ascii=False)
    
    html = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistem Pakar Diagnosa Penyakit Saluran Pernapasan</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: Tahoma, Arial, sans-serif;
            background: #d9d9d9;
            color: #222;
        }}
        .container {{
            width: min(1200px, calc(100vw - 20px));
            height: min(800px, calc(100vh - 20px));
            margin: 10px auto;
            background: #f2f2f2;
            border: 1px solid #777;
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: 1fr auto;
        }}
        .left-panel {{
            background: #fff44d;
            border-right: 1px solid #999;
            overflow-y: auto;
            padding: 10px;
        }}
        .left-panel label {{
            display: flex;
            align-items: center;
            gap: 8px;
            margin: 5px 0;
            font-size: 13px;
            cursor: pointer;
        }}
        .left-panel input[type="checkbox"] {{
            width: 16px;
            height: 16px;
            cursor: pointer;
        }}
        .right-panel {{
            background: #efefef;
            border-left: 1px solid #999;
            overflow-y: auto;
            padding: 10px;
            font-size: 14px;
            white-space: pre-wrap;
            line-height: 1.5;
            font-family: monospace;
        }}
        .bottom-bar {{
            grid-column: 1 / -1;
            background: #ddd;
            border-top: 1px solid #999;
            padding: 8px 10px;
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 16px;
            flex-wrap: wrap;
        }}
        input[type="number"] {{
            width: 70px;
            padding: 4px;
            font-size: 14px;
        }}
        button {{
            padding: 6px 16px;
            background: #e0e0e0;
            border: 1px solid #888;
            cursor: pointer;
            font-size: 14px;
        }}
        button:hover {{
            background: #f0f0f0;
        }}
        .spacer {{ flex: 1; }}
        .diagnosis {{
            color: #b10000;
            font-weight: bold;
            font-size: 18px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="left-panel" id="gejala-list"></div>
        <div class="right-panel" id="result">Pilih gejala dan klik Proses</div>
        <div class="bottom-bar">
            <span>Threshold:</span>
            <input type="number" id="threshold" min="0" max="100" value="50">
            <span>%</span>
            <button onclick="proses()">Proses</button>
            <div class="spacer"></div>
            <span>Diagnosis: <span class="diagnosis" id="diagnosis">-</span></span>
        </div>
    </div>

    <script>
        const GEJALA = {gejala_json};
        const RULES = {rules_json};
        const INFO = {info_json};

        // Render checkbox list
        const listDiv = document.getElementById('gejala-list');
        Object.entries(GEJALA).forEach(([kode, pertanyaan]) => {{
            const label = document.createElement('label');
            label.innerHTML = `<input type="checkbox" value="${{kode}}"> ${{pertanyaan}}`;
            listDiv.appendChild(label);
        }});

        function hitungConfidence(gejalaChecked, rule) {{
            const utama = new Set(rule.gejala_utama);
            const pendukung = new Set(rule.gejala_pendukung);
            const maxScore = (utama.size * 2) + pendukung.size;
            
            let score = 0;
            gejalaChecked.forEach(g => {{
                if (utama.has(g)) score += 2;
                else if (pendukung.has(g)) score += 1;
            }});
            
            return maxScore > 0 ? Math.round((score / maxScore) * 100) : 0;
        }}

        function proses() {{
            const threshold = parseInt(document.getElementById('threshold').value) || 50;
            const gejalaChecked = Array.from(document.querySelectorAll('.left-panel input:checked')).map(el => el.value);
            
            const hasil = Object.entries(RULES).map(([nama, rule]) => {{
                const conf = hitungConfidence(gejalaChecked, rule);
                return {{ nama, conf }};
            }}).sort((a, b) => b.conf - a.conf);

            // Display results
            const resultLines = hasil.map(r => `${{r.nama.padEnd(35)}} : ${{String(r.conf).padStart(3)}}%`);
            document.getElementById('result').textContent = resultLines.join('\\n') || 'Tidak ada hasil';

            // Show top diagnosis
            const topResult = hasil.find(r => r.conf >= threshold);
            if (topResult && topResult.conf > 0) {{
                document.getElementById('diagnosis').textContent = topResult.nama;
            }} else {{
                document.getElementById('diagnosis').textContent = 'Tidak terdeteksi';
            }}
        }}

        // Allow Enter key to process
        document.getElementById('threshold').addEventListener('keypress', (e) => {{
            if (e.key === 'Enter') proses();
        }});
    </script>
</body>
</html>
"""
    
    return html


def jalankan_visualisasi():
    """Launch the browser visualization."""
    html_content = buat_html_browser()
    
    output_path = Path(__file__).parent / 'sistem_pakar_gui_browser.html'
    output_path.write_text(html_content, encoding='utf-8')
    
    webbrowser.open(output_path.as_uri())
    print(f"✅ Visualisasi browser dibuka: {output_path.name}")


if __name__ == '__main__':
    jalankan_visualisasi()
