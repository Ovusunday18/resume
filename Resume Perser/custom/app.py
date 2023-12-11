from flask import Flask, request, jsonify
import spacy
from docx import Document
import json
import sys, fitz
from pathlib import Path


BASE_DIR = Path(__file__).resolve(strict=True).parent

app = Flask(__name__)
nlp_model = spacy.load(f'{BASE_DIR}/model-best')

def extractTextDocx(docx_file):
    doc = Document(docx_file)
    text = ""

    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"

    return text.strip()


def extractTextPDF(pdf_file):
    doc = fitz.open(pdf_file)
    text = ' '
    for page in doc:
        text = text + str(page.get_text())
    return text


def getText(file):
    if file.filename.endswith('.pdf'):
        try:
            text = extractTextPDF(file)
            return text
        except Exception as e:
            return f"Error extracting text from PDF: {str(e)}"
    elif file.filename.endswith('.docx'):
        try:
            text = extractTextDocx(file)
            return text
        except Exception as e:
            return f"Error extracting text from DOCX: {str(e)}"
    else:
        return "Unsupported file type"


@app.route('/custompred', methods=['POST'])
def customPred():
    
  file = request.files['pdf']
    
  text = getText(file)  
  doc = nlp_model(text)
  entities_data = {}
  for ent in doc.ents:
      if ent.label_ not in entities_data:
          entities_data[ent.label_] = [ent.text]
      else:
          entities_data[ent.label_].append(ent.text)

  return jsonify({'result': entities_data})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
