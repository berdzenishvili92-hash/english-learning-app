import streamlit as st
import streamlit.components.v1 as components
import anthropic
import base64
import json
import re
import os
import hashlib
import datetime

# ══════════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════════
ANTHROPIC_API_KEY = "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"
MODEL = "claude-sonnet-4-6"

# ბაზის ფაილი — ამ ფაილის გადაწერა = სრული სარეზერვო ასლი
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "english_learning_data.json")

# ══════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="English Learning App",
    page_icon="📚",
    layout="centered",
    initial_sidebar_state="auto",
)

# ══════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main {
    background: linear-gradient(160deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}
.main .block-container { max-width: 860px; padding: 1.5rem 1rem; }

/* ── login page ── */
.auth-card {
    background: rgba(255,255,255,0.06);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 24px;
    padding: 2rem 2rem 1.5rem;
    margin: 1rem 0;
}

/* ── page hero ── */
.page-hero {
    background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.03));
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 24px;
    padding: 1.8rem 2rem 1.4rem;
    margin-bottom: 1.5rem;
    color: #fff;
}
.page-hero h1 { font-size: 1.9rem; font-weight: 800; margin: 0 0 .3rem; letter-spacing: -.5px; }
.page-hero p  { font-size: .95rem; opacity: .65; margin: 0; }

