from flask import Flask, request, send_file
from pdf2image import convert_from_path
import os
import uuid
import zipfile

app = Flask(__name__)

@app.route("/convert", methods=["POST"])
def convert_docx_to_pdf():
    file = request.files.get("file")
    if not file or not file.filename.endswith(".docx"):
        return "Arquivo inválido para este endpoint.", 400

    filename = str(uuid.uuid4()) + ".docx"
    input_path = f"/tmp/{filename}"
    output_path = input_path.replace(".docx", ".pdf")
    file.save(input_path)

    os.system(f"libreoffice --headless --convert-to pdf --outdir /tmp {input_path}")

    if not os.path.exists(output_path):
        return "Erro na conversão.", 500

    return send_file(output_path, as_attachment=True, download_name="convertido.pdf")

@app.route("/convert-pdf-jpg", methods=["POST"])
def convert_pdf_to_jpg():
    file = request.files.get("file")
    if not file or not file.filename.endswith(".pdf"):
        return "Arquivo inválido para este endpoint.", 400

    pdf_path = f"/tmp/{uuid.uuid4()}.pdf"
    file.save(pdf_path)

    try:
        imagens = convert_from_path(pdf_path, dpi=300)
        zip_path = pdf_path.replace(".pdf", ".zip")

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for i, img in enumerate(imagens):
                img_name = f"pagina_{i+1}.jpg"
                img_path = f"/tmp/{img_name}"
                img.save(img_path, "JPEG")
                zipf.write(img_path, img_name)

        return send_file(zip_path, as_attachment=True, download_name="imagens_convertidas.zip")

    except Exception as e:
        return f"Erro ao converter PDF: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
