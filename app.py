import streamlit as st
import os
import shutil
import zipfile
import re
import tempfile
from pdf2image import convert_from_path
from PIL import Image
import requests

# Configurações
st.set_page_config(page_title="Conversor de Documentos", layout="wide")

WORK_DIR = tempfile.mkdtemp()

def salvar_arquivo(uploaded_file):
    filename = re.sub(r'[^\w\-_\. ]', '_', uploaded_file.name)
    path = os.path.join(WORK_DIR, filename)
    with open(path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return path, filename

def criar_link_download(caminho, nome, label, mime="application/octet-stream"):
    with open(caminho, "rb") as f:
        st.download_button(label, data=f, file_name=nome, mime=mime)

# === WORD → PDF com API Railway ===
RAILWAY_API_URL = "https://testepdf-production.up.railway.app/convert"

def word_para_pdf():
    st.header("📄 Word para PDF (via API Railway)")
    arquivos = st.file_uploader("Selecione arquivos .docx", type=["docx"], accept_multiple_files=True)
    if not arquivos:
        return
    if st.button("Converter para PDF"):
        for arquivo in arquivos:
            files = {"file": (arquivo.name, arquivo.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
            response = requests.post(RAILWAY_API_URL, files=files)
            if response.status_code == 200:
                nome_pdf = os.path.splitext(arquivo.name)[0] + ".pdf"
                st.download_button(f"📥 Baixar {nome_pdf}", data=response.content, file_name=nome_pdf, mime="application/pdf")
            else:
                st.error(f"Erro ao converter {arquivo.name}")

# === PDF → JPG ===
def pdf_para_jpg():
    st.header("🖼️ PDF para JPG")
    arquivo = st.file_uploader("Selecione um PDF", type=["pdf"])
    if not arquivo:
        return
    if not shutil.which("pdftoppm"):
        st.error("❌ Poppler não está instalado. O PDF não pode ser convertido.")
        return
    if st.button("Converter para JPG"):
        path, nome = salvar_arquivo(arquivo)
        nome_base = os.path.splitext(nome)[0]
        imagens = convert_from_path(path, dpi=300)
        zip_path = os.path.join(WORK_DIR, f"{nome_base}_jpg.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for i, img in enumerate(imagens):
                img_nome = f"{nome_base}_pag{i+1}.jpg"
                img_path = os.path.join(WORK_DIR, img_nome)
                img.save(img_path, "JPEG", quality=90)
                zipf.write(img_path, img_nome)
        st.success(f"Convertido {len(imagens)} páginas!")
        criar_link_download(zip_path, f"{nome_base}_jpg.zip", "📥 Baixar ZIP com imagens", mime="application/zip")

# === Interface Principal ===
def main():
    st.title("📄 Conversor de Documentos")
    menu = st.sidebar.selectbox("Escolha a função", ["Word para PDF", "PDF para JPG"])

    if st.sidebar.button("🧹 Limpar arquivos temporários"):
        shutil.rmtree(WORK_DIR)
        os.makedirs(WORK_DIR, exist_ok=True)
        st.sidebar.success("Arquivos limpos.")

    if menu == "Word para PDF":
        word_para_pdf()
    elif menu == "PDF para JPG":
        pdf_para_jpg()

if __name__ == "__main__":
    main()

