# ============================================================
# SETUP — Import & Kompatibilitas Experta
# ============================================================

from typing import Any

# Simbol API experta yang dipakai di seluruh file.
Fact: Any
L: Any
AND: Any
OR: Any
NOT: Any
Rule: Any
KnowledgeEngine: Any

try:
    # Coba import experta asli
    from experta import AND as _AND
    from experta import Fact as _Fact
    from experta import KnowledgeEngine as _KnowledgeEngine
    from experta import L as _L
    from experta import NOT as _NOT
    from experta import OR as _OR
    from experta import Rule as _Rule

    Fact = _Fact
    L = _L
    AND = _AND
    OR = _OR
    NOT = _NOT
    Rule = _Rule
    KnowledgeEngine = _KnowledgeEngine

    EXPERTA_MODE = 'original'
    print("✅ Menggunakan pustaka experta asli")

except ImportError:
    # -------------------------------------------------------
    # IMPLEMENTASI EXPERTA-COMPATIBLE (Fallback)
    # Mengimplementasikan pola Fact / Rule / KnowledgeEngine
    # yang identik dengan API experta asli
    # -------------------------------------------------------
    print("⚠️  Pustaka experta tidak ditemukan.")
    print("   Menggunakan implementasi experta-compatible (built-in).")
    print("   Install dengan: pip install experta")
    print()

    EXPERTA_MODE = 'compatible'

    # --- Fact ---
    class _CompatFact(dict):
        """
        Representasi sebuah fakta dalam working memory.
        Mewarisi dict sehingga bisa menyimpan field-value.
        Contoh: Fact(gejala='demam')
        """
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

    # --- Kondisi Rule (L = Left-Hand Side) ---
    class _CompatL:
        """Wrapper kondisi untuk mencocokkan field Fact."""
        def __init__(self, value):
            self.value = value
        def match(self, v):
            return v == self.value

    # --- AND / OR / NOT helper ---
    class _CompatAND(list):
        """Semua kondisi harus terpenuhi."""
        pass

    class _CompatOR(list):
        """Minimal satu kondisi terpenuhi."""
        pass

    class _CompatNOT:
        """Kondisi TIDAK boleh ada."""
        def __init__(self, fact_pattern):
            self.pattern = fact_pattern

    # --- Dekorator @Rule ---
    def _compat_rule(*conditions):
        """
        Dekorator @Rule — menandai sebuah method sebagai aturan.
        Kondisi disimpan sebagai atribut _conditions pada method.
        """
        def decorator(func):
            func._is_rule    = True
            func._conditions = list(conditions)
            return func
        return decorator

    # --- KnowledgeEngine ---
    class _CompatKnowledgeEngine:
        """
        Mesin inferensi utama.
        - Menyimpan working memory (list of Facts)
        - Mengumpulkan semua @Rule dari subclass
        - Menjalankan forward chaining: cari rule yang match → eksekusi
        """

        def __init__(self):
            self.facts   = []   # Working memory
            self._fired  = set()  # Rule yang sudah dieksekusi (hindari loop)
            self._rules  = []   # Daftar method @Rule

            # Kumpulkan semua rule dari class ini dan parent-nya
            for name in dir(self.__class__):
                method = getattr(self.__class__, name, None)
                if callable(method) and getattr(method, '_is_rule', False):
                    self._rules.append(name)

        def reset(self):
            """Bersihkan working memory dan status eksekusi."""
            self.facts  = []
            self._fired = set()

        def declare(self, fact: _CompatFact):
            """
            Tambahkan fakta baru ke working memory.
            Tidak boleh ada duplikat.
            """
            if fact not in self.facts:
                self.facts.append(fact)

        def _fact_matches(self, pattern: _CompatFact) -> bool:
            """
            Cek apakah ada fakta di working memory yang cocok dengan pattern.
            Setiap field dalam pattern harus ada dan nilainya cocok.
            """
            for fact in self.facts:
                if all(
                    k in fact and (
                        v.match(fact[k]) if isinstance(v, _CompatL) else fact[k] == v
                    )
                    for k, v in pattern.items()
                ):
                    return True
            return False

        def _conditions_met(self, conditions: list) -> bool:
            """
            Evaluasi list kondisi sebuah rule.
            Mendukung: Fact (pattern), AND, OR, NOT.
            """
            for cond in conditions:
                if isinstance(cond, NOT):
                    if self._fact_matches(cond.pattern):
                        return False
                elif isinstance(cond, _CompatAND):
                    if not all(self._fact_matches(c) for c in cond):
                        return False
                elif isinstance(cond, _CompatOR):
                    if not any(self._fact_matches(c) for c in cond):
                        return False
                elif isinstance(cond, _CompatFact):
                    if not self._fact_matches(cond):
                        return False
            return True

        def run(self, max_iterations: int = 100):
            """
            Jalankan inference cycle (forward chaining).
            Loop hingga tidak ada rule baru yang bisa dieksekusi.
            """
            iteration = 0
            while iteration < max_iterations:
                fired_any = False
                for rule_name in self._rules:
                    method = getattr(self.__class__, rule_name)
                    conditions = method._conditions
                    # Buat key unik berdasarkan nama rule + snapshot fakta
                    key = (rule_name, tuple(sorted(str(f) for f in self.facts)))
                    if key not in self._fired and self._conditions_met(conditions):
                        self._fired.add(key)
                        getattr(self, rule_name)()  # Eksekusi rule
                        fired_any = True
                if not fired_any:
                    break
                iteration += 1

    Fact = _CompatFact
    L = _CompatL
    AND = _CompatAND
    OR = _CompatOR
    NOT = _CompatNOT
    Rule = _compat_rule
    KnowledgeEngine = _CompatKnowledgeEngine

    print("✅ Implementasi experta-compatible berhasil dimuat.")

