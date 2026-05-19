import streamlit as st
import fitz
import easyocr
from PIL import Image
import tempfile
import random
import pandas as pd

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="AI Fraud Detection System",
    page_icon="🛡️",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>

/* Main Background */

.stApp {
    background: linear-gradient(
        135deg,
        #0f172a,
        #111827,
        #1e293b
    );
    color: white;
}

/* Main Container */

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Headings */

h1 {
    color: #ffffff;
    font-size: 3.5rem !important;
    font-weight: 800;
    text-align: center;
}

h2, h3 {
    color: #38bdf8;
    font-weight: 700;
}

/* Sidebar */

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #111827,
        #0f172a
    );
    border-right: 1px solid #334155;
}

/* Buttons */

.stButton > button {
    width: 100%;
    border-radius: 15px;
    height: 3.2em;
    border: none;
    background: linear-gradient(
        90deg,
        #06b6d4,
        #3b82f6
    );
    color: white;
    font-size: 18px;
    font-weight: 700;
    transition: 0.3s;
    box-shadow: 0px 0px 15px rgba(59,130,246,0.5);
}

.stButton > button:hover {
    transform: scale(1.03);
    background: linear-gradient(
        90deg,
        #3b82f6,
        #06b6d4
    );
}

/* Login Box */

.login-box {
    background: rgba(17, 24, 39, 0.9);
    padding: 50px;
    border-radius: 25px;
    margin-top: 80px;
    box-shadow: 0px 0px 30px rgba(0,0,0,0.5);
    border: 1px solid #334155;
}

/* Cards */

.metric-card {
    background: linear-gradient(
        145deg,
        #1e293b,
        #0f172a
    );
    padding: 25px;
    border-radius: 20px;
    text-align: center;
    color: white;
    border: 1px solid #334155;
    box-shadow: 0px 0px 20px rgba(0,0,0,0.4);
}

/* Input Boxes */

.stTextInput > div > div > input {
    background-color: #1e293b;
    color: white;
    border-radius: 12px;
    border: 1px solid #475569;
}

/* Upload Box */

[data-testid="stFileUploader"] {
    background-color: #111827;
    padding: 20px;
    border-radius: 20px;
    border: 2px dashed #38bdf8;
}

/* Tabs */

button[data-baseweb="tab"] {
    background-color: #1e293b;
    color: white;
    border-radius: 10px;
    margin-right: 10px;
    padding: 10px 20px;
}

/* Progress Bar */

.stProgress > div > div > div > div {
    background: linear-gradient(
        90deg,
        #06b6d4,
        #3b82f6
    );
}

/* Tables */

[data-testid="stDataFrame"] {
    border-radius: 15px;
    overflow: hidden;
    border: 1px solid #334155;
}

/* Alerts */

.stAlert {
    border-radius: 15px;
}

