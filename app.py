import gradio as gr
from PyPDF2 import PdfMerger, PdfReader
import os

# --- PDF Merge Function ---
def merge_pdfs(files):
    merger = PdfMerger()
    for f in files:
        merger.append(f.name)
    output_path = "merged.pdf"
    merger.write(output_path)
    merger.close()
    return output_path

# --- PDF Split Function ---
def split_pdf(file, start_page, end_page):
    reader = PdfReader(file.name)
    writer_output = "split.pdf"

    from PyPDF2 import PdfWriter
    writer = PdfWriter()
    for page in range(start_page-1, end_page):  # 0-index
        writer.add_page(reader.pages[page])
    with open(writer_output, "wb") as f_out:
        writer.write(f_out)
    return writer_output

# --- Gradio Interface ---
with gr.Blocks() as demo:
    gr.Markdown("## 📄 PDF Tools - Merge & Split (Lightweight Version)")
    
    with gr.Tab("Merge PDFs"):
        merge_input = gr.File(file_types=[".pdf"], label="Upload PDFs", file_types_multiple=True)
        merge_output = gr.File(label="Download Merged PDF")
        merge_btn = gr.Button("Merge")
        merge_btn.click(fn=merge_pdfs, inputs=merge_input, outputs=merge_output)

    with gr.Tab("Split PDF"):
        split_input = gr.File(file_types=[".pdf"], label="Upload PDF")
        start_page = gr.Number(label="Start Page", value=1)
        end_page = gr.Number(label="End Page", value=1)
        split_output = gr.File(label="Download Split PDF")
        split_btn = gr.Button("Split")
        split_btn.click(fn=split_pdf, inputs=[split_input, start_page, end_page], outputs=split_output)

demo.launch()