print(f"\n   Mode: {EXPERTA_MODE}")
print("   Komponen tersedia: Fact, Rule, KnowledgeEngine, AND, OR, NOT, L")
# ============================================================
# KNOWLEDGE BASE — Rules Sistem Pakar Pernapasan
# ============================================================

# Kamus Gejala: kode → (pertanyaan, deskripsi singkat)
GEJALA_MAP = {
    # Gejala Umum
    'demam'             : 'Apakah Anda mengalami demam (suhu > 37.5°C)?',
    'demam_tinggi'      : 'Apakah demam Anda sangat tinggi (suhu > 39°C)?',
    'menggigil'         : 'Apakah Anda merasa menggigil?',
    # Gejala Pernapasan
    'batuk'             : 'Apakah Anda mengalami batuk?',
    'batuk_berdahak'    : 'Apakah batuk Anda berdahak (berwarna kuning/hijau)?',
    'batuk_kering'      : 'Apakah batuk Anda kering (tanpa dahak)?',
    'batuk_persisten'   : 'Apakah batuk Anda sudah berlangsung lebih dari 2 minggu?',
    'sesak_napas'       : 'Apakah Anda merasa sesak napas atau kesulitan bernapas?',
    'sesak_berat'       : 'Apakah sesak napas terasa sangat berat (sulit berbicara)?',
    'pilek'             : 'Apakah Anda mengalami pilek atau hidung meler?',
    'hidung_tersumbat'  : 'Apakah hidung Anda tersumbat?',
    'bersin'            : 'Apakah Anda sering bersin-bersin?',
    # Gejala Sistemik
    'nyeri_otot'        : 'Apakah Anda mengalami nyeri atau pegal pada otot/sendi?',
    'sakit_kepala'      : 'Apakah Anda mengalami sakit kepala?',
    'kelelahan'         : 'Apakah Anda merasa sangat lelah atau lemas?',
    'sakit_tenggorokan' : 'Apakah Anda mengalami sakit atau nyeri tenggorokan?',
    # Gejala Khas
    'hilang_penciuman'  : 'Apakah Anda kehilangan kemampuan mencium bau (anosmia)?',
    'hilang_perasa'     : 'Apakah Anda kehilangan kemampuan merasakan makanan (ageusia)?',
    'nyeri_dada'        : 'Apakah Anda merasakan nyeri atau rasa berat di dada?',
    'dahak_berdarah'    : 'Apakah dahak Anda disertai darah?',
}

# Informasi lengkap tiap penyakit (untuk output)
INFO_PENYAKIT = {
    'Flu (Influenza)': {
        'deskripsi' : 'Infeksi virus influenza yang menyerang saluran pernapasan atas. '
                      'Biasanya berlangsung 5–7 hari.',
        'saran'     : '• Istirahat cukup minimal 2–3 hari\n'
                      '• Minum air putih yang banyak\n'
                      '• Konsumsi obat penurun demam (paracetamol) jika diperlukan\n'
                      '• Konsultasi dokter jika demam > 3 hari atau gejala memburuk',
        'urgensi'   : '🟡 Sedang — Pantau kondisi'
    },
    'Bronkitis': {
        'deskripsi' : 'Peradangan pada saluran bronkus yang menyebabkan batuk berdahak '
                      'persisten. Bisa akut (viral) atau kronis (umumnya akibat merokok).',
        'saran'     : '• Istirahat dan jaga kelembapan udara\n'
                      '• Hindari asap rokok dan polusi udara\n'
                      '• Minum air hangat dan madu\n'
                      '• Periksakan ke dokter untuk kemungkinan antibiotik (bronkitis bakteri)',
        'urgensi'   : '🟡 Sedang — Disarankan ke dokter'
    },
    'COVID-19': {
        'deskripsi' : 'Infeksi virus SARS-CoV-2. Gejala khas mencakup demam, batuk kering, '
                      'dan hilang penciuman/perasa. Tingkat keparahan bervariasi.',
        'saran'     : '• SEGERA lakukan tes PCR / Antigen\n'
                      '• Isolasi mandiri minimal 5 hari\n'
                      '• Pantau saturasi oksigen (normal: > 95%)\n'
                      '• Hubungi dokter atau hotline COVID jika sesak napas memburuk',
        'urgensi'   : '🔴 Tinggi — Segera isolasi & tes'
    },
    'Pneumonia': {
        'deskripsi' : 'Infeksi serius pada jaringan paru-paru yang menyebabkan peradangan. '
                      'Dapat disebabkan bakteri, virus, atau jamur.',
        'saran'     : '• SEGERA ke rumah sakit / IGD\n'
                      '• Pemeriksaan foto rontgen dada diperlukan\n'
                      '• Kemungkinan perlu antibiotik/antiviral\n'
                      '• Pantau saturasi oksigen dan suhu tubuh',
        'urgensi'   : '🔴 Darurat — Segera ke dokter/RS'
    },
    'Common Cold (Pilek Biasa)': {
        'deskripsi' : 'Infeksi virus ringan pada saluran pernapasan atas. '
                      'Biasanya sembuh sendiri dalam 7–10 hari.',
        'saran'     : '• Istirahat cukup\n'
                      '• Minum vitamin C dan banyak cairan\n'
                      '• Gunakan obat pereda gejala (dekongestan, antihistamin)\n'
                      '• Ke dokter jika gejala tidak membaik dalam 10 hari',
        'urgensi'   : '🟢 Ringan — Istirahat di rumah'
    },
}

print("✅ Knowledge base berhasil dimuat.")
print(f"   - Jumlah gejala  : {len(GEJALA_MAP)}")
print(f"   - Jumlah penyakit: {len(INFO_PENYAKIT)}")
# ============================================================
# KNOWLEDGE ENGINE — Aturan IF-THEN dengan @Rule (Experta)
# ============================================================