/* Footer Hide */

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN SYSTEM ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.markdown("<div class='login-box'>", unsafe_allow_html=True)

    st.title("🔐 Secure Banking Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.rerun()

        else:
            st.error("Invalid credentials")

    st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# ---------------- MAIN TITLE ----------------

st.title("🛡️ AI Fraud Detection Dashboard")
st.markdown("### Real-time Banking & Underwriting Intelligence")

# ---------------- SIDEBAR ----------------

st.sidebar.title("🏦 Banking Dashboard")

page = st.sidebar.radio(
    "Navigation",
    [
        "Single Document Analysis",
        "Compare Two Documents"
    ]
)

# ---------------- OCR ----------------

reader = easyocr.Reader(['en'])

suspicious_words = [
    "edited",
    "fake",
    "forged",
    "tampered",
    "duplicate",
    "modified",
    "invalid",
    "suspicious"
]

# ---------------- FUNCTION ----------------

def analyze_document(uploaded_file):

    extracted_text = ""

    if uploaded_file.type == "application/pdf":

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            pdf_path = tmp.name

        doc = fitz.open(pdf_path)

        metadata = doc.metadata

        for page in doc:
            extracted_text += page.get_text()

    else:

        image = Image.open(uploaded_file)

        result = reader.readtext(image)

        extracted_text = " ".join([text[1] for text in result])

        metadata = {
            "type": "Image File"
        }

    found = []

    highlighted_text = extracted_text

    for word in suspicious_words:

        if word.lower() in extracted_text.lower():

            found.append(word)

            highlighted_text = highlighted_text.replace(
                word,
                f"🔴 {word.upper()}"
            )

    fraud_score = min(len(found) * 20 + random.randint(5, 15), 100)

    authenticity_score = 100 - fraud_score

    return {
        "text": extracted_text,
        "highlighted_text": highlighted_text,
        "metadata": metadata,
        "fraud_score": fraud_score,
        "authenticity_score": authenticity_score,
        "findings": found
    }

# ---------------- SINGLE ANALYSIS ----------------

if page == "Single Document Analysis":

    st.subheader("📄 Upload Document")

    uploaded_file = st.file_uploader(
        "Upload PDF or Image",
        type=["pdf", "png", "jpg", "jpeg"]
    )

    if uploaded_file:

        result = analyze_document(uploaded_file)

        # ALERT

        if result["fraud_score"] > 70:
            st.error("🚨 HIGH RISK DOCUMENT DETECTED")
        elif result["fraud_score"] > 30:
            st.warning("⚠️ MEDIUM RISK DOCUMENT")
        else:
            st.success("✅ LOW RISK DOCUMENT")

        # METRICS

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Fraud Score", f"{result['fraud_score']}%")

        with col2:
            st.metric("Authenticity", f"{result['authenticity_score']}%")

        with col3:
            st.metric("Suspicious Indicators", len(result["findings"]))

        # PROGRESS

        st.progress(result["fraud_score"] / 100)

        # TABS

        tab1, tab2, tab3 = st.tabs([
            "📝 Extracted Text",
            "📑 Metadata",
            "🤖 AI Analysis"
        ])

        with tab1:
            st.markdown(result["highlighted_text"])

        with tab2:

            metadata_df = pd.DataFrame({
                "Property": list(result["metadata"].keys()),
                "Value": list(result["metadata"].values())
            })

            st.dataframe(metadata_df)

        with tab3:

            if result["findings"]:

                st.error(
                    f"Suspicious keywords detected: {result['findings']}"
                )

            else:

                st.success("No suspicious indicators found")

# ---------------- COMPARE DOCUMENTS ----------------

if page == "Compare Two Documents":

    st.subheader("📂 Compare Two Documents")

    col1, col2 = st.columns(2)

    with col1:
        file1 = st.file_uploader(
            "Upload First Document",
            type=["pdf", "png", "jpg", "jpeg"],
            key="file1"
        )

    with col2:
        file2 = st.file_uploader(
            "Upload Second Document",
            type=["pdf", "png", "jpg", "jpeg"],
            key="file2"
        )

    if file1 and file2:

        result1 = analyze_document(file1)
        result2 = analyze_document(file2)

        st.subheader("📊 Comparison Dashboard")

        c1, c2 = st.columns(2)

        with c1:

            st.markdown("## Document 1")

            st.metric(
                "Fraud Score",
                f"{result1['fraud_score']}%"
            )

            st.metric(
                "Authenticity",
                f"{result1['authenticity_score']}%"
            )

            st.write("### Findings")
            st.write(result1["findings"])

        with c2:

            st.markdown("## Document 2")

            st.metric(
                "Fraud Score",
                f"{result2['fraud_score']}%"
            )

            st.metric(
                "Authenticity",
                f"{result2['authenticity_score']}%"
            )

            st.write("### Findings")
            st.write(result2["findings"])

        # DIFFERENCE CHECK

        st.subheader("🔍 Text Difference Analysis")

        if result1["text"] == result2["text"]:
            st.success("Documents appear identical")
        else:
            st.warning("Differences detected between documents")

        st.subheader("📝 Document 1 Text")
        st.write(result1["text"][:3000])

        st.subheader("📝 Document 2 Text")
        st.write(result2["text"][:3000])