/* ── user badge in sidebar ── */
.user-badge {
    background: linear-gradient(135deg, rgba(99,102,241,.3), rgba(139,92,246,.3));
    border: 1px solid rgba(99,102,241,.4);
    border-radius: 16px;
    padding: .9rem 1rem;
    margin-bottom: .8rem;
    text-align: center;
}
.user-avatar {
    width: 52px; height: 52px;
    background: linear-gradient(135deg,#6366f1,#8b5cf6);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.4rem; font-weight: 800; color: #fff;
    margin: 0 auto .5rem;
}
.user-name  { font-size: 1rem; font-weight: 700; color: #e0e7ff; }
.user-uname { font-size: .78rem; color: rgba(255,255,255,.45); }

/* ── backup box ── */
.backup-box {
    background: rgba(16,185,129,.1);
    border: 1px solid rgba(52,211,153,.25);
    border-radius: 12px;
    padding: .7rem .9rem;
    font-size: .78rem;
    color: #a7f3d0;
    word-break: break-all;
    margin: .4rem 0;
}

/* ── word cards ── */
.word-card {
    background: linear-gradient(135deg,#6366f1 0%,#8b5cf6 100%);
    border-radius: 20px; padding: 1.3rem 1.4rem 1rem;
    margin: .8rem 0; color: #fff;
    box-shadow: 0 8px 32px rgba(99,102,241,.35);
    border: 1px solid rgba(255,255,255,0.15);
}
.word-card.known {
    background: linear-gradient(135deg,#10b981 0%,#059669 100%);
    box-shadow: 0 6px 20px rgba(16,185,129,.3); opacity:.8;
}
.review-card {
    background: linear-gradient(135deg,#f43f5e 0%,#e11d48 100%);
    border-radius: 20px; padding: 1.3rem 1.4rem 1rem;
    margin: .8rem 0; color: #fff;
    box-shadow: 0 8px 32px rgba(244,63,94,.35);
    border: 1px solid rgba(255,255,255,0.15);
}
.word-badge {
    display: inline-block; background: rgba(255,255,255,0.2);
    border-radius: 30px; padding: .15rem .7rem;
    font-size: .7rem; font-weight: 600; letter-spacing: .5px;
    text-transform: uppercase; margin-bottom: .6rem;
}
.word-title    { font-size: 1.5rem; font-weight: 800; letter-spacing: -.3px; margin-bottom: .15rem; }
.word-phonetic { font-size: .9rem; opacity: .6; font-style: italic; margin-bottom: .4rem; letter-spacing: .5px; }
.word-trans    { font-size: 1rem; opacity: .85; font-weight: 500; margin-bottom: .5rem; }
.word-def      { font-size: .88rem; opacity: .8; margin-bottom: .5rem; line-height: 1.5; }
.word-example  {
    font-size: .82rem; opacity: .7; font-style: italic;
    background: rgba(0,0,0,0.15); border-radius: 10px;
    padding: .5rem .75rem; line-height: 1.5;
}

/* ── stat boxes ── */
.stat-box {
    background: rgba(255,255,255,0.07);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 18px; padding: 1.2rem .8rem; text-align: center;
}
.stat-label { font-size: .78rem; color: rgba(255,255,255,.5); margin-top: .3rem; text-transform: uppercase; letter-spacing: .5px; }
.stat-num         { font-size: 2.2rem; font-weight: 800; color: #a5b4fc; }
.stat-num.green   { color: #34d399; }
.stat-num.red     { color: #fb7185; }

/* ── banners ── */
.banner-info {
    background: linear-gradient(135deg,rgba(59,130,246,.3),rgba(6,182,212,.3));
    border: 1px solid rgba(99,179,237,.3); color: #e0f2fe;
    border-radius: 16px; padding: 1rem 1.2rem; margin: .6rem 0; line-height: 1.7;
}
.banner-ok {
    background: linear-gradient(135deg,rgba(16,185,129,.3),rgba(5,150,105,.3));
    border: 1px solid rgba(52,211,153,.3); color: #d1fae5;
    border-radius: 16px; padding: 1rem 1.2rem; margin: .6rem 0;
}

/* ── sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#1e1b4b 0%,#0f0c29 100%);
    border-right: 1px solid rgba(255,255,255,0.06);
}
[data-testid="stSidebar"] * { color: rgba(255,255,255,.85) !important; }

/* ── buttons ── */
.stButton > button {
    border-radius: 12px !important; font-weight: 600 !important;
}

/* ── chat ── */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 16px !important; margin: .4rem 0 !important;
}

/* ── text ── */
h1,h2,h3,h4,p,span,label,.stMarkdown { color: rgba(255,255,255,.9) !important; }
.stCaption { color: rgba(255,255,255,.45) !important; }
hr { border-color: rgba(255,255,255,0.08) !important; }

@media (max-width:640px) {
    .page-hero h1 { font-size: 1.4rem; }
    .word-title   { font-size: 1.2rem; }
    .main .block-container { padding: .6rem .4rem; }
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
#  DATABASE (JSON ფაილი)
# ══════════════════════════════════════════════
def _hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

def _load_db() -> dict:
    if not os.path.exists(DATA_FILE):
        return {"version": 1, "users": {}}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"version": 1, "users": {}}

def _write_db(db: dict):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def save_user_data():
    """მიმდინარე მომხმარებლის მონაცემები ფაილში შეინახოს."""
    if not st.session_state.get("logged_in"):
        return
    db = _load_db()
    uname = st.session_state.current_user
    if uname in db["users"]:
        db["users"][uname]["dictionary"]  = st.session_state.dictionary
        db["users"][uname]["known_words"] = st.session_state.known_words
        db["users"][uname]["review_list"] = st.session_state.review_list
        _write_db(db)

# ══════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════
def _init():
    defaults = {
        "logged_in":     False,
        "current_user":  "",
        "display_name":  "",
        "dictionary":    [],
        "known_words":   [],
        "review_list":   [],
        "chat_history":  [],
        "scanned_text":  "",
        "scanned_words": [],
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

# ══════════════════════════════════════════════
#  ANTHROPIC CLIENT
# ══════════════════════════════════════════════
@st.cache_resource
def get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# ══════════════════════════════════════════════
#  LOGIN / REGISTER PAGE
# ══════════════════════════════════════════════
def page_auth():
    st.markdown("""
    <div class="page-hero" style="text-align:center;">
        <h1>📚 English Learning</h1>
        <p>AI-powered ინგლისურის სასწავლო პლატფორმა</p>
    </div>
    """, unsafe_allow_html=True)

    tab_in, tab_reg, tab_restore = st.tabs(["🔑 შესვლა", "✨ რეგისტრაცია", "♻️ ბაზის აღდგენა"])

    # ── შესვლა ──
    with tab_in:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        uname = st.text_input("მომხმარებლის სახელი", key="li_u", placeholder="username")
        passw = st.text_input("პაროლი", type="password", key="li_p")
        if st.button("შესვლა →", type="primary", use_container_width=True, key="li_btn"):
            if not uname or not passw:
                st.error("შეავსე ყველა ველი")
            else:
                db = _load_db()
                user = db["users"].get(uname.strip().lower())
                if not user:
                    st.error("❌ მომხმარებელი ვერ მოიძებნა")
                elif user["password_hash"] != _hash_pw(passw):
                    st.error("❌ პაროლი არასწორია")
                else:
                    st.session_state.logged_in    = True
                    st.session_state.current_user = uname.strip().lower()
                    st.session_state.display_name = user["display_name"]
                    st.session_state.dictionary   = user.get("dictionary", [])
                    st.session_state.known_words  = user.get("known_words", [])
                    st.session_state.review_list  = user.get("review_list", [])
                    st.session_state.chat_history = []
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── რეგისტრაცია ──
    with tab_reg:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        disp  = st.text_input("სახელი (ნებისმიერი)", key="rg_d", placeholder="მაგ: გიორგი")
        uname_r = st.text_input("Username (ლათინური, პატარა)", key="rg_u", placeholder="მაგ: giorgi")
        pw1   = st.text_input("პაროლი", type="password", key="rg_p1")
        pw2   = st.text_input("პაროლის გამეორება", type="password", key="rg_p2")
        if st.button("რეგისტრაცია →", type="primary", use_container_width=True, key="rg_btn"):
            if not all([disp, uname_r, pw1, pw2]):
                st.error("შეავსე ყველა ველი")
            elif pw1 != pw2:
                st.error("❌ პაროლები არ ემთხვევა")
            elif len(pw1) < 4:
                st.error("❌ პაროლი მინიმუმ 4 სიმბოლო")
            elif not re.match(r'^[a-z0-9_]+$', uname_r.lower()):
                st.error("❌ Username-ში მხოლოდ ლათინური ასოები, ციფრები და _ ")
            else:
                db = _load_db()
                if uname_r.lower() in db["users"]:
                    st.error("❌ ეს username უკვე გამოყენებულია")
                else:
                    db["users"][uname_r.lower()] = {
                        "password_hash": _hash_pw(pw1),
                        "display_name":  disp,
                        "created_at":    str(datetime.date.today()),
                        "dictionary":    [],
                        "known_words":   [],
                        "review_list":   [],
                    }
                    _write_db(db)
                    st.success("✅ რეგისტრაცია წარმატებულია! გადადი 'შესვლა' tab-ზე.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── ბაზის აღდგენა ──
    with tab_restore:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.markdown("**სარეზერვო ფაილიდან აღდგენა:**")
        st.caption("ატვირთე შენახული `english_learning_data.json` ფაილი")
        backup = st.file_uploader("ფაილის ატვირთვა", type=["json"], key="restore_file")
        if backup:
            try:
                data = json.loads(backup.read().decode("utf-8"))
                if "users" not in data:
                    st.error("❌ ეს სწორი სარეზერვო ფაილი არ არის")
                else:
                    users = list(data["users"].keys())
                    st.success(f"✅ ფაილში ნაპოვნია {len(users)} მომხმარებელი: {', '.join(users)}")
                    if st.button("🔄 ბაზის აღდგენა", type="primary", use_container_width=True, key="do_restore"):
                        _write_db(data)
                        st.success("✅ ბაზა წარმატებით აღდგა! ახლა შეგიძლია შეხვიდე.")
                        st.rerun()
            except Exception as e:
                st.error(f"❌ ფაილის წაკითხვის შეცდომა: {e}")
        st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
#  AUTH GATE
# ══════════════════════════════════════════════
if not st.session_state.logged_in:
    page_auth()
    st.stop()


# ══════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════
def _to_base64(f) -> str:
    return base64.standard_b64encode(f.getvalue()).decode("utf-8")

def _parse_json_words(text: str):
    text = re.sub(r"```(?:json)?", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\[.*\]", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group())
        except json.JSONDecodeError:
            pass
    return None

def _is_known(word: str) -> bool:
    return word.lower() in st.session_state.known_words

def _add_to_dictionary(words: list) -> int:
    existing = {w["word"].lower() for w in st.session_state.dictionary}
    added = 0
    for w in words:
        if w["word"].lower() not in existing:
            st.session_state.dictionary.append(w)
            existing.add(w["word"].lower())
            added += 1
    if added:
        save_user_data()
    return added

def _tokenize_words(text: str) -> list:
    seen, result = set(), []
    for w in re.findall(r"[a-zA-Z']+", text):
        wc = w.strip("'")
        if len(wc) >= 4:
            k = wc.lower()
            if k not in seen:
                seen.add(k); result.append(wc)
    return result


# ══════════════════════════════════════════════
#  ANTHROPIC FUNCTIONS
# ══════════════════════════════════════════════
def analyze_image(uploaded_file):
    client = get_client()
    b64 = _to_base64(uploaded_file)
    prompt = (
        "Please read every word in this image carefully.\n"
        "Then pick exactly 5 interesting English words at B1–C1 level.\n\n"
        "Return ONLY a valid JSON array:\n"
        '[\n  {\n    "word": "example",\n'
        '    "georgian_phonetic": "ეგზამპლ",\n'
        '    "georgian_translation": "მაგალითი",\n'
        '    "english_definition": "A single sentence.",\n'
        '    "context_example": "Exact sentence from image."\n  }\n]\n\n'
        "Rules: exactly 5 words, georgian_phonetic uses Georgian letters for English sound, output only JSON."
    )
    msg = client.messages.create(
        model=MODEL, max_tokens=1500,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": uploaded_file.type, "data": b64}},
            {"type": "text", "text": prompt},
        ]}],
    )
    raw = msg.content[0].text
    return _parse_json_words(raw), raw

def extract_all_text(uploaded_file) -> str:
    client = get_client()
    b64 = _to_base64(uploaded_file)
    msg = client.messages.create(
        model=MODEL, max_tokens=2000,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": uploaded_file.type, "data": b64}},
            {"type": "text", "text": "Transcribe ALL text in this image exactly as written. Output only the text."},
        ]}],
    )
    return msg.content[0].text.strip()

def define_words(word_list: list, context: str) -> list:
    client = get_client()
    words_str = ", ".join(f'"{w}"' for w in word_list)
    prompt = (
        f'Text:\n"""\n{context}\n"""\n\n'
        f"Define these words: {words_str}\n\n"
        "Return ONLY a JSON array:\n"
        '[\n  {\n    "word": "example",\n'
        '    "georgian_phonetic": "ეგზამპლ",\n'
        '    "georgian_translation": "მაგალითი",\n'
        '    "english_definition": "A single sentence.",\n'
        '    "context_example": "Sentence from text."\n  }\n]\n'
        "Output only JSON."
    )
    msg = client.messages.create(
        model=MODEL, max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )
    return _parse_json_words(msg.content[0].text) or []

def chat_with_teacher(user_msg: str, history: list) -> str:
    client = get_client()
    system = (
        "You are a friendly English teacher. Talk in simple, clear English. "
        "If the user makes a grammar mistake, correct it simply, explain the rule in 1 sentence, "
        "then continue the conversation.\n\n"
        "Format corrections:\n"
        "✏️ Correction: [corrected sentence]\n"
        "📌 Rule: [one-sentence explanation]\n\n"
        "Keep responses concise and encouraging."
    )
    messages = [{"role": m["role"], "content": m["content"]} for m in history]
    messages.append({"role": "user", "content": user_msg})
    resp = client.messages.create(model=MODEL, max_tokens=800, system=system, messages=messages)
    return resp.content[0].text


# ══════════════════════════════════════════════
#  RENDER CARD
# ══════════════════════════════════════════════
def _render_card(word_data: dict, card_class: str, card_key: str, show_buttons: bool = True):
    word     = word_data.get("word", "")
    phonetic = word_data.get("georgian_phonetic", "")
    trans    = word_data.get("georgian_translation", "")
    defn     = word_data.get("english_definition", "")
    ex       = word_data.get("context_example", "")
    word_l   = word.lower()
    is_known = _is_known(word)

    phonetic_html = f'<div class="word-phonetic">[ {phonetic} ]</div>' if phonetic else ""
    badge = "✅ ვიცი" if is_known else "📖 ახალი სიტყვა"

    st.markdown(f"""
    <div class="{card_class}{'  known' if is_known else ''}">
        <div class="word-badge">{badge}</div>
        <div class="word-title">{word}</div>
        {phonetic_html}
        <div class="word-trans">🇬🇪 {trans}</div>
        <div class="word-def">💡 {defn}</div>
        <div class="word-example">"{ex}"</div>
    </div>
    """, unsafe_allow_html=True)

    safe = word.replace("'", "\\'").replace('"', "&quot;")
    if st.button(f"🔊 გამოთქმა — {word}", key=f"speak_{card_key}", use_container_width=True):
        components.html(
            f"<script>var u=new SpeechSynthesisUtterance('{safe}');u.lang='en-US';u.rate=0.82;"
            "speechSynthesis.cancel();speechSynthesis.speak(u);</script>",
            height=0,
        )

    if not show_buttons:
        return

    col1, col2 = st.columns(2)
    with col1:
        lbl = "✅ ვიცი ✓" if is_known else "✅ ვიცი"
        if st.button(lbl, key=f"know_{card_key}", use_container_width=True,
                     type="primary" if is_known else "secondary"):
            if word_l not in st.session_state.known_words:
                st.session_state.known_words.append(word_l)
            st.session_state.review_list = [r for r in st.session_state.review_list
                                             if r["word"].lower() != word_l]
            save_user_data()
            st.rerun()
    with col2:
        if st.button("❌ არ ვიცი", key=f"dontknow_{card_key}", use_container_width=True):
            st.session_state.known_words = [w for w in st.session_state.known_words if w != word_l]
            if word_l not in [r["word"].lower() for r in st.session_state.review_list]:
                st.session_state.review_list.append(word_data)
            save_user_data()
            st.rerun()


# ══════════════════════════════════════════════
#  PAGE: VISION
# ══════════════════════════════════════════════
def page_vision():
    st.markdown("""
    <div class="page-hero">
        <h1>📷 ტექსტის დამუშავება</h1>
        <p>ატვირთე ტექსტიანი სურათი — ავტომატურად ან სიტყვები თავად აირჩიე</p>
    </div>
    """, unsafe_allow_html=True)

    mode = st.radio("რეჟიმი:", ["🤖 ავტომატური (5 სიტყვა)", "✋ ხელით არჩევა"],
                    horizontal=True, key="vision_mode_radio")
    uploaded = st.file_uploader("სურათის ატვირთვა", type=["jpg","jpeg","png","webp"],
                                help="მობილურზე კამერა გაიხსნება")

    if uploaded is None:
        st.markdown("""<div class="banner-info">
            📱 <strong>გამოყენება:</strong><br>
            1. აირჩიე რეჟიმი ზემოთ<br>
            2. ატვირთე სურათი ტექსტით<br>
            3. <strong>ავტომატური</strong> — Claude 5 საუკეთესო სიტყვას ამოარჩევს<br>
            4. <strong>ხელით</strong> — ტექსტი ამოდის, შენ ირჩევ
        </div>""", unsafe_allow_html=True)
        return

    st.image(uploaded, caption="ატვირთული სურათი", use_container_width=True)

    if mode == "🤖 ავტომატური (5 სიტყვა)":
        if st.button("🔍 სიტყვების ამოღება", type="primary", use_container_width=True):
            with st.spinner("Claude კითხულობს სურათს…"):
                try:
                    words, raw = analyze_image(uploaded)
                except anthropic.AuthenticationError:
                    st.error("❌ API გასაღები არასწორია.")
                    return
                except Exception as exc:
                    st.error(f"❌ შეცდომა: {exc}")
                    return
            if not words:
                st.error("ვერ მოხერხდა JSON-ის წაკითხვა.")
                with st.expander("Raw პასუხი"):
                    st.code(raw)
                return
            added = _add_to_dictionary(words)
            st.markdown(f"""<div class="banner-ok">✨ ნაპოვნია <strong>{len(words)}</strong> სიტყვა —
                <strong>{added}</strong> ახალი დაემატა ლექსიკონს!</div>""", unsafe_allow_html=True)
            for i, w in enumerate(words):
                _render_card(w, "word-card", f"vision_{i}", show_buttons=False)
    else:
        c1, c2 = st.columns([3,1])
        with c1:
            scan = st.button("🔎 ტექსტის სკანირება", type="primary", use_container_width=True)
        with c2:
            if st.button("🗑️", use_container_width=True, help="სკანირების გასუფთავება"):
                st.session_state.scanned_text = ""; st.session_state.scanned_words = []; st.rerun()

        if scan:
            with st.spinner("Claude ტექსტს კითხულობს…"):
                try:
                    raw_text = extract_all_text(uploaded)
                except Exception as exc:
                    st.error(f"❌ {exc}"); st.stop()
            st.session_state.scanned_text  = raw_text
            st.session_state.scanned_words = _tokenize_words(raw_text)

        if st.session_state.scanned_text:
            with st.expander("📄 ამოღებული ტექსტი", expanded=False):
                st.text(st.session_state.scanned_text)
            if not st.session_state.scanned_words:
                st.warning("სურათში ინგლისური სიტყვები ვერ მოიძებნა."); return

            selected = st.multiselect(
                "📌 აირჩიე სიტყვები რომელთა სწავლა გინდა:",
                options=st.session_state.scanned_words,
                placeholder="დააწკაპე სიტყვებზე…",
                key="manual_sel",
            )
            if selected:
                if st.button(f"📖 {len(selected)} სიტყვის განმარტება",
                             type="primary", use_container_width=True, key="def_btn"):
                    with st.spinner("Claude განმარტებებს ამზადებს…"):
                        try:
                            words = define_words(selected, st.session_state.scanned_text)
                        except Exception as exc:
                            st.error(f"❌ {exc}"); st.stop()
                    if not words:
                        st.error("Claude-მა ვერ დაამუშავა."); return
                    added = _add_to_dictionary(words)
                    st.markdown(f"""<div class="banner-ok">✨ <strong>{added}</strong> ახალი სიტყვა დაემატა!</div>""",
                                unsafe_allow_html=True)
                    for i, w in enumerate(words):
                        _render_card(w, "word-card", f"man_{i}", show_buttons=False)


# ══════════════════════════════════════════════
#  PAGE: DICTIONARY
# ══════════════════════════════════════════════
def page_dictionary():
    st.markdown("""
    <div class="page-hero">
        <h1>📚 ჩემი ლექსიკონი</h1>
        <p>შენი შენახული სიტყვები — ავტომატურად ინახება ფაილში</p>
    </div>
    """, unsafe_allow_html=True)

    total    = len(st.session_state.dictionary)
    known_n  = len(st.session_state.known_words)
    review_n = len(st.session_state.review_list)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-box"><div class="stat-num">{total}</div>'
                    '<div class="stat-label">სულ სიტყვა</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-box"><div class="stat-num green">{known_n}</div>'
                    '<div class="stat-label">ვიცი</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-box"><div class="stat-num red">{review_n}</div>'
                    '<div class="stat-label">გასამეორებელი</div></div>', unsafe_allow_html=True)

    st.divider()

    if total == 0:
        st.info("ლექსიკონი ცარიელია.\n\nგადადი **📷 ტექსტის დამუშავება** გვერდზე!")
        return

    if review_n > 0:
        with st.expander(f"🔄 გასამეორებელი სიტყვები ({review_n})", expanded=True):
            for i, w in enumerate(st.session_state.review_list):
                _render_card(w, "review-card", f"rev_{i}")

    st.subheader(f"ყველა სიტყვა ({total})")
    filt = st.selectbox("ფილტრი:", ["ყველა", "მხოლოდ ვიცი", "მხოლოდ არ ვიცი"], key="dict_filter")

    for i, w in enumerate(st.session_state.dictionary):
        is_known = _is_known(w["word"])
        if filt == "მხოლოდ ვიცი"   and not is_known: continue
        if filt == "მხოლოდ არ ვიცი" and is_known:     continue
        _render_card(w, "word-card", f"dict_{i}")


# ══════════════════════════════════════════════
#  PAGE: CHAT
# ══════════════════════════════════════════════
def page_chat():
    st.markdown("""
    <div class="page-hero">
        <h1>💬 სალაპარაკო გრამატიკა</h1>
        <p>ესაუბრე AI მასწავლებელს — გრამატიკის შეცდომებს ავტომატურად გაასწორებს</p>
    </div>
    """, unsafe_allow_html=True)

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if not st.session_state.chat_history:
        with st.chat_message("assistant"):
            st.markdown("Hello! 👋 I'm your friendly English teacher. How are you today? "
                        "Feel free to write anything in English! 😊")

    if user_input := st.chat_input("Write in English… / დაწერე ინგლისურად…"):
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            with st.spinner("…"):
                try:
                    reply = chat_with_teacher(user_input, st.session_state.chat_history)
                except anthropic.AuthenticationError:
                    reply = "❌ API გასაღები არასწორია."
                except Exception as exc:
                    reply = f"❌ შეცდომა: {exc}"
            st.markdown(reply)
        st.session_state.chat_history.append({"role": "user",      "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": reply})

    if st.session_state.chat_history:
        if st.button("🗑️ საუბრის გასუფთავება", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()


# ══════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════
with st.sidebar:
    initials = st.session_state.display_name[:1].upper() if st.session_state.display_name else "?"
    st.markdown(f"""
    <div class="user-badge">
        <div class="user-avatar">{initials}</div>
        <div class="user-name">{st.session_state.display_name}</div>
        <div class="user-uname">@{st.session_state.current_user}</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    page = st.radio("გვერდი:", [
        "📷 ტექსტის დამუშავება",
        "📚 ჩემი ლექსიკონი",
        "💬 სალაპარაკო გრამატიკა",
    ], key="nav_page")
    st.divider()

    st.metric("სიტყვები",       len(st.session_state.dictionary))
    st.metric("გასამეორებელი", len(st.session_state.review_list))
    st.divider()

    st.caption("💾 სარეზერვო ფაილი:")
    st.markdown(f'<div class="backup-box">{DATA_FILE}</div>', unsafe_allow_html=True)
    st.caption("ამ ფაილის გადაწერა = სრული სარეზერვო ასლი")

    if st.button("💾 ხელით შენახვა", use_container_width=True):
        save_user_data()
        st.success("შენახულია!")

    st.divider()
    if st.button("🚪 გამოსვლა", use_container_width=True):
        save_user_data()
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()


# ══════════════════════════════════════════════
#  ROUTER
# ══════════════════════════════════════════════
if   page == "📷 ტექსტის დამუშავება":   page_vision()
elif page == "📚 ჩემი ლექსიკონი":       page_dictionary()
elif page == "💬 სალაპარაკო გრამატიკა": page_chat()