class SistemPakarPernapasan(KnowledgeEngine):
    """
    Sistem pakar diagnosis penyakit saluran pernapasan.
    
    Menggunakan Forward Chaining dengan pustaka experta.
    Setiap @Rule merepresentasikan aturan IF gejala... THEN diagnosis...
    
    Penyakit yang didiagnosis:
    1. Flu (Influenza)
    2. Bronkitis
    3. COVID-19
    4. Pneumonia
    5. Common Cold (Pilek Biasa)
    """

    def __init__(self):
        super().__init__()
        self.hasil_diagnosis = []  # Menyimpan semua diagnosis yang ditemukan

    # ----------------------------------------------------------
    # RULE INTERMEDIAT: Inferensi fakta-fakta turunan
    # Rule ini menghasilkan fakta baru dari kombinasi gejala dasar
    # ----------------------------------------------------------

    @Rule(
        Fact(gejala='batuk_berdahak'),
        Fact(gejala='batuk')
    )
    def ada_gejala_batuk_produktif(self):
        """IF batuk berdahak → ada batuk produktif (fakta turunan)"""
        self.declare(Fact(kondisi='batuk_produktif'))

    @Rule(
        Fact(gejala='hilang_penciuman'),
        Fact(gejala='hilang_perasa')
    )
    def ada_gangguan_indera(self):
        """IF hilang penciuman AND hilang perasa → ada gangguan indera (khas COVID)"""
        self.declare(Fact(kondisi='gangguan_indera'))

    @Rule(
        Fact(gejala='sesak_napas'),
        Fact(gejala='sesak_berat')
    )
    def ada_sesak_berat(self):
        """IF sesak napas AND berat → kondisi kritis"""
        self.declare(Fact(kondisi='darurat_pernapasan'))

    # ----------------------------------------------------------
    # RULE DIAGNOSIS: Setiap penyakit
    # ----------------------------------------------------------

    # ---------- Rule 1: Common Cold ----------
    @Rule(
        Fact(gejala='pilek'),
        Fact(gejala='bersin'),
        Fact(gejala='hidung_tersumbat'),
        NOT(Fact(gejala='demam')),
        NOT(Fact(gejala='sesak_napas'))
    )
    def diagnosis_common_cold(self):
        """
        Rule: IF pilek AND bersin AND hidung tersumbat
              AND NOT demam AND NOT sesak napas
        THEN Common Cold
        """
        self.declare(Fact(diagnosis='Common Cold (Pilek Biasa)', confidence=85))
        self.hasil_diagnosis.append(('Common Cold (Pilek Biasa)', 85))

    @Rule(
        Fact(gejala='pilek'),
        Fact(gejala='sakit_tenggorokan'),
        NOT(Fact(gejala='demam')),
        NOT(Fact(gejala='batuk_kering'))
    )
    def diagnosis_common_cold_v2(self):
        """
        Rule alternatif Common Cold: IF pilek AND sakit tenggorokan
              AND NOT demam AND NOT batuk kering
        """
        if ('Common Cold (Pilek Biasa)', 85) not in self.hasil_diagnosis:
            self.declare(Fact(diagnosis='Common Cold (Pilek Biasa)', confidence=70))
            self.hasil_diagnosis.append(('Common Cold (Pilek Biasa)', 70))

    # ---------- Rule 2: Flu (Influenza) ----------
    @Rule(
        Fact(gejala='demam'),
        Fact(gejala='batuk'),
        Fact(gejala='nyeri_otot'),
        Fact(gejala='sakit_kepala'),
        Fact(gejala='kelelahan')
    )
    def diagnosis_flu_penuh(self):
        """
        Rule Flu Lengkap: IF demam AND batuk AND nyeri otot
                         AND sakit kepala AND kelelahan
        THEN Flu dengan confidence tinggi
        """
        self.declare(Fact(diagnosis='Flu (Influenza)', confidence=90))
        self.hasil_diagnosis.append(('Flu (Influenza)', 90))

    @Rule(
        Fact(gejala='demam'),
        Fact(gejala='batuk'),
        Fact(gejala='nyeri_otot'),
        NOT(Fact(gejala='sesak_napas')),
        NOT(Fact(kondisi='gangguan_indera'))
    )
    def diagnosis_flu_sedang(self):
        """
        Rule Flu Dasar: IF demam AND batuk AND nyeri otot
                       AND NOT sesak napas AND NOT gangguan indera
        """
        if ('Flu (Influenza)', 90) not in self.hasil_diagnosis:
            self.declare(Fact(diagnosis='Flu (Influenza)', confidence=75))
            self.hasil_diagnosis.append(('Flu (Influenza)', 75))

    @Rule(
        Fact(gejala='demam'),
        Fact(gejala='pilek'),
        Fact(gejala='sakit_kepala'),
        Fact(gejala='kelelahan'),
        NOT(Fact(kondisi='gangguan_indera'))
    )
    def diagnosis_flu_v3(self):
        """Rule Flu tambahan: demam + pilek + sakit kepala + kelelahan"""
        if not any(d[0] == 'Flu (Influenza)' for d in self.hasil_diagnosis):
            self.declare(Fact(diagnosis='Flu (Influenza)', confidence=70))
            self.hasil_diagnosis.append(('Flu (Influenza)', 70))

    # ---------- Rule 3: Bronkitis ----------
    @Rule(
        Fact(kondisi='batuk_produktif'),
        Fact(gejala='batuk_persisten'),
        Fact(gejala='sesak_napas')
    )
    def diagnosis_bronkitis_penuh(self):
        """
        Rule Bronkitis Lengkap:
        IF batuk produktif AND batuk > 2 minggu AND sesak napas
        THEN Bronkitis confidence tinggi
        """
        self.declare(Fact(diagnosis='Bronkitis', confidence=88))
        self.hasil_diagnosis.append(('Bronkitis', 88))

    @Rule(
        Fact(gejala='batuk_berdahak'),
        Fact(gejala='batuk_persisten'),
        Fact(gejala='nyeri_dada')
    )
    def diagnosis_bronkitis_sedang(self):
        """
        Rule Bronkitis Sedang:
        IF batuk berdahak AND batuk persisten AND nyeri dada
        """
        if not any(d[0] == 'Bronkitis' for d in self.hasil_diagnosis):
            self.declare(Fact(diagnosis='Bronkitis', confidence=78))
            self.hasil_diagnosis.append(('Bronkitis', 78))

    @Rule(
        Fact(kondisi='batuk_produktif'),
        Fact(gejala='batuk_persisten'),
        NOT(Fact(gejala='demam_tinggi'))
    )
    def diagnosis_bronkitis_ringan(self):
        """
        Rule Bronkitis Ringan:
        IF batuk produktif AND persisten AND NOT demam tinggi
        """
        if not any(d[0] == 'Bronkitis' for d in self.hasil_diagnosis):
            self.declare(Fact(diagnosis='Bronkitis', confidence=65))
            self.hasil_diagnosis.append(('Bronkitis', 65))

    # ---------- Rule 4: COVID-19 ----------
    @Rule(
        Fact(gejala='demam'),
        Fact(gejala='batuk_kering'),
        Fact(kondisi='gangguan_indera')
    )
    def diagnosis_covid_khas(self):
        """
        Rule COVID-19 Khas (Gejala Patognomonik):
        IF demam AND batuk kering AND (hilang penciuman + perasa)
        THEN COVID-19 confidence sangat tinggi
        """
        self.declare(Fact(diagnosis='COVID-19', confidence=95))
        self.hasil_diagnosis.append(('COVID-19', 95))

    @Rule(
        Fact(gejala='demam'),
        Fact(gejala='batuk_kering'),
        Fact(gejala='sesak_napas'),
        NOT(Fact(kondisi='gangguan_indera'))
    )
    def diagnosis_covid_sedang(self):
        """
        Rule COVID-19 Sedang:
        IF demam AND batuk kering AND sesak napas
        """
        if not any(d[0] == 'COVID-19' for d in self.hasil_diagnosis):
            self.declare(Fact(diagnosis='COVID-19', confidence=80))
            self.hasil_diagnosis.append(('COVID-19', 80))

    @Rule(
        Fact(gejala='demam'),
        Fact(kondisi='gangguan_indera'),
        Fact(gejala='kelelahan')
    )
    def diagnosis_covid_ringan(self):
        """
        Rule COVID-19 Ringan:
        IF demam AND gangguan indera AND kelelahan
        """
        if not any(d[0] == 'COVID-19' for d in self.hasil_diagnosis):
            self.declare(Fact(diagnosis='COVID-19', confidence=75))
            self.hasil_diagnosis.append(('COVID-19', 75))

    # ---------- Rule 5: Pneumonia ----------
    @Rule(
        Fact(gejala='demam_tinggi'),
        Fact(kondisi='darurat_pernapasan'),
        Fact(gejala='nyeri_dada'),
        Fact(gejala='menggigil')
    )
    def diagnosis_pneumonia_berat(self):
        """
        Rule Pneumonia Berat:
        IF demam tinggi AND sesak berat AND nyeri dada AND menggigil
        THEN Pneumonia — DARURAT
        """
        self.declare(Fact(diagnosis='Pneumonia', confidence=92))
        self.hasil_diagnosis.append(('Pneumonia', 92))

    @Rule(
        Fact(gejala='demam_tinggi'),
        Fact(gejala='sesak_napas'),
        Fact(gejala='batuk_berdahak'),
        Fact(gejala='nyeri_dada')
    )
    def diagnosis_pneumonia_sedang(self):
        """
        Rule Pneumonia Sedang:
        IF demam tinggi AND sesak napas AND batuk berdahak AND nyeri dada
        """
        if not any(d[0] == 'Pneumonia' for d in self.hasil_diagnosis):
            self.declare(Fact(diagnosis='Pneumonia', confidence=82))
            self.hasil_diagnosis.append(('Pneumonia', 82))

    @Rule(
        Fact(gejala='demam_tinggi'),
        Fact(gejala='sesak_napas'),
        Fact(gejala='dahak_berdarah')
    )
    def diagnosis_pneumonia_khas(self):
        """
        Rule Pneumonia Khas:
        IF demam tinggi AND sesak napas AND dahak berdarah
        """
        if not any(d[0] == 'Pneumonia' for d in self.hasil_diagnosis):
            self.declare(Fact(diagnosis='Pneumonia', confidence=88))
            self.hasil_diagnosis.append(('Pneumonia', 88))


