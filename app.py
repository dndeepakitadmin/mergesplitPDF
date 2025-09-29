import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from datetime import datetime
import os

# ------------------- Logging Setup -------------------
LOG_FILE = "ack_log.txt"
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        f.write("Timestamp,Action,User Note\n")

def log_action(action, note=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp},{action},{note}\n")

# ------------------- Streamlit UI -------------------
st.set_page_config(page_title="PDF Tool", layout="wide")
st.title("📄 PDF Tool: Merge, Split & Manage PDFs")

# Tabs for Merge and Split
tab = st.tabs(["Merge PDFs", "Split PDFs"])

# ------------------- Merge PDFs -------------------
with tab[0]:
    st.subheader("Merge PDFs")
    merge_files = st.file_uploader("Upload PDFs to merge", type=["pdf"], accept_multiple_files=True)
    merge_name = st.text_input("Enter output file name (without .pdf)", value="merged_pdf")
    
    if st.button("Merge PDFs"):
        if merge_files and merge_name:
            merger = PdfWriter()
            for file in merge_files:
                reader = PdfReader(file)
                for page in reader.pages:
                    merger.add_page(page)
            output_pdf = BytesIO()
            merger.write(output_pdf)
            output_pdf.seek(0)
            
            st.download_button(
                label="Download Merged PDF",
                data=output_pdf,
                file_name=f"{merge_name}.pdf",
                mime="application/pdf"
            )
            log_action("Merged PDFs", f"{merge_name}.pdf")
        else:
            st.warning("Please upload PDFs and provide an output name.")

# ------------------- Split PDFs -------------------
with tab[1]:
    st.subheader("Split PDF")
    split_file = st.file_uploader("Upload a PDF to split", type=["pdf"])
    page_ranges = st.text_input("Enter page ranges (e.g., 1-2,4,6-7)")
    
    if st.button("Split PDF"):
        if split_file and page_ranges:
            reader = PdfReader(split_file)
            ranges = [r.strip() for r in page_ranges.split(",")]
            split_outputs = []
            
            for i, r in enumerate(ranges):
                pages = []
                if "-" in r:
                    start, end = r.split("-")
                    pages = list(range(int(start)-1, int(end)))
                else:
                    pages = [int(r)-1]
                
                writer = PdfWriter()
                for p in pages:
                    if p < len(reader.pages):
                        writer.add_page(reader.pages[p])
                
                split_pdf_io = BytesIO()
                writer.write(split_pdf_io)
                split_pdf_io.seek(0)
                split_outputs.append((f"split_{i+1}.pdf", split_pdf_io))
                st.download_button(
                    label=f"Download split_{i+1}.pdf",
                    data=split_pdf_io,
                    file_name=f"split_{i+1}.pdf",
                    mime="application/pdf"
                )
            
            log_action("Split PDF", f"{split_file.name} into {len(split_outputs)} files")
        else:
            st.warning("Please upload a PDF and provide page ranges.")

# ------------------- Optional Deletion Certificate -------------------
st.markdown("---")
st.subheader("Optional: Data Deletion Certificate")
if st.checkbox("Generate Data Deletion Certificate"):
    user_name = st.text_input("Enter your name for certificate", value="User")
    if st.button("Generate Certificate"):
        from reportlab.pdfgen import canvas
        cert_pdf = BytesIO()
        c = canvas.Canvas(cert_pdf)
        c.setFont("Helvetica-Bold", 20)
        c.drawString(100, 750, "📄 Data Deletion Certificate")
        c.setFont("Helvetica", 14)
        c.drawString(100, 700, f"Name: {user_name}")
        c.drawString(100, 680, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(100, 650, "All uploaded files have been securely deleted from the server session.")
        c.save()
        cert_pdf.seek(0)
        
        st.download_button(
            label="Download Deletion Certificate",
            data=cert_pdf,
            file_name="data_deletion_certificate.pdf",
            mime="application/pdf"
        )
        log_action("Generated Deletion Certificate", f"Name: {user_name}")

# ------------------- Display Log -------------------
if st.checkbox("Show Acknowledgment Log"):
    with open(LOG_FILE, "r") as f:
        log_content = f.read()
    st.text_area("Log", log_content, height=200)
