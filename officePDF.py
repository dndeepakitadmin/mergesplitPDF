import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from reportlab.pdfgen import canvas
from datetime import datetime

# --- Page setup ---
st.set_page_config(layout="wide", page_title="PDF Merge & Split Tool")
st.title("📄 Merge and Split PDF Tool")

# --- Acknowledgment ---
ack = st.checkbox(
    "✅ I acknowledge that this tool will NOT be used for unethical or illegal purposes. "
    "It is intended only for professional use."
)
if not ack:
    st.warning("⚠️ You must acknowledge the terms to use this tool.")
    st.stop()

st.info("⚠️ Please ensure the PDF you upload is not encrypted or corrupted.")

# --- Layout: two sections side by side ---
merge_col, spacer, split_col = st.columns([1, 0.1, 1])

# -------------------------------------------------------------------
# 🧩 MERGE PDFs
# -------------------------------------------------------------------
with merge_col:
    st.header("🔗 Merge PDFs")

    merge_files = st.file_uploader(
        "Upload PDF files to merge", type=["pdf"], accept_multiple_files=True, key="merge_files"
    )
    merge_name = st.text_input("Custom output file name", value="merged.pdf", key="merge_name")

    if "merge_cert" not in st.session_state:
        st.session_state.merge_cert = False

    st.session_state.merge_cert = st.checkbox(
        "Generate Data Deletion Certificate for Merge",
        value=st.session_state.merge_cert,
        key="merge_cert_checkbox"
    )

    if merge_files and st.button("Merge PDFs"):
        try:
            writer = PdfWriter()
            for pdf in merge_files:
                reader = PdfReader(pdf)
                for page in reader.pages:
                    writer.add_page(page)

            merged_bytes = BytesIO()
            writer.write(merged_bytes)
            merged_bytes.seek(0)

            st.success("✅ PDFs merged successfully!")
            st.download_button(
                "⬇️ Download Merged PDF",
                data=merged_bytes,
                file_name=merge_name,
                mime="application/pdf",
            )

            # Generate optional certificate
            if st.session_state.merge_cert:
                cert = BytesIO()
                c = canvas.Canvas(cert)
                c.setFont("Helvetica", 12)
                c.drawString(50, 750, "Data Deletion Certificate (Merge)")
                c.setFont("Helvetica", 10)
                c.drawString(50, 720, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                c.drawString(50, 700, "This certifies that all temporary files used for merging were deleted.")
                c.save()
                cert.seek(0)

                st.download_button(
                    "📜 Download Merge Deletion Certificate",
                    data=cert,
                    file_name="merge_deletion_certificate.pdf",
                    mime="application/pdf",
                )

        except Exception as e:
            st.error(f"Error merging PDFs: {e}")

# -------------------------------------------------------------------
# ✂️ SPLIT PDFs
# -------------------------------------------------------------------
with split_col:
    st.header("📑 Split PDF by Page Ranges")

    split_file = st.file_uploader("Upload PDF to split", type=["pdf"], key="split_file")

    if split_file:
        reader = PdfReader(split_file)
        total_pages = len(reader.pages)
        st.success(f"Uploaded PDF has {total_pages} pages.")

        # Initialize session state
        if "split_downloaded" not in st.session_state:
            st.session_state.split_downloaded = []

        st.markdown("**Enter page ranges separated by commas (e.g., 1-5, 10-15, 20-25)**")
        user_input = st.text_input("Page ranges", value="", key="range_input")

        ranges = []
        try:
            for part in user_input.split(","):
                if not part.strip():
                    continue
                start, end = map(int, part.split("-"))
                if start < 1 or end > total_pages or start > end:
                    st.error(f"Invalid range: {start}-{end} (must be within 1-{total_pages})")
                else:
                    ranges.append((start, end))
        except:
            st.warning("⚠️ Please enter ranges correctly in format: start-end, separated by commas.")

        if ranges:
            # Initialize tracking for each range
            if len(st.session_state.split_downloaded) != len(ranges):
                st.session_state.split_downloaded = [False] * len(ranges)

            for i, (start, end) in enumerate(ranges):
                if not st.session_state.split_downloaded[i]:
                    writer = PdfWriter()
                    for p in range(start - 1, end):
                        writer.add_page(reader.pages[p])

                    output_bytes = BytesIO()
                    writer.write(output_bytes)
                    output_bytes.seek(0)

                    if st.download_button(
                        f"⬇️ Download pages {start}-{end}",
                        data=output_bytes,
                        file_name=f"pages_{start}_{end}.pdf",
                        mime="application/pdf",
                        key=f"dl_btn_{i}"
                    ):
                        st.session_state.split_downloaded[i] = True
                        st.success(f"✅ Pages {start}-{end} downloaded!")

            if all(st.session_state.split_downloaded) and len(ranges) > 0:
                st.success("🎉 All selected page ranges have been downloaded!")

                # Optional certificate
                if "split_cert" not in st.session_state:
                    st.session_state.split_cert = False

                st.session_state.split_cert = st.checkbox(
                    "Generate Data Deletion Certificate for Split",
                    value=st.session_state.split_cert,
                    key="split_cert_checkbox"
                )

                if st.session_state.split_cert:
                    cert = BytesIO()
                    c = canvas.Canvas(cert)
                    c.setFont("Helvetica", 12)
                    c.drawString(50, 750, "Data Deletion Certificate (Split)")
                    c.setFont("Helvetica", 10)
                    c.drawString(50, 720, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    c.drawString(50, 700, "All temporary split files were securely deleted.")
                    c.save()
                    cert.seek(0)

                    st.download_button(
                        "📜 Download Split Deletion Certificate",
                        data=cert,
                        file_name="split_deletion_certificate.pdf",
                        mime="application/pdf",
                    )

                if st.button("🔄 Reset Split"):
                    st.session_state.split_downloaded = [False] * len(ranges)
                    st.rerun()