print("✅ KnowledgeEngine 'SistemPakarPernapasan' berhasil didefinisikan.")
print()
print("📋 Ringkasan Rules:")
import inspect
rules = [(name, getattr(SistemPakarPernapasan, name).__doc__.strip().split('\n')[0]
          if getattr(SistemPakarPernapasan, name).__doc__ else '-')
         for name in dir(SistemPakarPernapasan)
         if callable(getattr(SistemPakarPernapasan, name))
         and getattr(getattr(SistemPakarPernapasan, name), '_is_rule', False)]
for i, (name, doc) in enumerate(rules, 1):
    print(f"  Rule {i:02d}: {name:<35} → {doc}")
    # ============================================================
# USER INTERFACE — Antarmuka Konsultasi Interaktif
# ============================================================

import textwrap

def tampilkan_header():
    print("=" * 65)
    print("  🫁 SISTEM PAKAR DIAGNOSA PENYAKIT SALURAN PERNAPASAN")
    print("     Berbasis Experta | Forward Chaining")
    print("=" * 65)
    print()
    print("  Sistem ini membantu mendeteksi kemungkinan penyakit:")
    print("  • Flu (Influenza)         • COVID-19")
    print("  • Bronkitis               • Pneumonia")
    print("  • Common Cold (Pilek)")
    print()
    print("  Jawab setiap pertanyaan dengan y (ya) atau n (tidak).")
    print()


