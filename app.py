import gradio as gr
from PyPDF2 import PdfMerger, PdfReader
import tempfile
import os

# --- PDF Merge Function ---
def merge_pdfs(files):
    if not files:
        return None

    merger = PdfMerger()
    for file in files:
        merger.append(file.name)

    output_path = os.path.join(tempfile.gettempdir(), "merged.pdf")
    merger.write(output_path)
    merger.close()
    return output_path

# --- PDF Split Function ---
def split_pdf(file):
    if not file:
        return None

    reader = PdfReader(file.name)
    output_files = []
    for i, page in enumerate(reader.pages):
        writer = PdfMerger()
        writer.append(file.name, pages=(i, i+1))
        out_path = os.path.join(tempfile.gettempdir(), f"page_{i+1}.pdf")
        writer.write(out_path)
        writer.close()
        output_files.append(out_path)
    return output_files

# --- Gradio UI ---
with gr.Blocks() as demo:
    gr.Markdown("## 📄 PDF Tools - Merge & Split (Stable Version)")
    gr.Markdown("⚠️ Maximum file size per PDF: ~50 MB")

    # Merge PDFs Tab
    with gr.Tab("Merge PDFs"):
        merge_input = gr.File(
            label="Upload PDFs",
            file_types=[".pdf"],
            type="file",
            file_types_multiple=True  # ✅ works with Gradio 3.55+
        )
        merge_output = gr.File(label="Download Merged PDF")
        merge_button = gr.Button("Merge")
        merge_button.click(merge_pdfs, inputs=merge_input, outputs=merge_output)

    # Split PDFs Tab
    with gr.Tab("Split PDF"):
        split_input = gr.File(
            label="Upload a PDF to split",
            file_types=[".pdf"],
            type="file"
        )
        split_output = gr.File(label="Download Split PDFs")
        split_button = gr.Button("Split")
        split_button.click(split_pdf, inputs=split_input, outputs=split_output)

# --- Launch the app ---
demo.launch()
