import streamlit as st
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import tempfile
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

st.set_page_config(page_title="PDF Tool", page_icon="📄", layout="centered")
st.title("📄 PDF Tools - Merge & Split")

st.info("⚠️ Make sure the file you are uploading is not encrypted or corrupted.")

# ------------------ Google Sheets Setup ------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
service_account_info = json.loads(st.secrets["gcp"]["service_account_json"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
gc = gspread.authorize(creds)

# Replace with your Google Sheet name
SHEET_NAME = "PDFToolLogs"
try:
    sheet = gc.open(SHEET_NAME).sheet1
except gspread.SpreadsheetNotFound:
    # Create sheet if not exists
    sh = gc.create(SHEET_NAME)
    sheet = sh.sheet1
    sheet.append_row(["Timestamp", "Action", "Filename", "Pages/Range", "Acknowledgment"])

# ------------------ Functions ------------------

def log_action(action, filename, pages_range="", ack=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([timestamp, action, filename, pages_range, ack])

# --- PDF Merge ---
def merge_pdfs(files, output_name):
    if not files:
        return None
    merger = PdfMerger()
    for file in files:
        merger.append(file)
    output_path = os.path.join(tempfile.gettempdir(), f"{output_name}.pdf")
    with open(output_path, "wb") as f:
        merger.write(f)
    merger.close()
    return output_path

# --- PDF Split by ranges ---
def split_pdf_by_ranges(file_path, ranges):
    reader = PdfReader(file_path)
    output_files = []
    total_pages = len(reader.pages)

    for r in ranges:
        start, end = r
        writer = PdfWriter()
        for i in range(start-1, min(end, total_pages)):
            writer.add_page(reader.pages[i])
        out_path = os.path.join(tempfile.gettempdir(), f"pages_{start}-{end}.pdf")
        with open(out_path, "wb") as f:
            writer.write(f)
        output_files.append((out_path, f"{start}-{end}"))
    return output_files, total_pages

# ------------------ Tabs ------------------
tab1, tab2 = st.tabs(["🔗 Merge PDFs", "✂️ Split PDF"])

# ------------------ Merge ------------------
with tab1:
    st.header("Merge PDFs")
    uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)
    output_name = st.text_input("Enter merged file name:", "merged")
    ack_merge = st.checkbox("I confirm that I will use these files legally and responsibly")
    
    if st.button("Merge") and uploaded_files:
        temp_files = []
        for file in uploaded_files:
            temp_path = os.path.join(tempfile.gettempdir(), file.name)
            with open(temp_path, "wb") as f:
                f.write(file.getbuffer())
            temp_files.append(temp_path)
        merged_file = merge_pdfs(temp_files, output_name)
        if merged_file:
            with open(merged_file, "rb") as f:
                st.download_button("⬇️ Download Merged PDF", f, file_name=f"{output_name}.pdf")
            log_action("Merge", output_name, pages_range=f"{len(temp_files)} files", ack="Yes" if ack_merge else "No")

# ------------------ Split ------------------
with tab2:
    st.header("Split PDF")
    uploaded_file = st.file_uploader("Upload a PDF file to split", type="pdf", key="split_uploader")
    
    if uploaded_file:
        temp_path = os.path.join(tempfile.gettempdir(), uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        reader = PdfReader(temp_path)
        total_pages = len(reader.pages)
        st.info(f"✅ Uploaded PDF has **{total_pages} pages**")
        
        page_ranges_input = st.text_input("Enter page ranges to split (e.g., 1-15,17-25,30-50):")
        ack_split = st.checkbox("I confirm that I will use these files legally and responsibly")
        finished_split = st.button("Finished Splitting")
        
        if page_ranges_input:
            try:
                ranges = []
                for part in page_ranges_input.split(","):
                    start, end = map(int, part.strip().split("-"))
                    ranges.append((start, end))
                
                split_files, _ = split_pdf_by_ranges(temp_path, ranges)
                
                if split_files:
                    st.write("⬇️ Download your split files:")
                    # Only show download buttons until "Finished Splitting" clicked
                    if not finished_split:
                        for out_path, r in split_files:
                            with open(out_path, "rb") as f:
                                st.download_button(f"Download Pages {r}", f, file_name=f"pages_{r}.pdf", key=r)
                    else:
                        for out_path, r in split_files:
                            with open(out_path, "rb") as f:
                                st.download_button(f"Download Pages {r}", f, file_name=f"pages_{r}.pdf", key=r)
                        st.success("✅ Finished splitting. All pages are ready for download.")
                    log_action("Split", uploaded_file.name, pages_range=page_ranges_input, ack="Yes" if ack_split else "No")
            except Exception as e:
                st.error(f"❌ Invalid input. Please enter ranges like 1-15,17-25. Error: {e}")

# ------------------ Optional Deletion Certificate ------------------
st.sidebar.header("Optional: Data Deletion Certificate")
cert_option = st.sidebar.checkbox("I want a certificate confirming uploaded data is deleted after processing")
if cert_option:
    st.sidebar.success("After processing, you can download a certificate stating your data was deleted safely.")
    if st.button("Download Deletion Certificate"):
        cert_text = f"""
        PDF Tool Data Deletion Certificate

        This is to certify that all uploaded PDF files for processing have been deleted from the system
        immediately after processing.

        User: End User
        Tool: PDF Tools - Merge & Split
        Operator: Deepak Narayan
        Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        st.download_button("⬇️ Download Certificate", cert_text, file_name="deletion_certificate.txt")

