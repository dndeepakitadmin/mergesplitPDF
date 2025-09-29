import streamlit as st
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import tempfile
import os

st.set_page_config(page_title="PDF Tool", page_icon="📄", layout="centered")
st.title("📄 PDF Tools - Merge & Split")

# --- PDF Merge ---
def merge_pdfs(files):
    if not files:
        return None
    merger = PdfMerger()
    for file in files:
        merger.append(file)
    output_path = os.path.join(tempfile.gettempdir(), "merged.pdf")
    with open(output_path, "wb") as f:
        merger.write(f)
    merger.close()
    return output_path

# --- PDF Split by ranges ---
def split_pdf_by_ranges(file, ranges):
    if not file or not ranges:
        return None
    reader = PdfReader(file)
    output_files = []
    for i, (start, end) in enumerate(ranges):
        writer = PdfWriter()
        for page_num in range(start-1, min(end, len(reader.pages))):
            writer.add_page(reader.pages[page_num])
        out_path = os.path.join(tempfile.gettempdir(), f"split_{start}_{end}.pdf")
        with open(out_path, "wb") as f:
            writer.write(f)
        output_files.append((f"{start}-{end}", out_path))
    return output_files

# --- UI Tabs ---
tab1, tab2 = st.tabs(["🔗 Merge PDFs", "✂️ Split PDF"])

# --- Merge PDFs ---
with tab1:
    st.header("Merge PDFs")
    uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)
    custom_name = st.text_input("Enter file name for merged PDF (without extension)", value="merged")
    
    if st.button("Merge") and uploaded_files:
        temp_files = []
        for file in uploaded_files:
            temp_path = os.path.join(tempfile.gettempdir(), file.name)
            with open(temp_path, "wb") as f:
                f.write(file.getbuffer())
            temp_files.append(temp_path)
        merged_file = merge_pdfs(temp_files)
        if merged_file:
            with open(merged_file, "rb") as f:
                st.download_button("⬇️ Download Merged PDF", f, file_name=f"{custom_name}.pdf")

# --- Split PDFs ---
with tab2:
    st.header("Split PDF")
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    
    if uploaded_file:
        # Save temporary file
        temp_path = os.path.join(tempfile.gettempdir(), uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Get number of pages
        reader = PdfReader(temp_path)
        total_pages = len(reader.pages)
        st.info(f"📄 The uploaded file has **{total_pages} pages**.")
        
        # Page ranges input
        page_ranges_text = st.text_area(
            "Enter page ranges separated by commas (e.g., 1-30,50-75,96-113,125-148)",
            value=""
        )

        if st.button("Split"):
            # Parse user ranges
            try:
                ranges = []
                for part in page_ranges_text.split(","):
                    start, end = map(int, part.strip().split("-"))
                    if start < 1 or end > total_pages or start > end:
                        st.error(f"Invalid range {start}-{end}. File has only {total_pages} pages.")
                        ranges = []
                        break
                    ranges.append((start, end))
            except Exception as e:
                st.error("Invalid page range format. Use like 1-30,50-75,...")
                ranges = []

            if ranges:
                split_files = split_pdf_by_ranges(temp_path, ranges)
                if split_files:
                    for label, path in split_files:
                        with open(path, "rb") as f:
                            st.download_button(f"⬇️ Download Pages {label}", f, file_name=f"pages_{label}.pdf")