def kumpulkan_gejala_interaktif() -> list:
    """
    Mengumpulkan gejala dari pengguna melalui pertanyaan interaktif.
    Returns: list of Fact objects yang akan di-declare ke engine
    """
    # Urutan pertanyaan dikelompokkan secara logis
    urutan_tanya = [
        # Kelompok 1: Gejala dasar
        ('demam',            'KELOMPOK GEJALA UTAMA'),
        ('demam_tinggi',     None),
        ('menggigil',        None),
        ('kelelahan',        None),
        # Kelompok 2: Batuk
        ('batuk',            'KELOMPOK BATUK'),
        ('batuk_kering',     None),
        ('batuk_berdahak',   None),
        ('batuk_persisten',  None),
        ('dahak_berdarah',   None),
        # Kelompok 3: Pernapasan
        ('sesak_napas',      'KELOMPOK PERNAPASAN & DADA'),
        ('sesak_berat',      None),
        ('nyeri_dada',       None),
        # Kelompok 4: Hidung & Tenggorokan
        ('pilek',            'KELOMPOK HIDUNG & TENGGOROKAN'),
        ('hidung_tersumbat', None),
        ('bersin',           None),
        ('sakit_tenggorokan',None),
        # Kelompok 5: Sistemik
        ('nyeri_otot',       'KELOMPOK GEJALA SISTEMIK'),
        ('sakit_kepala',     None),
        # Kelompok 6: Gejala khas
        ('hilang_penciuman', 'KELOMPOK GEJALA KHAS'),
        ('hilang_perasa',    None),
    ]

    gejala_terpilih = []
    total = len(urutan_tanya)

    for i, (kode, header) in enumerate(urutan_tanya, start=1):
        if header:
            print(f"\n  ── {header} ──")

        pertanyaan = GEJALA_MAP[kode]
        while True:
            jawaban = input(f"  [{i:02d}/{total}] {pertanyaan} (y/n): ").strip().lower()
            if jawaban in ('y', 'n', 'ya', 'tidak', 'yes', 'no'):
                break
            print("          ⚠️  Masukkan 'y' atau 'n'")

        if jawaban in ('y', 'ya', 'yes'):
            gejala_terpilih.append(kode)

    return gejala_terpilih


def tampilkan_hasil(engine: SistemPakarPernapasan, gejala_user: list):
    """Menampilkan hasil diagnosis dari engine."""
    # Ambil hasil, ambil yang terbaik per penyakit
    diagnosis_dict = {}
    for nama, conf in engine.hasil_diagnosis:
        if nama not in diagnosis_dict or conf > diagnosis_dict[nama]:
            diagnosis_dict[nama] = conf

    # Urutkan berdasarkan confidence
    diagnosis_sorted = sorted(diagnosis_dict.items(), key=lambda x: x[1], reverse=True)

    print()
    print("=" * 65)
    print("  📊 HASIL DIAGNOSIS")
    print("=" * 65)

    # Ringkasan gejala
    print(f"\n  Gejala yang Anda laporkan ({len(gejala_user)} gejala):")
    for g in gejala_user:
        print(f"    ✓ {GEJALA_MAP[g][:60]}")

    print()
    if not diagnosis_sorted:
        print("  ℹ️  Tidak ada diagnosis spesifik yang ditemukan.")
        print("     Gejala Anda tidak cukup spesifik atau kombinasi gejala")
        print("     tidak cocok dengan penyakit dalam knowledge base.")
        print("     Disarankan berkonsultasi langsung dengan dokter.")
    else:
        # Bar chart confidence
        print("  📈 Confidence Score Diagnosis:")
        print("  " + "-" * 55)
        for nama, conf in diagnosis_sorted:
            bar = '█' * int(conf / 5) + '░' * (20 - int(conf / 5))
            print(f"  {nama:<30} {bar} {conf}%")

        # Diagnosis utama
        nama_utama, conf_utama = diagnosis_sorted[0]
        info = INFO_PENYAKIT.get(nama_utama, {})

        print()
        print(f"  {'─'*55}")
        print(f"  🏆 DIAGNOSIS UTAMA: {nama_utama}")
        print(f"     Confidence: {conf_utama}%")
        print(f"     Urgensi   : {info.get('urgensi', '-')}")
        print()

        print("  📖 Deskripsi:")
        for line in textwrap.wrap(info.get('deskripsi', '-'), 56):
            print(f"     {line}")

        print()
        print("  💡 Saran Tindak Lanjut:")
        for line in info.get('saran', '-').split('\n'):
            print(f"     {line}")

        if len(diagnosis_sorted) > 1:
            print()
            print("  ⚠️  Kemungkinan lain:")
            for nama, conf in diagnosis_sorted[1:]:
                print(f"     • {nama} ({conf}%)")

    print()
    print("=" * 65)
    print("  ⚕️  PENTING: Hasil ini hanya perkiraan awal.")
    print("      Konsultasikan dengan dokter untuk diagnosis resmi.")
    print("=" * 65)


print("✅ User interface berhasil dimuat.")

# ============================================================
# SIMPLIFIED RULES FOR BROWSER — Definisi Gejala per Penyakit
# ============================================================
# Untuk visualisasi browser (tanpa Experta engine complexity)
# Setiap penyakit memiliki gejala_utama (bobot 2) dan gejala_pendukung (bobot 1)

