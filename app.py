import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO

st.title("AI PDF Tool")

# User acknowledgment
ack = st.checkbox(
    "I acknowledge that this tool will NOT be used for unethical or illegal purposes. "
    "It is intended only for personal and professional use."
)

if not ack:
    st.warning("You must acknowledge the terms to use this tool.")
    st.stop()

# File upload warning
st.info("⚠️ Make sure the file you are uploading is not encrypted or corrupted.")

# Upload PDF
uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
if uploaded_file:
    pdf_reader = PdfReader(uploaded_file)
    total_pages = len(pdf_reader.pages)
    st.success(f"Uploaded PDF has {total_pages} pages.")

    # Define multiple page ranges
    ranges = [(1, 15), (20, 25), (30, 45)]

    # Initialize session state for tracking downloads
    if "downloaded" not in st.session_state:
        st.session_state.downloaded = [False] * len(ranges)

    for i, (start, end) in enumerate(ranges):
        # Adjust to actual PDF page count
        end = min(end, total_pages)

        if not st.session_state.downloaded[i]:
            # Create PDF for the range
            pdf_writer = PdfWriter()
            for page_num in range(start - 1, end):
                pdf_writer.add_page(pdf_reader.pages[page_num])

            pdf_bytes = BytesIO()
            pdf_writer.write(pdf_bytes)
            pdf_bytes.seek(0)

            # Download button
            if st.download_button(
                label=f"Download pages {start}-{end}",
                data=pdf_bytes,
                file_name=f"pages_{start}_{end}.pdf",
                mime="application/pdf"
            ):
                st.session_state.downloaded[i] = True
                st.success(f"Pages {start}-{end} downloaded!")

    # Check if all ranges downloaded
    if all(st.session_state.downloaded):
        st.balloons()
        st.success("All selected ranges downloaded! You can reset now.")
        if st.button("Reset"):
            st.session_state.downloaded = [False] * len(ranges)
