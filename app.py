import streamlit as st
import cv2
import easyocr
import re
import numpy as np
import pandas as pd
import mysql.connector
from mysql.connector import Error
from ultralytics import YOLO
from PIL import Image
import io
import time
from datetime import datetime

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="VehicleID — AI Number Plate Recognition",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&family=Outfit:wght@300;400;500;600&display=swap');

/* ── Root Variables ── */
:root {
    --bg-dark:       #0a0c10;
    --bg-card:       #10141c;
    --bg-card2:      #151a25;
    --border:        #1e2535;
    --border-bright: #2a3550;
    --accent:        #00d4ff;
    --accent2:       #0099cc;
    --accent-glow:   rgba(0,212,255,0.15);
    --success:       #00e676;
    --danger:        #ff4444;
    --warning:       #ffa726;
    --text-primary:  #e8eaf0;
    --text-secondary:#8892a4;
    --text-muted:    #4a5568;
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
    background-color: var(--bg-dark);
    color: var(--text-primary);
}

.stApp { background-color: var(--bg-dark); }

/* ── Hide Streamlit defaults ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 2rem; max-width: 1400px; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--bg-card) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] .block-container { padding: 1.5rem 1.2rem; }

/* ── Top Banner ── */
.top-banner {
    background: linear-gradient(135deg, #0d1117 0%, #0a1628 50%, #0d1117 100%);
    border: 1px solid var(--border-bright);
    border-radius: 12px;
    padding: 1.4rem 2rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
    position: relative;
    overflow: hidden;
}
.top-banner::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
}
.top-banner::after {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(0,212,255,0.06) 0%, transparent 70%);
    border-radius: 50%;
}
.banner-icon { font-size: 2.4rem; filter: drop-shadow(0 0 12px var(--accent)); }
.banner-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: 2px;
    text-transform: uppercase;
    line-height: 1.1;
}
.banner-sub {
    font-size: 0.8rem;
    color: var(--text-secondary);
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 2px;
}
.banner-badge {
    margin-left: auto;
    background: rgba(0,212,255,0.08);
    border: 1px solid rgba(0,212,255,0.3);
    border-radius: 20px;
    padding: 0.3rem 0.9rem;
    font-size: 0.72rem;
    color: var(--accent);
    letter-spacing: 2px;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Cards ── */
.card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}
.card-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--text-secondary);
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.card-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ── Plate Display ── */
.plate-display {
    background: linear-gradient(135deg, #fff8e1, #fffde7);
    border: 3px solid #f9a825;
    border-radius: 8px;
    padding: 0.6rem 1.4rem;
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    color: #1a1a1a;
    letter-spacing: 6px;
    box-shadow: 0 4px 20px rgba(249,168,37,0.3),
                inset 0 1px 0 rgba(255,255,255,0.8);
    margin: 0.8rem 0;
}

/* ── Owner Card ── */
.owner-found {
    background: linear-gradient(135deg, rgba(0,230,118,0.05), rgba(0,230,118,0.02));
    border: 1px solid rgba(0,230,118,0.25);
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    position: relative;
    overflow: hidden;
}
.owner-found::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--success), transparent);
}
.owner-not-found {
    background: rgba(255,68,68,0.05);
    border: 1px solid rgba(255,68,68,0.2);
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    text-align: center;
}
.owner-label {
    font-size: 0.68rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 2px;
}
.owner-value {
    font-size: 1rem;
    font-weight: 500;
    color: var(--text-primary);
    font-family: 'Outfit', sans-serif;
}
.owner-name-big {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--success);
    letter-spacing: 1px;
    margin-bottom: 0.8rem;
}

/* ── Status Badges ── */
.badge-found {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(0,230,118,0.1);
    border: 1px solid rgba(0,230,118,0.3);
    color: var(--success);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 1px;
}
.badge-not-found {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(255,68,68,0.1);
    border: 1px solid rgba(255,68,68,0.3);
    color: var(--danger);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 1px;
}

