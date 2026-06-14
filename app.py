import streamlit as st
import google.generativeai as genai
import json
import re
import time

# =============================================
# SAYFA AYARLARI
# =============================================
st.set_page_config(
    page_title="Metin Kontrol — Türkçe Yazım Denetleyici",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================
# CUSTOM CSS
# =============================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* Global */
.stApp {
    font-family: 'Inter', sans-serif;
}

/* Header */
.main-header {
    text-align: center;
    padding: 1.5rem 0 2rem;
}
.main-header .logo {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 60px;
    height: 60px;
    border-radius: 16px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    font-size: 1.6rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 8px 32px rgba(99,102,241,0.3);
}
.main-header h1 {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #f1f5f9 0%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 0.4rem;
    letter-spacing: -0.02em;
}
.main-header p {
    color: #94a3b8;
    font-size: 0.95rem;
    max-width: 550px;
    margin: 0 auto;
}

/* Stat Cards */
.stats-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.stat-card {
    flex: 1;
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
    backdrop-filter: blur(10px);
}
.stat-card .value {
    font-size: 1.8rem;
    font-weight: 800;
    letter-spacing: -0.02em;
}
.stat-card .label {
    font-size: 0.72rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-top: 0.15rem;
}
.stat-card.total .value { color: #f1f5f9; }
.stat-card.spelling .value { color: #f43f5e; }
.stat-card.punctuation .value { color: #f59e0b; }
.stat-card.grammar .value { color: #3b82f6; }
.stat-card.ai .value { color: #8b5cf6; }

/* Error Cards */
.error-card {
    background: rgba(30, 41, 59, 0.5);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.6rem;
    transition: all 0.2s;
}
.error-card:hover {
    background: rgba(30, 41, 59, 0.8);
    border-color: rgba(99,102,241,0.3);
}

.error-badge {
    display: inline-block;
    padding: 0.15rem 0.55rem;
    border-radius: 20px;
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 0.5rem;
}
.error-badge.spelling {
    background: rgba(244,63,94,0.12);
    color: #f43f5e;
    border: 1px solid rgba(244,63,94,0.25);
}
.error-badge.punctuation {
    background: rgba(245,158,11,0.12);
    color: #f59e0b;
    border: 1px solid rgba(245,158,11,0.25);
}
.error-badge.grammar {
    background: rgba(59,130,246,0.12);
    color: #3b82f6;
    border: 1px solid rgba(59,130,246,0.25);
}
.error-badge.ai {
    background: rgba(139,92,246,0.12);
    color: #a78bfa;
    border: 1px solid rgba(139,92,246,0.25);
}

.error-message {
    font-size: 0.88rem;
    color: #e2e8f0;
    margin-bottom: 0.4rem;
    line-height: 1.5;
}

.error-context {
    font-size: 0.78rem;
    color: #64748b;
    background: rgba(0,0,0,0.2);
    padding: 0.35rem 0.6rem;
    border-radius: 6px;
    margin-bottom: 0.5rem;
    font-family: 'JetBrains Mono', monospace;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.suggestion-chip {
    display: inline-block;
    padding: 0.2rem 0.55rem;
    border-radius: 20px;
    font-size: 0.73rem;
    font-weight: 500;
    background: rgba(16,185,129,0.1);
    color: #10b981;
    border: 1px solid rgba(16,185,129,0.2);
    margin-right: 0.3rem;
    margin-bottom: 0.25rem;
}

/* Preview */
.preview-box {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 1.5rem;
    line-height: 1.9;
    font-size: 1rem;
    min-height: 200px;
    white-space: pre-wrap;
    word-wrap: break-word;
}

.highlight-spelling {
    background: rgba(244,63,94,0.15);
    border-bottom: 2px solid #f43f5e;
    padding: 1px 3px;
    border-radius: 3px;
    cursor: help;
}
.highlight-punctuation {
    background: rgba(245,158,11,0.15);
    border-bottom: 2px solid #f59e0b;
    padding: 1px 3px;
    border-radius: 3px;
    cursor: help;
}
.highlight-grammar {
    background: rgba(59,130,246,0.15);
    border-bottom: 2px solid #3b82f6;
    padding: 1px 3px;
    border-radius: 3px;
    cursor: help;
}
.highlight-ai {
    background: rgba(139,92,246,0.15);
    border-bottom: 2px solid #a78bfa;
    padding: 1px 3px;
    border-radius: 3px;
    cursor: help;
}

/* Success Box */
.success-box {
    text-align: center;
    padding: 2rem;
    background: rgba(16,185,129,0.06);
    border: 1px solid rgba(16,185,129,0.2);
    border-radius: 12px;
}
.success-box .icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
.success-box h3 { color: #10b981; margin: 0; }
.success-box p { color: #64748b; font-size: 0.85rem; margin-top: 0.25rem; }

/* Footer */
.footer {
    text-align: center;
    padding: 2rem 0 1rem;
    color: #475569;
    font-size: 0.78rem;
}

/* Hide Streamlit defaults */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# =============================================
# TÜRKÇE SÖZLÜK VE KURALLAR (Yerel Denetleyici)
# =============================================
COMMON_MISSPELLINGS = {
    "cünkü": "çünkü", "cunki": "çünkü", "cünki": "çünkü", "çünki": "çünkü",
    "bişey": "bir şey", "bişi": "bir şey", "birşey": "bir şey",
    "herşey": "her şey", "hiçbirşey": "hiçbir şey",
    "herzaman": "her zaman", "hergün": "her gün", "heryer": "her yer",
    "herhangibi": "herhangi bir",
    "yalnış": "yanlış", "yanlız": "yalnız",
    "geliycek": "gelecek", "gidicem": "gideceğim", "gelcem": "geleceğim",
    "gidicek": "gidecek", "gelicek": "gelecek",
    "yapıcam": "yapacağım", "yapıcak": "yapacak",
    "edicek": "edecek", "edicem": "edeceğim",
    "alcam": "alacağım", "alcak": "alacak",
    "vercek": "verecek", "vercem": "vereceğim",
    "dicek": "diyecek", "dicem": "diyeceğim",
    "napalım": "ne yapalım", "napıyorsun": "ne yapıyorsun",
    "naber": "ne haber", "nbr": "ne haber",
    "slm": "selam", "mrb": "merhaba", "tşk": "teşekkür",
    "heralde": "herhalde", "galba": "galiba",
    "yaptıgı": "yaptığı", "oldugun": "olduğun", "oldugu": "olduğu",
    "yaptıgım": "yaptığım", "geldigim": "geldiğim",
    "soguk": "soğuk", "sicak": "sıcak", "kucuk": "küçük",
    "buyuk": "büyük", "guzel": "güzel", "gunaydın": "günaydın",
    "gorusmek": "görüşmek", "gorusuruz": "görüşürüz",
    "ozur": "özür", "ozaman": "o zaman",
    "ögretmen": "öğretmen", "ogrenci": "öğrenci", "ogretmen": "öğretmen",
    "universite": "üniversite",
    "turkiye": "Türkiye", "turkce": "Türkçe",
    "keske": "keşke", "herkez": "herkes", "herkezin": "herkesin",
    "progam": "program", "proğram": "program", "sistim": "sistem",
    "gerekioydu": "gerekiyordu", "olıyor": "oluyor", "gelıyor": "geliyor",
    "deil": "değil", "degil": "değil", "deği": "değil",
    "dahaönce": "daha önce",
    "bikaç": "birkaç", "bıkaç": "birkaç",
    "bazende": "bazen de", "ondanda": "ondan da",
    "bendede": "bende de", "sendede": "sende de",
    "iyiki": "iyi ki", "öyleki": "öyle ki", "böyleki": "böyle ki",
    "hemde": "hem de",
}


def check_punctuation_local(text):
    """Noktalama hatalarını yerel kurallarla kontrol eder."""
    errors = []
    stripped = text.rstrip()

    # Cümle sonu noktalama eksikliği
    if stripped and stripped[-1] not in '.!?…':
        errors.append({
            "type": "punctuation",
            "message": "Cümle sonunda noktalama işareti eksik. Nokta (.), ünlem (!) veya soru işareti (?) eklenmeli.",
            "original": "",
            "suggestion": "Sonuna nokta (.) ekleyin.",
        })

    # Birden fazla boşluk
    for m in re.finditer(r'  +', text):
        ctx = text[max(0, m.start()-10):m.end()+10]
        errors.append({
            "type": "punctuation",
            "message": f"Fazla boşluk tespit edildi: '...{ctx}...'",
            "original": m.group(),
            "suggestion": "Tek boşluk kullanın.",
        })

    # Noktalamadan önce boşluk
    for m in re.finditer(r' +([.!?,;:])', text):
        errors.append({
            "type": "punctuation",
            "message": f"'{m.group(1)}' işaretinden önce boşluk olmamalı.",
            "original": m.group(),
            "suggestion": m.group(1),
        })

    # Noktalamadan sonra boşluk eksik
    for m in re.finditer(r'([.!?,;:])([A-Za-zçÇğĞıİöÖşŞüÜ])', text):
        errors.append({
            "type": "punctuation",
            "message": f"'{m.group(1)}' işaretinden sonra boşluk bırakılmalı.",
            "original": m.group(),
            "suggestion": f"{m.group(1)} {m.group(2)}",
        })

    # Tekrarlanan noktalama
    for m in re.finditer(r'([.!?])\1{1,}', text):
        if m.group() != "...":
            errors.append({
                "type": "punctuation",
                "message": f"Tekrarlanan noktalama: '{m.group()}'",
                "original": m.group(),
                "suggestion": m.group(1),
            })

    # Cümle başı küçük harf
    for m in re.finditer(r'[.!?]\s+([a-zçğışöü])', text):
        char = m.group(1)
        errors.append({
            "type": "punctuation",
            "message": f"Cümle başında büyük harf kullanılmalı: '{char}' → '{char.upper()}'",
            "original": char,
            "suggestion": char.upper(),
        })

    # Metin başı küçük harf
    first = re.match(r'\s*([a-zçğışöü])', text)
    if first:
        char = first.group(1)
        errors.append({
            "type": "punctuation",
            "message": f"Metin başında büyük harf kullanılmalı: '{char}' → '{char.upper()}'",
            "original": char,
            "suggestion": char.upper(),
        })

    return errors


def check_spelling_local(text):
    """Yaygın yazım hatalarını yerel sözlükle kontrol eder."""
    errors = []
    for m in re.finditer(r'[a-zA-ZçÇğĞıİöÖşŞüÜâÂîÎûÛ]+', text):
        word = m.group()
        word_lower = word.lower()
        if word_lower in COMMON_MISSPELLINGS:
            correction = COMMON_MISSPELLINGS[word_lower]
            if correction is not None:
                errors.append({
                    "type": "spelling",
                    "message": f"'{word}' yanlış yazılmış olabilir.",
                    "original": word,
                    "suggestion": correction,
                })

    # Tekrarlanan kelime
    words = re.findall(r'[a-zA-ZçÇğĞıİöÖşŞüÜâÂîÎûÛ]+', text)
    for i in range(len(words) - 1):
        if words[i].lower() == words[i + 1].lower():
            errors.append({
                "type": "grammar",
                "message": f"Tekrarlanan kelime: '{words[i]}'",
                "original": f"{words[i]} {words[i+1]}",
                "suggestion": words[i],
            })

    return errors


# =============================================
# GEMİNİ API İLE YAPAY ZEKA ANALİZİ
# =============================================
GEMINI_SYSTEM_PROMPT = """Sen bir Türkçe dil uzmanısın. Sana verilen Türkçe metni analiz et ve şu hataları bul:

1. **Yazım hataları**: Yanlış yazılmış kelimeler (örn: "cünkü" → "çünkü")
2. **Noktalama hataları**: Eksik/yanlış noktalama işaretleri
3. **Dilbilgisi hataları**: Yanlış cümle yapıları, uyumsuzluklar
4. **Birleşik/ayrı yazım**: Ayrı yazılması gerekenler (örn: "herşey" → "her şey")
5. **Büyük/küçük harf**: Cümle başı, özel isimler vb.

SADECE gerçek hataları bildir. Doğru yazılmış kelimeleri hata olarak gösterme.

Yanıtını SADECE aşağıdaki JSON formatında ver, başka hiçbir şey yazma:
```json
{
  "errors": [
    {
      "type": "spelling|punctuation|grammar",
      "original": "hatalı kelime veya ifade",
      "suggestion": "doğru hali",
      "message": "Açıklama"
    }
  ],
  "corrected_text": "Düzeltilmiş metnin tamamı",
  "summary": "Kısa özet (1-2 cümle)"
}
```

Eğer hiç hata yoksa boş errors listesi döndür.
SADECE JSON döndür, markdown code block kullanma."""


def analyze_with_gemini(text, api_key):
    """Gemini API ile metni analiz eder."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

        response = model.generate_content(
            f"{GEMINI_SYSTEM_PROMPT}\n\nAnaliz edilecek metin:\n\"{text}\"",
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=2048,
            ),
        )

        response_text = response.text.strip()

        # JSON bloğunu ayıkla
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        result = json.loads(response_text)
        return result

    except json.JSONDecodeError:
        return {"errors": [], "corrected_text": text, "summary": "JSON ayrıştırma hatası oluştu.", "raw": response_text}
    except Exception as e:
        return {"errors": [], "corrected_text": text, "summary": f"API hatası: {str(e)}"}


# =============================================
# HIGHLIGHTED PREVIEW
# =============================================
def build_highlighted_html(text, errors):
    """Hatalı kısımları renkli olarak vurgular."""
    if not errors:
        return f'<div class="preview-box">{text}</div>'

    # Sort errors by position in text (find each error's position)
    positioned = []
    search_start = 0
    for err in errors:
        orig = err.get("original", "")
        if orig and orig in text[search_start:]:
            idx = text.index(orig, search_start)
            positioned.append((idx, idx + len(orig), err))

    positioned.sort(key=lambda x: x[0])

    # Remove overlaps
    filtered = []
    last_end = 0
    for start, end, err in positioned:
        if start >= last_end:
            filtered.append((start, end, err))
            last_end = end

    # Build HTML
    html_parts = []
    last_pos = 0
    for start, end, err in filtered:
        html_parts.append(_escape(text[last_pos:start]))
        etype = err.get("type", "spelling")
        css_class = f"highlight-{etype}"
        tooltip = _escape(err.get("message", ""))
        suggestion = err.get("suggestion", "")
        title = f"{tooltip} → {suggestion}" if suggestion else tooltip
        html_parts.append(f'<span class="{css_class}" title="{title}">{_escape(text[start:end])}</span>')
        last_pos = end

    html_parts.append(_escape(text[last_pos:]))

    return f'<div class="preview-box">{"".join(html_parts)}</div>'


def _escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# =============================================
# HEADER
# =============================================
st.markdown("""
<div class="main-header">
    <div class="logo">📝</div>
    <h1>Metin Kontrol</h1>
    <p>Yapay zeka destekli Türkçe yazım, noktalama ve dilbilgisi denetleyici. Google Gemini API ile güçlendirilmiştir.</p>
</div>
""", unsafe_allow_html=True)


# =============================================
# SIDEBAR
# =============================================
with st.sidebar:
    st.markdown("### ⚙️ Ayarlar")

    try:
        default_api = st.secrets["GEMINI_API_KEY"]
    except:
        default_api = ""

    api_key = st.text_input(
        "🔑 Gemini API Anahtarı",
        type="password",
        value=default_api,
        placeholder="AIza...",
        help="Google AI Studio'dan ücretsiz API anahtarı alabilirsiniz: https://aistudio.google.com/apikey"
    )

    st.markdown("---")

    st.markdown("### 📊 Analiz Yöntemi")
    analysis_mode = st.radio(
        "Denetleme Modu",
        ["🤖 Yapay Zeka (Gemini)", "📚 Yerel Sözlük", "🔀 Her İkisi"],
        index=2 if api_key else 1,
        help="Gemini API anahtarı girilirse yapay zeka modu aktif olur."
    )

    st.markdown("---")

    st.markdown("### 📖 Nasıl Kullanılır?")
    st.markdown("""
    1. Metin kutusuna Türkçe metninizi yazın
    2. **"🔍 Metni Kontrol Et"** butonuna tıklayın
    3. Hatalar renkli kartlarla gösterilir
    4. Düzeltilmiş metni kopyalayabilirsiniz
    """)

    st.markdown("---")
    st.markdown("### 🎨 Renk Kodları")
    st.markdown("""
    - 🔴 **Kırmızı** → Yazım hatası
    - 🟡 **Sarı** → Noktalama hatası
    - 🔵 **Mavi** → Dilbilgisi hatası
    - 🟣 **Mor** → Yapay zeka önerisi
    """)

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; color:#475569; font-size:0.75rem;">
        <p>Yapay Zeka Destekli</p>
        <p>Google Gemini API ile güçlendirilmiştir</p>
        <p>© 2026 Metin Kontrol</p>
    </div>
    """, unsafe_allow_html=True)


# =============================================
# ANA ALAN
# =============================================
# Metin girişi
text_input = st.text_area(
    "📝 Metninizi buraya yazın veya yapıştırın:",
    height=200,
    placeholder="Bugün hava çok güzeldi ama ben dışarı çıkmak istemedim cünkü ödevlerimi bitirmem gerekioydu.",
    key="text_input_area"
)

# Karakter sayısı ve butonlar
col_info, col_btn1, col_btn2 = st.columns([3, 1, 1])
with col_info:
    char_count = len(text_input) if text_input else 0
    word_count = len(text_input.split()) if text_input else 0
    st.caption(f"📊 {char_count} karakter · {word_count} kelime")
with col_btn1:
    check_clicked = st.button("🔍 Metni Kontrol Et", type="primary", use_container_width=True, disabled=not text_input)
with col_btn2:
    clear_clicked = st.button("🗑️ Temizle", use_container_width=True)

if clear_clicked:
    st.rerun()

# =============================================
# ANALİZ
# =============================================
if check_clicked and text_input:
    all_errors = []
    corrected_text = text_input
    ai_summary = ""

    use_local = analysis_mode in ["📚 Yerel Sözlük", "🔀 Her İkisi"]
    use_ai = analysis_mode in ["🤖 Yapay Zeka (Gemini)", "🔀 Her İkisi"] and api_key

    # --- Yerel analiz ---
    if use_local:
        with st.spinner("📚 Yerel sözlük ile kontrol ediliyor..."):
            local_spelling = check_spelling_local(text_input)
            local_punctuation = check_punctuation_local(text_input)
            all_errors.extend(local_spelling)
            all_errors.extend(local_punctuation)

    # --- Gemini AI analiz ---
    if use_ai:
        with st.spinner("🤖 Yapay zeka analiz ediyor..."):
            ai_result = analyze_with_gemini(text_input, api_key)

            if ai_result.get("errors"):
                for err in ai_result["errors"]:
                    # Yerel kontrolde zaten bulunan hataları tekrarlama
                    already_found = any(
                        e.get("original", "").lower() == err.get("original", "").lower()
                        for e in all_errors
                    )
                    if not already_found:
                        err["type"] = err.get("type", "ai")
                        if err["type"] not in ("spelling", "punctuation", "grammar"):
                            err["type"] = "ai"
                        all_errors.append(err)

            corrected_text = ai_result.get("corrected_text", text_input)
            ai_summary = ai_result.get("summary", "")

    elif analysis_mode in ["🤖 Yapay Zeka (Gemini)", "🔀 Her İkisi"] and not api_key:
        st.warning("⚠️ Gemini API anahtarı girilmedi. Sol menüden API anahtarınızı girin veya 'Yerel Sözlük' modunu seçin.")

    # --- İstatistikler ---
    total = len(all_errors)
    spelling_count = sum(1 for e in all_errors if e["type"] == "spelling")
    punct_count = sum(1 for e in all_errors if e["type"] == "punctuation")
    grammar_count = sum(1 for e in all_errors if e["type"] == "grammar")
    ai_count = sum(1 for e in all_errors if e["type"] == "ai")

    st.markdown(f"""
    <div class="stats-row">
        <div class="stat-card total">
            <div class="value">{total}</div>
            <div class="label">Toplam Hata</div>
        </div>
        <div class="stat-card spelling">
            <div class="value">{spelling_count}</div>
            <div class="label">Yazım Hatası</div>
        </div>
        <div class="stat-card punctuation">
            <div class="value">{punct_count}</div>
            <div class="label">Noktalama</div>
        </div>
        <div class="stat-card grammar">
            <div class="value">{grammar_count}</div>
            <div class="label">Dilbilgisi</div>
        </div>
        <div class="stat-card ai">
            <div class="value">{ai_count}</div>
            <div class="label">AI Önerisi</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Sonuçlar ---
    if total == 0:
        st.markdown("""
        <div class="success-box">
            <div class="icon">✅</div>
            <h3>Harika!</h3>
            <p>Metninizde herhangi bir hata bulunamadı.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        tab1, tab2, tab3 = st.tabs(["🔎 Bulunan Hatalar", "👁️ Önizleme", "✅ Düzeltilmiş Metin"])

        with tab1:
            for i, err in enumerate(all_errors):
                etype = err.get("type", "spelling")
                badge_text = {"spelling": "✏️ Yazım", "punctuation": "📌 Noktalama", "grammar": "📝 Dilbilgisi", "ai": "🤖 AI"}.get(etype, "📋 Diğer")
                suggestion = err.get("suggestion", "")
                original = err.get("original", "")

                suggestion_html = ""
                if suggestion:
                    suggestion_html = f'<span class="suggestion-chip">→ {_escape(suggestion)}</span>'

                context_html = ""
                if original:
                    context_html = f'<div class="error-context">"{_escape(original)}"</div>'

                st.markdown(f"""
                <div class="error-card">
                    <div class="error-badge {etype}">{badge_text}</div>
                    <div class="error-message">{_escape(err.get("message", ""))}</div>
                    {context_html}
                    {suggestion_html}
                </div>
                """, unsafe_allow_html=True)

        with tab2:
            html = build_highlighted_html(text_input, all_errors)
            st.markdown(html, unsafe_allow_html=True)
            st.caption("💡 Hatalı kelimelerin üzerine gelince detay görebilirsiniz.")

        with tab3:
            if corrected_text and corrected_text != text_input:
                st.markdown("**Düzeltilmiş metin:**")
                st.text_area("", value=corrected_text, height=200, key="corrected_output")
                st.caption("📋 Yukarıdaki düzeltilmiş metni kopyalayabilirsiniz.")
            else:
                st.info("Düzeltilmiş metin mevcut değil. Gemini API modunu aktif edin veya metinde gerçek hata olduğundan emin olun.")

        # AI Özeti
        if ai_summary:
            st.markdown("---")
            st.markdown(f"**🤖 Yapay Zeka Özeti:** {ai_summary}")

# =============================================
# FOOTER
# =============================================
st.markdown("""
<div class="footer">
    <p>📝 Metin Kontrol — Yapay Zeka Destekli Türkçe Yazım Denetleyici</p>
    <p>Google Gemini API · Python · Streamlit</p>
</div>
""", unsafe_allow_html=True)
