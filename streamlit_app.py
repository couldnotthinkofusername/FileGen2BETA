from transformers import pipeline
from docx import Document
import pdfplumber
import logging
import streamlit as st

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@st.cache_resource(show_spinner=True)
def load_summarizer():
    return pipeline("summarization")

def extract_text_from_docx(file):
    doc = Document(file)
    full_text = [para.text for para in doc.paragraphs]
    return "\n".join(full_text)

import pdfplumber

def extract_text_from_pdf_plumber(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def summarize_text(summarizer, text, max_length = 130, min_length = 50):

    if len(text) > 1000:
        text = text[:1000]
    summary = summarizer(text, max_length=max_length, min_length=min_length, do_sample=False)
    return summary[0]['summary_text']

def main():
    st.set_page_config(
        page_title='FileGen2',
        page_icon='📄',
        layout='centered',
        initial_sidebar_state='auto',
    )
    st.title('File Gen 2')
    st.markdown('File Summarizer (DOCX/PDF only)')

    st.markdown('''<style>
        .stButton>button {
            width: 100%; 
            padding: 0.5rem; 
            font-weight: bold; 
            border-radius: 10px; 
            border-color: #AB2323;
            color: red;
        }
        .summary-box {
            border: 1px solid rgb(166, 80, 126);
            padding: 1rem;
            border-radius: 8px;
            border-color: #A6507E;
            margin-bottom: 1rem;
            line-height: 1.5;
            white-space: pre-wrap;
        }
        .error-box {
            background-color: #ffcccb; 
            padding: 1rem; 
            border-radius: 5px; 
            color: #a00;
            margin-bottom: 1rem;
        }
    </style>''', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        label = 'Upload File',
        type = ['docx', 'pdf'],
        accept_multiple_files = False
    )

    if uploaded_file:
        if st.button('Summarize'):
            try:
                file_type = uploaded_file.name.split('.')[-1].lower()
                
                if file_type == 'docx':
                    text = extract_text_from_docx(uploaded_file)
               
                elif file_type == 'pdf':
                    text = extract_text_from_pdf_plumber(uploaded_file)
                
                else:
                    st.error("Unsupported file format. Please upload a DOCX or PDF file.")
                    return

                if not text.strip():
                    st.error("No extractable text found in the document.")
                    return
                
                with st.spinner('Processing File...'):
                    summarizer = load_summarizer()
                    summary = summarize_text(summarizer,text)

                st.markdown("Summary")
                st.markdown(f'<div class="summary-box">{summary}</div>', unsafe_allow_html=True)
                
                st.session_state.summary = summary
                
                st.download_button(
                    label = "Download Summary",
                    data = st.session_state.summary,
                    file_name = "Summary.txt",
                    mime = "text/plain",
                    type = "primary"
                )
                
            except Exception as e:
                logging.error(f"Error during summarization: {e}")
                st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