/* ── Metric Boxes ── */
.metric-row { display: flex; gap: 0.8rem; margin-bottom: 1rem; }
.metric-box {
    flex: 1;
    background: var(--bg-card2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.9rem 1rem;
    text-align: center;
}
.metric-val {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--accent);
    line-height: 1;
}
.metric-lbl {
    font-size: 0.65rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-top: 4px;
}

/* ── Table ── */
.stDataFrame {
    border-radius: 8px !important;
    overflow: hidden !important;
    border: 1px solid var(--border) !important;
}
[data-testid="stDataFrameResizable"] th {
    background: #151a25 !important;
    color: var(--accent) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: 1px !important;
    text-transform: uppercase !important;
}
[data-testid="stDataFrameResizable"] td {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.82rem !important;
    color: var(--text-primary) !important;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, var(--accent2), var(--accent)) !important;
    color: #0a0c10 !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 15px rgba(0,212,255,0.2) !important;
}
.stButton > button:hover {
    box-shadow: 0 6px 25px rgba(0,212,255,0.4) !important;
    transform: translateY(-1px) !important;
}

/* ── Inputs ── */
.stTextInput input, .stSelectbox select {
    background: var(--bg-card2) !important;
    border: 1px solid var(--border-bright) !important;
    border-radius: 6px !important;
    color: var(--text-primary) !important;
    font-family: 'JetBrains Mono', monospace !important;
}
.stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-glow) !important;
}

/* ── File Uploader ── */
[data-testid="stFileUploader"] {
    background: var(--bg-card2) !important;
    border: 1px dashed var(--border-bright) !important;
    border-radius: 8px !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--accent) !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Sidebar labels ── */
.sidebar-section {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: var(--text-muted);
    margin: 1.2rem 0 0.5rem;
    padding-bottom: 0.3rem;
    border-bottom: 1px solid var(--border);
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--accent) !important; }

/* ── Confidence bar ── */
.conf-bar-wrap {
    background: var(--bg-card2);
    border-radius: 4px;
    height: 6px;
    width: 100%;
    overflow: hidden;
    margin-top: 4px;
}
.conf-bar-fill {
    height: 100%;
    border-radius: 4px;
    background: linear-gradient(90deg, var(--accent2), var(--accent));
    transition: width 0.5s ease;
}

/* ── OCR raw text ── */
.raw-ocr {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-secondary);
    background: var(--bg-card2);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 0.3rem 0.7rem;
    display: inline-block;
    margin-top: 4px;
}

