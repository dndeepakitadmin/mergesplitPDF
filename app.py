import gradio as gr
from PyPDF2 import PdfMerger, PdfReader
import tempfile, os

def merge_pdfs(files):
    if not files:
        return None
    merger = PdfMerger()
    for f in files:
        merger.append(f.name)
    out_path = os.path.join(tempfile.gettempdir(), "merged.pdf")
    merger.write(out_path)
    merger.close()
    return out_path

def split_pdf(file):
    if not file:
        return None
    reader = PdfReader(file.name)
    out_files = []
    for i, page in enumerate(reader.pages):
        writer = PdfMerger()
        writer.append(file.name, pages=(i, i+1))
        path = os.path.join(tempfile.gettempdir(), f"page_{i+1}.pdf")
        writer.write(path)
        writer.close()
        out_files.append(path)
    return out_files

with gr.Blocks() as demo:
    gr.Markdown("## 📄 PDF Tools - Merge & Split")
    gr.Markdown("⚠️ Max file size per PDF ~50MB")

    with gr.Tab("Merge PDFs"):
        merge_input = gr.File(
            label="Upload PDFs",
            file_types=[".pdf"],
            file_count="multiple",      # ✅ multiple files
            type="filepath"             # ✅ must be 'filepath' or 'binary'
        )
        merge_output = gr.File(label="Download Merged PDF")
        merge_button = gr.Button("Merge")
        merge_button.click(merge_pdfs, inputs=merge_input, outputs=merge_output)

    with gr.Tab("Split PDF"):
        split_input = gr.File(
            label="Upload PDF to split",
            file_types=[".pdf"],
            type="filepath"             # ✅ 'filepath'
        )
        split_output = gr.File(label="Download Split PDFs")
        split_button = gr.Button("Split")
        split_button.click(split_pdf, inputs=split_input, outputs=split_output)

demo.launch()
