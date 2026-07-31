# 🧠 AI-Based Text Summarizer

An AI-powered web application that automatically generates concise and meaningful summaries from lengthy documents using Natural Language Processing (NLP) and Transformer-based models. The application supports PDF, DOCX, TXT files, and direct text input with a modern, responsive user interface.

---

## 🚀 Features

- 📄 Upload PDF, DOCX, and TXT documents
- ✍️ Paste text directly for summarization
- 🤖 AI-powered text summarization using Hugging Face Transformers
- 🔑 Automatic keyword extraction
- ⏱️ Reading time estimation
- 📊 Summary history using SQLite database
- 📥 Export summary as PDF and DOCX
- 📱 Responsive and user-friendly interface

---

## 🛠️ Tech Stack

### Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap 5

### Backend
- Python
- Flask

### AI & NLP
- Hugging Face Transformers
- PyTorch
- NLTK
- spaCy
- YAKE

### Database
- SQLite

### Utilities
- PyPDF2
- pdfplumber
- python-docx
- ReportLab

---

# 📂 Project Structure

```
AI-Text-Summarizer
│
├── app.py
├── requirements.txt
│
├── models
│      summarizer.py
│      keyword.py
│      preprocess.py
│
├── utils
│      pdf_reader.py
│      doc_reader.py
│      exporter.py
│
├── database
│      history.db
│
├── uploads
├── outputs
│
├── templates
│      base.html
│      index.html
│      dashboard.html
│
└── static
       ├── css
       ├── js
       └── images
```

---

# ⚙️ Prerequisites

Install the following before running the project.

- Python 3.10 or above
- Visual Studio Code
- Git
- GitHub Account

---

# 🧰 Recommended VS Code Extensions

Install these extensions from VS Code Marketplace.

- Python (Microsoft)
- Pylance
- Jupyter
- GitHub Copilot (Optional)
- GitLens (Optional)
- Prettier
- HTML CSS Support
- Bootstrap IntelliSense

---

# 📥 Clone Repository

```bash
git clone https://github.com/your-username/AI-Text-Summarizer.git
```

```bash
cd AI-Text-Summarizer
```

---

# 🐍 Create Virtual Environment

Windows

```bash
python -m venv venv
```

Activate Virtual Environment

Command Prompt

```bash
venv\Scripts\activate
```

PowerShell

```powershell
venv\Scripts\Activate.ps1
```

Mac/Linux

```bash
source venv/bin/activate
```

---

# 📦 Install Dependencies

```bash
pip install -r requirements.txt
```

If you don't have a requirements file, install manually.

```bash
pip install flask
pip install transformers
pip install torch
pip install sentencepiece
pip install nltk
pip install spacy
pip install PyPDF2
pip install pdfplumber
pip install python-docx
pip install reportlab
pip install pandas
pip install scikit-learn
pip install yake
pip install flask_sqlalchemy
pip install python-dotenv
pip install waitress
```

Download the English language model for spaCy.

```bash
python -m spacy download en_core_web_sm
```

---

# ▶️ Run the Application

```bash
python app.py
```

or

```bash
flask run
```

---

# 🌐 Open in Browser

```
http://127.0.0.1:5000
```

---

# 📋 Supported File Types

- PDF
- DOCX
- TXT

---

# 🔄 Workflow

```
User Upload
      │
      ▼
Text Extraction
      │
      ▼
Preprocessing
      │
      ▼
AI Summarization
      │
      ▼
Keyword Extraction
      │
      ▼
Display Summary
      │
      ▼
Export PDF / DOCX
```

---

# 📸 Screenshots

Add screenshots of your application here.

```
Home Page

Dashboard

Summary Output

History
```

---

# 🔮 Future Enhancements

- Multi-language summarization
- Voice summarization
- User authentication
- Cloud deployment
- AI chatbot integration
- OCR support for scanned PDFs
- REST API support

---

# 👩‍💻 Author

**Aishwarya Varshini Grandhi**

B.Tech Computer Science Engineering

GitHub: https://github.com/Aishwaryavarshinigrandhi

LinkedIn: https://linkedin.com/in/aishwarya-varshini-grandhi-bb657a368/

---

# 📄 License

This project is developed for educational and learning purposes.