RULES_BROWSER = {
    'Common Cold (Pilek Biasa)': {
        'deskripsi': 'Infeksi virus ringan pada saluran pernapasan atas.',
        'gejala_utama': ['pilek', 'bersin', 'hidung_tersumbat'],
        'gejala_pendukung': ['sakit_tenggorokan', 'demam']
    },
    'Flu (Influenza)': {
        'deskripsi': 'Infeksi virus influenza yang menyerang saluran pernapasan atas.',
        'gejala_utama': ['demam', 'batuk', 'nyeri_otot', 'sakit_kepala'],
        'gejala_pendukung': ['kelelahan', 'pilek', 'sakit_tenggorokan']
    },
    'Bronkitis': {
        'deskripsi': 'Peradangan pada saluran bronkus yang menyebabkan batuk berdahak.',
        'gejala_utama': ['batuk_berdahak', 'batuk_persisten', 'sesak_napas'],
        'gejala_pendukung': ['batuk', 'nyeri_dada', 'demam']
    },
    'COVID-19': {
        'deskripsi': 'Infeksi virus SARS-CoV-2 dengan gejala khas:  demam, batuk, gangguan indera.',
        'gejala_utama': ['demam', 'batuk_kering', 'hilang_penciuman', 'hilang_perasa'],
        'gejala_pendukung': ['sesak_napas', 'kelelahan', 'sakit_kepala']
    },
    'Pneumonia': {
        'descrepsi': 'Infeksi serius pada jaringan paru-paru yang menyebabkan peradangan.',
        'gejala_utama': ['demam_tinggi', 'sesak_napas', 'sesak_berat', 'nyeri_dada'],
        'gejala_pendukung': ['menggigil', 'batuk_berdahak', 'dahak_berdarah']
    }
}

# ============================================================
# MAIN PROGRAM — Jalankan Sistem Pakar Pernapasan
# ============================================================

def jalankan_sistem_pakar():
    """
    Fungsi utama sistem pakar pernapasan.
    
    Alur:
    1. Tampilkan header
    2. Kumpulkan gejala dari user (kumpulkan_gejala_interaktif)
    3. Inisialisasi KnowledgeEngine
    4. Declare semua fakta gejala ke engine
    5. Jalankan engine.run() → forward chaining
    6. Tampilkan hasil diagnosis
    """
    tampilkan_header()

    # FASE 1: Kumpulkan gejala
    gejala_user = kumpulkan_gejala_interaktif()

    print("\n  🔄 Memproses dengan inference engine (forward chaining)...")

    # FASE 2: Inisialisasi engine
    engine = SistemPakarPernapasan()
    engine.reset()

    # FASE 3: Declare fakta gejala ke working memory
    for kode in gejala_user:
        engine.declare(Fact(gejala=kode))

    # FASE 4: Jalankan inference (forward chaining)
    # Engine akan mencocokkan fakta dengan rules secara berulang
    # hingga tidak ada rule baru yang bisa dieksekusi
    engine.run()

    # FASE 5: Tampilkan hasil
    tampilkan_hasil(engine, gejala_user)


# ▶️ Entry Point untuk CLI (opsional)
# Uncomment line berikut untuk menjalankan mode CLI interaktif:
# jalankan_sistem_pakar()


# ============================================================
# UNIT TESTING — Skenario Otomatis
# ============================================================

def jalankan_unit_testing():
    """Menjalankan semua test scenario."""
# ============================================================
# UNIT TESTING — Skenario Otomatis
# ============================================================

def uji_skenario(nama_skenario: str, gejala_input: list, ekspektasi: str):
    """
    Menguji sistem dengan skenario gejala tertentu.
    
    Args:
        nama_skenario : Nama skenario uji
        gejala_input  : List kode gejala yang diinput
        ekspektasi    : Nama penyakit yang diharapkan menjadi diagnosis utama
    """
    # Inisialisasi dan jalankan engine
    engine = SistemPakarPernapasan()
    engine.reset()
    for kode in gejala_input:
        engine.declare(Fact(gejala=kode))
    engine.run()

    # Ambil hasil terbaik per penyakit
    diagnosis_dict = {}
    for nama, conf in engine.hasil_diagnosis:
        if nama not in diagnosis_dict or conf > diagnosis_dict[nama]:
            diagnosis_dict[nama] = conf
    hasil_sorted = sorted(diagnosis_dict.items(), key=lambda x: x[1], reverse=True)

    # Evaluasi
    top_diagnosis = hasil_sorted[0][0] if hasil_sorted else 'Tidak ada'
    top_conf      = hasil_sorted[0][1] if hasil_sorted else 0
    status        = '✅ LULUS' if top_diagnosis == ekspektasi else '❌ GAGAL'

    print(f"\n  📌 {nama_skenario}")
    print(f"     Gejala    : {', '.join(gejala_input)}")
    print(f"     Ekspektasi: {ekspektasi}")
    print(f"     Hasil     : {top_diagnosis} ({top_conf}%) → {status}")
    if len(hasil_sorted) > 1:
        print(f"     Lainnya   : {', '.join(f'{n}({c}%)' for n,c in hasil_sorted[1:])}")


print("=" * 65)
print("  🧪 HASIL UNIT TESTING SISTEM PAKAR")
print("=" * 65)

# Skenario 1: Common Cold
uji_skenario(
    'Skenario 1 — Common Cold',
    ['pilek', 'bersin', 'hidung_tersumbat', 'sakit_tenggorokan'],
    'Common Cold (Pilek Biasa)'
)

# Skenario 2: Flu
uji_skenario(
    'Skenario 2 — Flu (Influenza)',
    ['demam', 'batuk', 'nyeri_otot', 'sakit_kepala', 'kelelahan', 'pilek'],
    'Flu (Influenza)'
)

# Skenario 3: Bronkitis
uji_skenario(
    'Skenario 3 — Bronkitis',
    ['batuk', 'batuk_berdahak', 'batuk_persisten', 'sesak_napas', 'nyeri_dada'],
    'Bronkitis'
)

