import streamlit as st
import fitz
import easyocr
from PIL import Image
import tempfile
import pandas as pd
from difflib import SequenceMatcher

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="AI Fraud Detection System",
    page_icon="🛡️",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        #0f172a,
        #111827,
        #1e293b
    );
    color: white;
}

h1 {
    color: white;
    font-size: 3.5rem !important;
    font-weight: 800;
    text-align: center;
}

h2, h3 {
    color: #38bdf8;
}

section[data-testid="stSidebar"] {
    background: #111827;
}

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
}

[data-testid="stFileUploader"] {
    background-color: #111827;
    padding: 20px;
    border-radius: 20px;
    border: 2px dashed #38bdf8;
}

.login-box {
    background: rgba(17,24,39,0.9);
    padding: 50px;
    border-radius: 25px;
    margin-top: 60px;
}

footer {
    visibility: hidden;
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN ----------------

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

            st.error("Invalid Credentials")

    st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# ---------------- TITLE ----------------

st.title("🛡️ AI Fraud Detection Dashboard")
st.markdown("### Real-time Banking & Underwriting Intelligence")

# ---------------- SIDEBAR ----------------

st.sidebar.title("🏦 Dashboard")

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
    "suspicious",
    "unauthorized"
]

# ---------------- ANALYZE FUNCTION ----------------

def analyze_document(uploaded_file):

    extracted_text = ""

    # PDF FILE

    if uploaded_file.type == "application/pdf":

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:

            tmp.write(uploaded_file.read())
            pdf_path = tmp.name

        doc = fitz.open(pdf_path)

        metadata = doc.metadata

        for page in doc:

            extracted_text += page.get_text()

    # IMAGE FILE

    else:

        image = Image.open(uploaded_file)

        result = reader.readtext(image)

        extracted_text = " ".join([text[1] for text in result])

        metadata = {
            "type": "Image File"
        }

    # ---------------- FRAUD DETECTION ----------------

    found = []
    reasons = []

    highlighted_text = extracted_text

    fraud_score = 0

    for word in suspicious_words:

        if word.lower() in extracted_text.lower():

            found.append(word)

            fraud_score += 20

            reasons.append(f"Suspicious keyword found: {word}")

            highlighted_text = highlighted_text.replace(
                word,
                f"🔴 {word.upper()}"
            )

    # METADATA CHECKS

    if metadata.get("producer"):

        if "photoshop" in str(metadata.get("producer")).lower():

            fraud_score += 30

            reasons.append("Edited using Photoshop")

    if metadata.get("creator"):

        if "canva" in str(metadata.get("creator")).lower():

            fraud_score += 20

            reasons.append("Created using Canva")

    # FINAL SCORES

    fraud_score = min(fraud_score, 100)

    authenticity_score = 100 - fraud_score

    return {
        "text": extracted_text,
        "highlighted_text": highlighted_text,
        "metadata": metadata,
        "fraud_score": fraud_score,
        "authenticity_score": authenticity_score,
        "findings": found,
        "reasons": reasons
    }

# ---------------- SINGLE DOCUMENT ----------------

if page == "Single Document Analysis":

    st.subheader("📄 Upload Certificate or Document")

    uploaded_file = st.file_uploader(
        "Upload PDF or Image",
        type=["pdf", "png", "jpg", "jpeg"]
    )

    if uploaded_file:

        result = analyze_document(uploaded_file)

        # ALERTS

        if result["fraud_score"] >= 50:

            st.error("❌ Possible Forged Certificate Detected")

        elif result["fraud_score"] >= 20:

            st.warning("⚠ Suspicious Certificate")

        else:

            st.success("✅ Certificate Appears Genuine")

        # METRICS

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Fraud Score",
                f"{result['fraud_score']}%"
            )

        with col2:

            st.metric(
                "Authenticity",
                f"{result['authenticity_score']}%"
            )

        with col3:

            st.metric(
                "Indicators Found",
                len(result["findings"])
            )

        # PROGRESS

        st.progress(result["fraud_score"] / 100)

        # TABS

        tab1, tab2, tab3 = st.tabs([
            "📝 Extracted Text",
            "📑 Metadata",
            "🤖 AI Analysis"
        ])

        # TEXT

        with tab1:

            st.markdown(result["highlighted_text"])

        # METADATA

        with tab2:

            metadata_df = pd.DataFrame({
                "Property": list(result["metadata"].keys()),
                "Value": [str(v) for v in result["metadata"].values()]
            })

            st.dataframe(metadata_df)

        # AI ANALYSIS

        with tab3:

            st.subheader("🛡 Certificate Verification")

            if result["fraud_score"] >= 50:

                st.error("Forgery Indicators Detected")

            elif result["fraud_score"] >= 20:

                st.warning("Document Appears Suspicious")

            else:

                st.success("Document Appears Genuine")

            # REASONS

            if result["reasons"]:

                st.subheader("🔍 Detection Reasons")

                for reason in result["reasons"]:

                    st.write("•", reason)

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

        # DOCUMENT 1

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

        # DOCUMENT 2

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

        # ---------------- COMPARISON ----------------

        st.subheader("🔍 Text Difference Analysis")

        similarity = SequenceMatcher(
            None,
            result1["text"],
            result2["text"]
        ).ratio()

        similarity_percent = int(similarity * 100)

        st.metric(
            "Document Similarity",
            f"{similarity_percent}%"
        )

        if similarity_percent > 90:

            st.success("✅ Documents are Highly Similar")

        elif similarity_percent > 60:

            st.warning("⚠ Partial Differences Detected")

        else:

            st.error("❌ Documents are Very Different")

        # DOCUMENT TEXTS

        st.subheader("📝 Document 1 Text")
        st.write(result1["text"][:3000])

        st.subheader("📝 Document 2 Text")
        st.write(result2["text"][:3000])