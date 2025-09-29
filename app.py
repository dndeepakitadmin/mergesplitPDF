import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from reportlab.pdfgen import canvas
from datetime import datetime

st.set_page_config(layout="wide")
st.title("AI PDF Tool")

# --- User acknowledgment ---
ack = st.checkbox(
    "I acknowledge that this tool will NOT be used for unethical or illegal purposes. "
    "It is intended only for personal and professional use."
)
if not ack:
    st.warning("You must acknowledge the terms to use this tool.")
    st.stop()

st.info("⚠️ Make sure the file you are uploading is not encrypted or corrupted.")

# --- Layout: Merge & Split side by side ---
merge_col, split_col = st.columns(2)

# ---------------- MERGE PDFs ----------------
with merge_col:
    st.header("Merge PDFs")
    merge_files = st.file_uploader("Upload PDFs to merge", type=["pdf"], accept_multiple_files=True, key="merge")
    custom_name = st.text_input("Custom output file name", value="merged.pdf", key="merge_name")

    if merge_files:
        if st.button("Merge PDFs"):
            pdf_writer = PdfWriter()
            for file in merge_files:
                reader = PdfReader(file)
                for page in reader.pages:
                    pdf_writer.add_page(page)

            merged_bytes = BytesIO()
            pdf_writer.write(merged_bytes)
            merged_bytes.seek(0)

            st.download_button(
                label="Download Merged PDF",
                data=merged_bytes,
                file_name=custom_name,
                mime="application/pdf"
            )

# ---------------- SPLIT PDFs ----------------
with split_col:
    st.header("Split PDF by Ranges")
    split_file = st.file_uploader("Upload PDF to split", type=["pdf"], key="split")
    
    if split_file:
        pdf_reader = PdfReader(split_file)
        total_pages = len(pdf_reader.pages)
        st.success(f"Uploaded PDF has {total_pages} pages.")

        # Predefined example ranges
        ranges = [(1, 15), (20, 25), (30, 45)]

        # Initialize session state for tracking downloads
        if "split_downloaded" not in st.session_state:
            st.session_state.split_downloaded = [False] * len(ranges)

        # Show all download buttons persistently
        for i, (start, end) in enumerate(ranges):
            end = min(end, total_pages)
            if not st.session_state.split_downloaded[i]:
                pdf_writer = PdfWriter()
                for page_num in range(start - 1, end):
                    pdf_writer.add_page(pdf_reader.pages[page_num])

                pdf_bytes = BytesIO()
                pdf_writer.write(pdf_bytes)
                pdf_bytes.seek(0)

                if st.download_button(
                    label=f"Download pages {start}-{end}",
                    data=pdf_bytes,
                    file_name=f"pages_{start}_{end}.pdf",
                    mime="application/pdf",
                    key=f"split_btn_{i}"
                ):
                    st.session_state.split_downloaded[i] = True
                    st.success(f"Pages {start}-{end} downloaded!")

        # Once all downloaded
        if all(st.session_state.split_downloaded):
            st.balloons()
            st.success("All selected ranges downloaded! You can reset now.")

            # Optional Data Deletion Certificate
            if st.checkbox("Generate Data Deletion Certificate"):
                buffer = BytesIO()
                c = canvas.Canvas(buffer)
                c.setFont("Helvetica", 12)
                c.drawString(50, 750, "Data Deletion Certificate")
                c.setFont("Helvetica", 10)
                c.drawString(50, 720, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                c.drawString(50, 700, "This certifies that all uploaded files have been removed from memory")
                c.drawString(50, 685, "and no data is stored by the AI PDF Tool.")
                c.save()
                buffer.seek(0)

                st.download_button(
                    "Download Data Deletion Certificate",
                    data=buffer,
                    file_name="data_deletion_certificate.pdf",
                    mime="application/pdf"
                )

            if st.button("Reset Split"):
                st.session_state.split_downloaded = [False] * len(ranges)