# Skenario 4: COVID-19 (dengan anosmia)
uji_skenario(
    'Skenario 4 — COVID-19 (Anosmia)',
    ['demam', 'batuk_kering', 'hilang_penciuman', 'hilang_perasa', 'kelelahan'],
    'COVID-19'
)

# Skenario 5: Pneumonia
uji_skenario(
    'Skenario 5 — Pneumonia',
    ['demam_tinggi', 'sesak_napas', 'sesak_berat', 'nyeri_dada', 'menggigil', 'batuk_berdahak'],
    'Pneumonia'
)

# Skenario 6: Gejala Campuran (COVID + Flu)
uji_skenario(
    'Skenario 6 — Campuran (COVID + Flu)',
    ['demam', 'batuk_kering', 'hilang_penciuman', 'hilang_perasa', 'nyeri_otot', 'sakit_kepala'],
    'COVID-19'
)

print()
print("=" * 65)
print("  Unit testing selesai.")
print("=" * 65)


# ============================================================
# BROWSER VISUALIZATION — Visualisasi GUI di Browser
# ============================================================

def jalankan_visualisasi_browser() -> None:
    """
    Menjalankan sistem pakar dalam visualisasi browser interaktif.
    User dapat memilih gejala dengan checkbox, mengatur threshold, 
    dan melihat diagnosis secara real-time.
    """
    import json
    import webbrowser
    from pathlib import Path
    
    # Persiapkan data untuk JavaScript
    gejala_js = json.dumps(GEJALA_MAP, ensure_ascii=False, indent=2)
    rules_js = json.dumps(RULES_BROWSER, ensure_ascii=False, indent=2)
    info_js = json.dumps(INFO_PENYAKIT, ensure_ascii=False, indent=2)

    # Template HTML dengan CSS dan JavaScript embedded
    html_content = f"""<!doctype html>
<html lang="id">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Sistem Pakar Diagnosa Penyakit Saluran Pernapasan</title>
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
            font-size: 18px;
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
            font-size: 22px;
        }}
        .row {{
            display: flex;
            align-items: center;
            gap: 6px;
            margin: 3px 0;
            font-size: 13px;
        }}
        input[type="checkbox"] {{
            width: 18px;
            height: 18px;
            accent-color: #d9d9d9;
        }}
        input[type="number"] {{
            width: 70px;
            height: 34px;
            font-size: 22px;
            padding: 2px 4px;
        }}
        button {{
            font-size: 22px;
            padding: 4px 14px;
            cursor: pointer;
            background: #e0e0e0;
            border: 1px solid #888;
                print("=" * 65)
                print("  HASIL UNIT TESTING SISTEM PAKAR")
                print("=" * 65)

                # Skenario 1: Common Cold
                uji_skenario(
                    'Skenario 1 — Common Cold',
                    ['pilek', 'bersin', 'hidung_tersumbat', 'sakit_tenggorokan'],
                    'Common Cold (Pilek Biasa)'
                )

                # Skenario 2: Flu
                uji_skenario(
                    'Skenario 2 — Flu (Influenza)',
                    ['demam', 'batuk', 'nyeri_otot', 'sakit_kepala', 'kelelahan', 'pilek'],
                    'Flu (Influenza)'
                )

                # Skenario 3: Bronkitis
                uji_skenario(
                    'Skenario 3 — Bronkitis',
                    ['batuk', 'batuk_berdahak', 'batuk_persisten', 'sesak_napas', 'nyeri_dada'],
                    'Bronkitis'
                )

                # Skenario 4: COVID-19 (dengan anosmia)
                uji_skenario(
                    'Skenario 4 — COVID-19 (Anosmia)',
                    ['demam', 'batuk_kering', 'hilang_penciuman', 'hilang_perasa', 'kelelahan'],
                    'COVID-19'
                )

                # Skenario 5: Pneumonia
                uji_skenario(
                    'Skenario 5 — Pneumonia',
                    ['demam_tinggi', 'sesak_napas', 'sesak_berat', 'nyeri_dada', 'menggigil', 'batuk_berdahak'],
                    'Pneumonia'
                )

                # Skenario 6: Gejala Campuran (COVID + Flu)
                uji_skenario(
                    'Skenario 6 — Campuran (COVID + Flu)',
                    ['demam', 'batuk_kering', 'hilang_penciuman', 'hilang_perasa', 'nyeri_otot', 'sakit_kepala'],
                    'COVID-19'
                )

                print()
                print("=" * 65)
                print("  Unit testing selesai.")
                print("=" * 65)
            Object.entries(GEJALA).forEach(([kode, pertanyaan]) => {{
                const row = document.createElement('label');
                row.className = 'row';
                row.innerHTML = `<input type="checkbox" data-kode="${{kode}}"> <span>${{pertanyaan}}</span>`;
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

            const hasil = Object.entries(RULES).map(([nama, rule]) => {{
                const confidence = hitungConfidence(fakta, rule);
                return {{ nama, confidence }};
            }}).sort((a, b) => b.confidence - a.confidence);

            const lines = hasil.map((h) => `${{h.nama:<40}} : ${{h.confidence.toFixed(0)}} %`);
            const displayLines = lines.slice(0, 5).join('\\n');
            resultEl.textContent = displayLines || 'Tidak ada hasil.';

            const top = hasil.find((h) => h.confidence >= threshold);
            if (top && top.confidence > 0) {{
                const info = INFO[top.nama] || {{}};
                topEl.textContent = top.nama;
            }} else {{
                topEl.textContent = 'Tidak terdeteksi';
            }}
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


# VISUALISASI — Diagram Rules dan Confidence


import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
import numpy as np

fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# ------- Plot 1: Heatmap Gejala vs Penyakit -------
ax1 = axes[0]

# Definisi gejala per penyakit (dari rules utama)
penyakit_plot = [
    'Common\nCold', 'Flu\n(Influenza)', 'Bronkitis', 'COVID-19', 'Pneumonia'
]
gejala_plot = [
    'demam', 'demam_tinggi', 'menggigil', 'batuk', 'batuk_kering',
    'batuk_berdahak', 'batuk_persisten', 'sesak_napas', 'sesak_berat',
    'nyeri_dada', 'pilek', 'hidung_tersumbat', 'bersin',
    'sakit_tenggorokan', 'nyeri_otot', 'sakit_kepala', 'kelelahan',
    'hilang_penciuman', 'hilang_perasa', 'dahak_berdarah'
]

# Matrix: 2=utama, 1=pendukung, 0=tidak
matrix = np.array([
    # Cold  Flu   Bron  COVID Pneum
    [0,    2,    1,    2,    2],   # demam
    [0,    0,    0,    0,    2],   # demam_tinggi
    [0,    1,    0,    0,    2],   # menggigil
    [0,    2,    2,    0,    1],   # batuk
    [0,    0,    0,    2,    0],   # batuk_kering
    [0,    0,    2,    0,    2],   # batuk_berdahak
    [0,    0,    2,    0,    0],   # batuk_persisten
    [0,    0,    2,    2,    2],   # sesak_napas
    [0,    0,    0,    0,    2],   # sesak_berat
    [0,    0,    2,    0,    2],   # nyeri_dada
    [2,    1,    0,    0,    0],   # pilek
    [2,    0,    0,    0,    0],   # hidung_tersumbat
    [2,    0,    0,    0,    0],   # bersin
    [1,    0,    0,    0,    0],   # sakit_tenggorokan
    [0,    2,    0,    0,    0],   # nyeri_otot
    [0,    2,    0,    0,    0],   # sakit_kepala
    [0,    2,    0,    1,    0],   # kelelahan
    [0,    0,    0,    2,    0],   # hilang_penciuman
    [0,    0,    0,    2,    0],   # hilang_perasa
    [0,    0,    0,    0,    1],   # dahak_berdarah
])

cmap = ListedColormap(['#eeeeee', '#90caf9', '#1565c0'])
im = ax1.imshow(matrix, cmap=cmap, vmin=0, vmax=2, aspect='auto')

ax1.set_xticks(range(len(penyakit_plot)))
ax1.set_xticklabels(penyakit_plot, fontsize=9, fontweight='bold')
ax1.set_yticks(range(len(gejala_plot)))
ax1.set_yticklabels(gejala_plot, fontsize=8)
ax1.set_xticks(np.arange(-0.5, len(penyakit_plot), 1), minor=True)
ax1.set_yticks(np.arange(-0.5, len(gejala_plot), 1), minor=True)
ax1.grid(which='minor', color='white', linewidth=1.2)
ax1.set_title('Peta Gejala vs Penyakit\n(Knowledge Base)', fontsize=11, fontweight='bold')

p0 = mpatches.Patch(color='#eeeeee', label='Tidak relevan')
p1 = mpatches.Patch(color='#90caf9', label='Gejala Pendukung')
p2 = mpatches.Patch(color='#1565c0', label='Gejala Utama')
ax1.legend(handles=[p0, p1, p2], loc='lower right', fontsize=8,
           bbox_to_anchor=(1.0, -0.15))

# ------- Plot 2: Bar Chart Confidence Skenario -------
ax2 = axes[1]

skenario_names = [
    'Skenario 1\n(Common Cold)', 'Skenario 2\n(Flu)',
    'Skenario 3\n(Bronkitis)', 'Skenario 4\n(COVID-19)', 'Skenario 5\n(Pneumonia)'
]
skenario_gejala = [
    ['pilek', 'bersin', 'hidung_tersumbat'],
    ['demam', 'batuk', 'nyeri_otot', 'sakit_kepala', 'kelelahan'],
    ['batuk', 'batuk_berdahak', 'batuk_persisten', 'sesak_napas', 'nyeri_dada'],
    ['demam', 'batuk_kering', 'hilang_penciuman', 'hilang_perasa'],
    ['demam_tinggi', 'sesak_napas', 'sesak_berat', 'nyeri_dada', 'menggigil'],
]
colors_bar = ['#4caf50', '#2196f3', '#ff9800', '#f44336', '#9c27b0']

conf_values = []
for gejala_input in skenario_gejala:
    engine = SistemPakarPernapasan()
    engine.reset()
    for kode in gejala_input:
        engine.declare(Fact(gejala=kode))
    engine.run()
    if engine.hasil_diagnosis:
        best = max(engine.hasil_diagnosis, key=lambda x: x[1])
        conf_values.append(best[1])


    else:
        conf_values.append(0)

bars = ax2.bar(skenario_names, conf_values, color=colors_bar, edgecolor='white', linewidth=1.5)
ax2.set_ylim(0, 110)
ax2.set_ylabel('Confidence (%)', fontsize=10)
ax2.set_title('Confidence Score per Skenario Uji', fontsize=11, fontweight='bold')
ax2.axhline(y=70, color='gray', linestyle='--', alpha=0.5, label='Threshold 70%')
ax2.legend(fontsize=8)
for bar, val in zip(bars, conf_values):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
            f'{val}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.suptitle('Visualisasi Sistem Pakar Diagnosis Penyakit Saluran Pernapasan',
            fontsize=13, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig('visualisasi_sistem_pakar_pernapasan.png', dpi=150, bbox_inches='tight')
plt.show()
print("✅ Visualisasi disimpan sebagai 'visualisasi_sistem_pakar_pernapasan.png'")


# ▶️ Entry Point — Jalankan sistem
if __name__ == '__main__':
    jalankan_visualisasi_browser()
