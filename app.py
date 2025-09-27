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

# --- PDF Split ---
def split_pdf(file):
    if not file:
        return None
    reader = PdfReader(file)
    output_files = []
    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)
        out_path = os.path.join(tempfile.gettempdir(), f"page_{i+1}.pdf")
        with open(out_path, "wb") as f:
            writer.write(f)
        output_files.append(out_path)
    return output_files

# --- UI Tabs ---
tab1, tab2 = st.tabs(["🔗 Merge PDFs", "✂️ Split PDF"])

with tab1:
    st.header("Merge PDFs")
    uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)
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
                st.download_button("⬇️ Download Merged PDF", f, file_name="merged.pdf")

with tab2:
    st.header("Split PDF")
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    if st.button("Split") and uploaded_file:
        temp_path = os.path.join(tempfile.gettempdir(), uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        split_files = split_pdf(temp_path)
        if split_files:
            for i, path in enumerate(split_files, start=1):
                with open(path, "rb") as f:
                    st.download_button(f"⬇️ Download Page {i}", f, file_name=f"page_{i}.pdf")
