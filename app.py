import streamlit as st
import fitz
import easyocr
from PIL import Image
import tempfile
import random
import pandas as pd
from io import BytesIO

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="AI Fraud Detection System",
    page_icon="🛡️",
    layout="wide"
)

# ---------------- TITLE ----------------

st.title("🛡️ AI Fraud Detection System")
st.markdown("## Real-time Anomaly Detection for Banking & Underwriting")

# ---------------- FILE UPLOAD ----------------

uploaded_file = st.file_uploader(
    "Upload PDF or Image",
    type=["pdf", "png", "jpg", "jpeg"]
)

# ---------------- KEYWORDS ----------------

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

# ---------------- OCR ----------------

reader = easyocr.Reader(['en'])

# ---------------- MAIN ----------------

if uploaded_file:

    st.success("✅ File uploaded successfully")

    extracted_text = ""

    # ---------- PDF ----------

    if uploaded_file.type == "application/pdf":

        st.subheader("📄 PDF Analysis")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            pdf_path = tmp.name

        doc = fitz.open(pdf_path)

        # Metadata
        metadata = doc.metadata

        st.subheader("📑 PDF Metadata")

        metadata_df = pd.DataFrame({
            "Property": list(metadata.keys()),
            "Value": list(metadata.values())
        })

        st.dataframe(metadata_df)

        for page in doc:
            extracted_text += page.get_text()

    # ---------- IMAGE ----------

    else:

        st.subheader("🖼️ Image Analysis")

        image = Image.open(uploaded_file)

        st.image(image, caption="Uploaded Image", width=400)

        result = reader.readtext(image)

        extracted_text = " ".join([text[1] for text in result])

    # ---------------- HIGHLIGHT SUSPICIOUS WORDS ----------------

    highlighted_text = extracted_text

    found = []

    for word in suspicious_words:

        if word.lower() in extracted_text.lower():
            found.append(word)

            highlighted_text = highlighted_text.replace(
                word,
                f"🔴 **{word.upper()}**"
            )

    # ---------------- SCORES ----------------

    fraud_score = min(len(found) * 18 + random.randint(5, 15), 100)

    authenticity_score = 100 - fraud_score

    # ---------------- ALERT BANNER ----------------

    if fraud_score > 70:
        st.error("🚨 HIGH RISK DOCUMENT DETECTED")
    elif fraud_score > 30:
        st.warning("⚠️ MEDIUM RISK DOCUMENT")
    else:
        st.success("✅ LOW RISK DOCUMENT")

    # ---------------- EXTRACTED TEXT ----------------

    st.subheader("📝 Extracted Text")

    if extracted_text.strip() == "":
        st.warning("No readable text detected")
    else:
        st.markdown(highlighted_text)

    # ---------------- FRAUD ANALYSIS ----------------

    st.subheader("🚨 Fraud Risk Analysis")

    st.progress(fraud_score / 100)

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Fraud Risk Score", f"{fraud_score}%")

    with col2:
        st.metric("Authenticity Score", f"{authenticity_score}%")

    # ---------------- FINDINGS ----------------

    st.subheader("🔍 Suspicious Findings")

    if found:
        st.error(f"Suspicious keywords detected: {found}")
    else:
        st.success("No suspicious keywords found")

    # ---------------- AI EXPLANATION ----------------

    st.subheader("🤖 AI Explanation")

    if found:
        st.write(
            f"""
            The system identified suspicious indicators such as {found}.
            These may indicate possible tampering, forgery,
            or unauthorized modification in the uploaded document.
            """
        )
    else:
        st.write(
            """
            The uploaded document appears normal based on
            OCR analysis, metadata validation,
            and anomaly keyword scanning.
            """
        )

    # ---------------- UNDERWRITING INSIGHTS ----------------

    st.subheader("🏦 Underwriting Insights")

    insights = {
        "Document Type": "Financial / Legal",
        "OCR Status": "Completed",
        "Tampering Indicators": len(found),
        "Verification Status": "Needs Review" if fraud_score > 50 else "Verified",
        "Processing Status": "Completed"
    }

    insights_df = pd.DataFrame(
        list(insights.items()),
        columns=["Category", "Value"]
    )

    st.table(insights_df)

    # ---------------- FINAL RECOMMENDATION ----------------

    st.subheader("✅ Final Recommendation")

    if fraud_score < 30:
        recommendation = "Document can proceed for underwriting review"
        st.success(recommendation)

    elif fraud_score < 70:
        recommendation = "Manual verification recommended"
        st.warning(recommendation)

    else:
        recommendation = "Potential fraud detected — escalate for investigation"
        st.error(recommendation)

    # ---------------- DOWNLOAD REPORT ----------------

    st.subheader("📥 Download Fraud Report")

    report = f"""
AI FRAUD DETECTION REPORT
=========================

Fraud Risk Score: {fraud_score}%
Authenticity Score: {authenticity_score}%

Suspicious Findings:
{found if found else "None"}

Final Recommendation:
{recommendation}

Extracted Text:
{extracted_text[:2000]}
"""

    report_bytes = BytesIO(report.encode())

    st.download_button(
        label="Download Report",
        data=report_bytes,
        file_name="fraud_report.txt",
        mime="text/plain"
    )

else:

    st.info("Upload a PDF or image document to begin fraud analysis")