/* ── Log entries ── */
.log-entry {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.82rem;
}
.log-plate {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    color: var(--accent);
    min-width: 110px;
}
.log-time {
    color: var(--text-muted);
    font-size: 0.72rem;
    font-family: 'JetBrains Mono', monospace;
    margin-left: auto;
}
</style>
""", unsafe_allow_html=True)

# ─── DB HELPERS ──────────────────────────────────────────────────────────────

@st.cache_resource
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="route",
            database="vehicle_db"
        )
        return conn
    except Error as e:
        return None


def ensure_tables(conn):
    """Create tables if they don't exist."""
    try:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS vehicle_info (
                registration VARCHAR(20) PRIMARY KEY,
                owner_name   VARCHAR(100),
                house_name   VARCHAR(100),
                place        VARCHAR(100),
                phone        VARCHAR(15)
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS detections (
                id           INT AUTO_INCREMENT PRIMARY KEY,
                plate_number VARCHAR(20),
                confidence   FLOAT,
                owner_found  BOOLEAN,
                detected_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        c.close()
    except:
        pass


def lookup_owner(conn, plate: str):
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM vehicle_info WHERE registration = %s", (plate,))
        row = c.fetchone()
        c.close()
        return row
    except:
        return None


def log_detection(conn, plate: str, conf: float, found: bool):
    try:
        c = conn.cursor()
        c.execute(
            "INSERT INTO detections (plate_number, confidence, owner_found) VALUES (%s,%s,%s)",
            (plate, round(float(conf), 4), found)
        )
        conn.commit()
        c.close()
    except:
        pass


def fetch_logs(conn, limit=15):
    try:
        df = pd.read_sql("""
            SELECT d.plate_number, d.confidence,
                   d.owner_found, v.owner_name,
                   d.detected_at
            FROM detections d
            LEFT JOIN vehicle_info v ON d.plate_number = v.registration
            ORDER BY d.detected_at DESC
            LIMIT %s
        """, conn, params=(limit,))
        return df
    except:
        return pd.DataFrame()


# ─── MODEL / OCR LOADERS ─────────────────────────────────────────────────────

@st.cache_resource
def load_model():
    return YOLO("best.pt")


@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'], gpu=False)


# ─── PREPROCESSING ───────────────────────────────────────────────────────────

def preprocess(plate_img):
    plate_img = cv2.resize(plate_img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    gray  = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
    blur  = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    return plate_img, gray, blur, thresh


def clean_text(raw: str) -> str:
    return re.sub('[^A-Z0-9]', '', raw.upper())


def run_detection(image_bgr, model, reader, conn):
    """Run full pipeline and return (annotated_image, list of result dicts)."""
    results_yolo = model(image_bgr)
    all_results  = []
    annotated    = image_bgr.copy()

    for r in results_yolo:
        for box in r.boxes.xyxy:
            x1, y1, x2, y2 = map(int, box)
            plate_crop = image_bgr[y1:y2, x1:x2]
            if plate_crop.size == 0:
                continue

            resized, gray, blur, thresh = preprocess(plate_crop)
            ocr_out = reader.readtext(thresh)

            best_text, best_conf, raw_text = "", 0.0, ""
            for det in ocr_out:
                raw   = det[1]
                conf  = det[2]
                clean = clean_text(raw)
                if conf > best_conf and len(clean) >= 3:
                    best_text = clean
                    best_conf = conf
                    raw_text  = raw

            owner = lookup_owner(conn, best_text) if best_text else None
            found = owner is not None
            log_detection(conn, best_text, best_conf, found)

            color = (0, 230, 118) if found else (255, 68, 68)
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 3)
            label = f'{best_text}  {"" if found else ""}'
            cv2.putText(annotated, label, (x1, max(y1 - 10, 15)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

            all_results.append({
                "plate"     : best_text,
                "raw"       : raw_text,
                "conf"      : best_conf,
                "owner"     : owner,
                "found"     : found,
                "crop"      : resized,
                "gray"      : gray,
                "thresh"    : thresh,
                "box"       : (x1, y1, x2, y2),
            })

    return annotated, all_results


# ─── SIDEBAR ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1rem 0 0.5rem;'>
        <div style='font-size:2.2rem;filter:drop-shadow(0 0 10px #00d4ff)'>🚗</div>
        <div style='font-family:Rajdhani,sans-serif;font-size:1.1rem;font-weight:700;
                    letter-spacing:3px;text-transform:uppercase;color:#00d4ff;margin-top:4px;'>
            VehicleID
        </div>
        <div style='font-size:0.68rem;color:#4a5568;letter-spacing:2px;text-transform:uppercase;'>
            AI Recognition System
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown('<div class="sidebar-section">⚙ Database</div>', unsafe_allow_html=True)
    db_conn = get_db_connection()
    if db_conn and db_conn.is_connected():
        st.markdown("""
        <div style='display:flex;align-items:center;gap:8px;
                    background:rgba(0,230,118,0.07);border:1px solid rgba(0,230,118,0.2);
                    border-radius:6px;padding:8px 12px;font-size:0.8rem;color:#00e676;'>
            <span style='font-size:0.6rem;'>●</span> MySQL Connected
        </div>""", unsafe_allow_html=True)
        ensure_tables(db_conn)
    else:
        st.markdown("""
        <div style='display:flex;align-items:center;gap:8px;
                    background:rgba(255,68,68,0.07);border:1px solid rgba(255,68,68,0.2);
                    border-radius:6px;padding:8px 12px;font-size:0.8rem;color:#ff4444;'>
            <span style='font-size:0.6rem;'>●</span> DB Not Connected
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">🔧 Settings</div>', unsafe_allow_html=True)
    show_preprocess = st.toggle("Show preprocessing stages", value=False)
    show_logs       = st.toggle("Show detection log",        value=True)
    conf_threshold  = st.slider("Min OCR confidence", 0.0, 1.0, 0.3, 0.05)

    st.markdown('<div class="sidebar-section">🔍 Manual Lookup</div>', unsafe_allow_html=True)
    manual_plate = st.text_input("", placeholder="e.g. KL07CA1234",
                                 label_visibility="collapsed")
    if st.button("LOOKUP", use_container_width=True):
        if db_conn and manual_plate:
            owner = lookup_owner(db_conn, clean_text(manual_plate))
            if owner:
                st.markdown(f"""
                <div style='margin-top:0.6rem;background:rgba(0,230,118,0.05);
                            border:1px solid rgba(0,230,118,0.2);border-radius:8px;
                            padding:0.8rem;'>
                    <div style='color:#00e676;font-weight:700;font-size:0.9rem;
                                font-family:Rajdhani,sans-serif;letter-spacing:1px;'>
                        ✅ {owner[1]}
                    </div>
                    <div style='color:#8892a4;font-size:0.75rem;margin-top:6px;line-height:1.8;'>
                        🏠 {owner[2]}<br>
                        📍 {owner[3]}<br>
                        📞 {owner[4]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style='margin-top:0.6rem;background:rgba(255,68,68,0.05);
                            border:1px solid rgba(255,68,68,0.2);border-radius:6px;
                            padding:0.7rem;color:#ff4444;font-size:0.8rem;text-align:center;'>
                    ❌ No record found
                </div>""", unsafe_allow_html=True)


# ─── MAIN CONTENT ─────────────────────────────────────────────────────────────

# Top banner
st.markdown("""
<div class="top-banner">
    <div class="banner-icon">🎯</div>
    <div>
        <div class="banner-title">Vehicle Identification System</div>
        <div class="banner-sub">AI-Powered Number Plate Recognition & Owner Retrieval</div>
    </div>
    <div class="banner-badge">YOLOv8 + EasyOCR</div>
</div>
""", unsafe_allow_html=True)

# ── Tab layout ──
tab1, tab2 = st.tabs(["  🔍  DETECTION  ", "  📋  DATABASE  "])

# ═══════════════════════════════════════════════════════════
# TAB 1 — Detection
# ═══════════════════════════════════════════════════════════
with tab1:
    col_upload, col_results = st.columns([1, 1.3], gap="large")

    with col_upload:
        st.markdown('<div class="card-title">📁 Input Image</div>', unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Upload vehicle image",
            type=["jpg", "jpeg", "png", "bmp", "webp"],
            label_visibility="collapsed"
        )

        if uploaded:
            file_bytes = np.frombuffer(uploaded.read(), np.uint8)
            img_bgr    = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            img_rgb    = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

            st.image(img_rgb, caption="Uploaded Image", use_container_width=True)
            st.markdown(f"""
            <div style='display:flex;gap:1rem;margin-top:0.5rem;'>
                <div class="metric-box" style='flex:1'>
                    <div class="metric-val" style='font-size:1.1rem;'>{img_bgr.shape[1]}×{img_bgr.shape[0]}</div>
                    <div class="metric-lbl">Resolution</div>
                </div>
                <div class="metric-box" style='flex:1'>
                    <div class="metric-val" style='font-size:1.1rem;'>{uploaded.size // 1024} KB</div>
                    <div class="metric-lbl">File Size</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            run_btn = st.button("⚡  RUN DETECTION", use_container_width=True)
        else:
            st.markdown("""
            <div style='text-align:center;padding:3rem 1rem;color:#4a5568;'>
                <div style='font-size:2.5rem;margin-bottom:0.8rem;'>📸</div>
                <div style='font-family:Rajdhani,sans-serif;font-size:1rem;letter-spacing:2px;
                            text-transform:uppercase;'>Upload an image to begin</div>
                <div style='font-size:0.75rem;margin-top:0.4rem;'>Supports JPG, PNG, BMP, WebP</div>
            </div>
            """, unsafe_allow_html=True)
            run_btn = False

    with col_results:
        st.markdown('<div class="card-title">🎯 Detection Results</div>', unsafe_allow_html=True)

        if uploaded and run_btn:
            if not db_conn or not db_conn.is_connected():
                st.error("⚠️ MySQL not connected. Check sidebar.")
            else:
                with st.spinner("Running AI pipeline..."):
                    t0    = time.time()
                    model  = load_model()
                    reader = load_reader()
                    annotated_bgr, detections = run_detection(img_bgr, model, reader, db_conn)
                    elapsed = time.time() - t0

                annotated_rgb = cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)
                st.image(annotated_rgb, caption="Annotated Output", use_container_width=True)

                found_count = sum(1 for d in detections if d["found"])
                st.markdown(f"""
                <div class="metric-row">
                    <div class="metric-box">
                        <div class="metric-val">{len(detections)}</div>
                        <div class="metric-lbl">Plates Found</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-val" style='color:#00e676'>{found_count}</div>
                        <div class="metric-lbl">Owner Matched</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-val">{elapsed:.1f}s</div>
                        <div class="metric-lbl">Process Time</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if detections:
                    st.markdown("---")
                    for i, det in enumerate(detections):
                        if det["conf"] < conf_threshold:
                            continue

                        st.markdown(f'<div class="card-title">PLATE {i+1} DETAILS</div>',
                                    unsafe_allow_html=True)

                        c1, c2 = st.columns([1, 1.5])
                        with c1:
                            st.image(cv2.cvtColor(det["crop"], cv2.COLOR_BGR2RGB),
                                     caption="Cropped & Resized", use_container_width=True)
                            if show_preprocess:
                                st.image(det["thresh"], caption="Thresholded",
                                         use_container_width=True, clamp=True)

                        with c2:
                            conf_pct = int(det["conf"] * 100)
                            st.markdown(f"""
                            <div class="plate-display">{det['plate'] or '—'}</div>
                            <div style='margin-bottom:0.6rem;'>
                                <div style='display:flex;justify-content:space-between;
                                            font-size:0.7rem;color:#8892a4;margin-bottom:3px;'>
                                    <span>OCR CONFIDENCE</span>
                                    <span style='font-family:JetBrains Mono,monospace;
                                                 color:#00d4ff;'>{conf_pct}%</span>
                                </div>
                                <div class="conf-bar-wrap">
                                    <div class="conf-bar-fill" style='width:{conf_pct}%'></div>
                                </div>
                            </div>
                            <div style='margin-bottom:0.8rem;'>
                                <div class="owner-label">Raw OCR Output</div>
                                <span class="raw-ocr">{det['raw'] or 'N/A'}</span>
                            </div>
                            """, unsafe_allow_html=True)

                            if det["found"]:
                                o = det["owner"]
                                st.markdown(f"""
                                <div class="owner-found">
                                    <div style='margin-bottom:0.6rem;'>
                                        <span class="badge-found">● OWNER FOUND</span>
                                    </div>
                                    <div class="owner-name-big">{o[1]}</div>
                                    <div style='display:grid;grid-template-columns:1fr 1fr;gap:0.6rem;'>
                                        <div>
                                            <div class="owner-label">🏠 House Name</div>
                                            <div class="owner-value">{o[2]}</div>
                                        </div>
                                        <div>
                                            <div class="owner-label">📍 Place</div>
                                            <div class="owner-value">{o[3]}</div>
                                        </div>
                                        <div>
                                            <div class="owner-label">📞 Phone</div>
                                            <div class="owner-value">{o[4]}</div>
                                        </div>
                                        <div>
                                            <div class="owner-label">🔢 Registration</div>
                                            <div class="owner-value"
                                                 style='font-family:JetBrains Mono,monospace;
                                                        color:#00d4ff;'>{o[0]}</div>
                                        </div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown("""
                                <div class="owner-not-found">
                                    <span class="badge-not-found">● NOT IN DATABASE</span>
                                    <div style='color:#8892a4;font-size:0.8rem;margin-top:0.5rem;'>
                                        No matching owner record found for this plate number.
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)

                else:
                    st.markdown("""
                    <div style='text-align:center;padding:2rem;color:#4a5568;'>
                        <div style='font-size:2rem;'>🔍</div>
                        <div style='font-family:Rajdhani,sans-serif;letter-spacing:2px;
                                    text-transform:uppercase;font-size:0.9rem;margin-top:0.5rem;'>
                            No plates detected
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        else:
            st.markdown("""
            <div style='text-align:center;padding:4rem 1rem;color:#4a5568;'>
                <div style='font-size:2.5rem;margin-bottom:0.8rem;'>⚡</div>
                <div style='font-family:Rajdhani,sans-serif;font-size:1rem;letter-spacing:2px;
                            text-transform:uppercase;'>Upload image and click Run Detection</div>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════
# TAB 2 — Database
# ═══════════════════════════════════════════════════════════
with tab2:
    col_a, col_b = st.columns([1.5, 1], gap="large")

    with col_a:
        st.markdown('<div class="card-title">📋 Detection Log</div>', unsafe_allow_html=True)
        if db_conn and db_conn.is_connected() and show_logs:
            logs = fetch_logs(db_conn, 20)
            if not logs.empty:
                logs["owner_found"] = logs["owner_found"].map(
                    {1: "✅ Found", 0: "❌ Not Found", True: "✅ Found", False: "❌ Not Found"}
                )
                logs["confidence"] = logs["confidence"].apply(
                    lambda x: f"{int(x*100)}%" if pd.notna(x) else "—"
                )
                logs.columns = ["Plate", "Confidence", "Status", "Owner", "Detected At"]
                st.dataframe(logs, use_container_width=True, hide_index=True)
            else:
                st.markdown("""
                <div style='text-align:center;padding:2rem;color:#4a5568;font-size:0.85rem;'>
                    No detections logged yet. Run detection first.
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='text-align:center;padding:2rem;color:#4a5568;font-size:0.85rem;'>
                Enable "Show detection log" in sidebar to view logs.
            </div>""", unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="card-title">👤 Owner Records</div>', unsafe_allow_html=True)
        if db_conn and db_conn.is_connected():
            try:
                df_owners = pd.read_sql("SELECT * FROM vehicle_info LIMIT 50", db_conn)
                if not df_owners.empty:
                    st.dataframe(df_owners, use_container_width=True, hide_index=True)
                else:
                    st.markdown("""
                    <div style='text-align:center;padding:1.5rem;color:#4a5568;font-size:0.82rem;'>
                        No owner records in database.<br>
                        <span style='font-family:JetBrains Mono,monospace;font-size:0.75rem;
                                     color:#2a3550;'>INSERT INTO vehicle_info ...</span>
                    </div>""", unsafe_allow_html=True)
            except:
                st.warning("Could not fetch owner records.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="card-title">➕ Add Owner Record</div>',
                    unsafe_allow_html=True)

        with st.form("add_owner_form", clear_on_submit=True):
            f1, f2 = st.columns(2)
            reg   = f1.text_input("Registration No.", placeholder="KL07CA1234")
            name  = f2.text_input("Owner Name",       placeholder="Rahul Menon")
            house = f1.text_input("House Name",        placeholder="Sreyas")
            place = f2.text_input("Place",             placeholder="Kochi, Kerala")
            phone = st.text_input("Phone",             placeholder="+91-9876543210")
            submitted = st.form_submit_button("ADD RECORD", use_container_width=True)

            if submitted:
                if reg and name:
                    try:
                        c = db_conn.cursor()
                        c.execute("""
                            INSERT IGNORE INTO vehicle_info
                                (registration, owner_name, house_name, place, phone)
                            VALUES (%s,%s,%s,%s,%s)
                        """, (clean_text(reg), name, house, place, phone))
                        db_conn.commit()
                        c.close()
                        st.success(f"✅ Record added for {clean_text(reg)}")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Registration and Owner Name are required.")