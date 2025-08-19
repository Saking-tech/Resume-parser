# Resume Parser API 🚀

A powerful AI-driven FastAPI application that extracts structured information from PDF and Word resume documents. This application can be deployed on Vercel as a serverless function.

## ✨ Features

- **Multi-format Support**: Parse PDF, DOC, and DOCX resume files
- **AI-Powered Extraction**: Extract key information using advanced NLP techniques
- **Structured Data Output**: Returns clean, structured JSON data
- **Batch Processing**: Process multiple resumes simultaneously
- **RESTful API**: Clean, documented REST API endpoints
- **Serverless Ready**: Optimized for Vercel serverless deployment
- **CORS Enabled**: Ready for frontend integration

## 📋 Extracted Information

The API extracts the following information from resumes:

- **Personal Information**: Name, contact details
- **Contact Information**: Email addresses, phone numbers, LinkedIn profiles, location
- **Skills**: Technical skills with categorization and relevance scoring
- **Education**: Degrees, institutions, graduation years
- **Work Experience**: Job titles, companies, years of experience
- **Professional Summary**: Extracted objective/summary sections

## 🏗️ Project Structure

```
resume-parser-api/
├── main.py              # FastAPI application entry point
├── resume_parser.py     # Core resume parsing logic
├── requirements.txt     # Python dependencies
├── vercel.json         # Vercel deployment configuration
└── README.md           # This file
```

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd resume-parser-api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download spaCy model (optional but recommended)**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`

## 🌐 Deployment on Vercel

### Prerequisites

- GitHub account
- Vercel account (free tier available)
- Git installed locally

### Step-by-Step Deployment

1. **Push code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Resume Parser API"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy to Vercel**

   **Option A: Using Vercel Dashboard**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will automatically detect the Python project
   - Click "Deploy"

   **Option B: Using Vercel CLI**
   ```bash
   npm install -g vercel
   vercel login
   vercel
   ```

3. **Environment Variables (if needed)**
   - In Vercel dashboard, go to Project Settings > Environment Variables
   - Add any required environment variables

### Important Notes for Vercel Deployment

- **File Size Limit**: Vercel has a 250MB unzipped size limit for serverless functions
- **Execution Time**: Maximum 30 seconds per request on free tier
- **Memory Limit**: 1024MB on free tier
- **Cold Starts**: First requests might be slower due to cold starts

## 📡 API Endpoints

### 1. Health Check
```http
GET /
GET /health
```

**Response:**
```json
{
  "message": "Resume Parser API is running",
  "version": "1.0.0",
  "status": "healthy",
  "supported_formats": ["PDF", "DOC", "DOCX"]
}
```

### 2. Parse Single Resume
```http
POST /parse-resume
Content-Type: multipart/form-data
```

**Request:** Upload a resume file (PDF, DOC, or DOCX)

**Response:**
```json
{
  "status": "success",
  "message": "Resume parsed successfully",
  "filename": "john_doe_resume.pdf",
  "file_size": 245760,
  "data": {
    "personal_info": {
      "name": "John Doe"
    },
    "contact_info": {
      "emails": ["john.doe@email.com"],
      "phones": ["+1-555-123-4567"],
      "linkedin": "john-doe-dev",
      "location": ["San Francisco, CA"]
    },
    "skills": {
      "technical_skills": [
        {
          "skill": "Python",
          "mentions": 5,
          "category": "programming_language"
        }
      ]
    },
    "education": {
      "degrees": [
        {
          "degree": "Bachelor",
          "field": "Computer Science",
          "type": "degree"
        }
      ]
    },
    "experience": {
      "total_years_experience": 3,
      "experience_level": "junior"
    }
  }
}
```

### 3. Parse Multiple Resumes
```http
POST /parse-resume-batch
Content-Type: multipart/form-data
```

**Request:** Upload up to 10 resume files

**Response:**
```json
{
  "status": "success",
  "message": "Processed 3 files",
  "results": [
    {
      "filename": "resume1.pdf",
      "status": "success",
      "data": { ... }
    }
  ]
}
```

## 🧪 Testing the API

### Using curl

```bash
# Health check
curl https://your-vercel-url.vercel.app/

# Parse resume
curl -X POST https://your-vercel-url.vercel.app/parse-resume \
  -F "file=@path/to/your/resume.pdf"
```

### Using Python

```python
import requests

# Parse resume
with open('resume.pdf', 'rb') as f:
    response = requests.post(
        'https://your-vercel-url.vercel.app/parse-resume',
        files={'file': f}
    )
    print(response.json())
```

### Using JavaScript/Frontend

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('https://your-vercel-url.vercel.app/parse-resume', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

## 🔧 Configuration

### File Size Limits
- Maximum file size: 10MB per file
- Maximum files in batch: 10 files

### Supported File Types
- PDF (`application/pdf`)
- Word Document (`application/vnd.openxmlformats-officedocument.wordprocessingml.document`)
- Legacy Word Document (`application/msword`)

## 📈 Performance Optimization

- **Lazy Loading**: NLP models are loaded only when needed
- **Text Caching**: Extracted text is cached during processing
- **Async Processing**: All operations are asynchronous
- **Memory Management**: Large files are processed in streams

## 🐛 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Ensure all dependencies in `requirements.txt` are correctly specified
   - Check Python version compatibility

2. **File upload fails**
   - Verify file size is under 10MB
   - Check file format is supported
   - Ensure proper Content-Type headers

3. **Vercel deployment fails**
   - Check that `vercel.json` configuration is correct
   - Verify file structure matches expected layout
   - Review Vercel build logs for specific errors

4. **spaCy model not found**
   - The app will work without spaCy but with reduced accuracy
   - For production, consider pre-downloading the model

### Error Codes

- `400`: Bad Request (unsupported file type, file too large)
- `413`: Payload Too Large (file exceeds 10MB)
- `500`: Internal Server Error (processing error)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- PDF processing powered by [pdfplumber](https://github.com/jsvine/pdfplumber)
- Word document processing with [python-docx](https://python-docx.readthedocs.io/)
- NLP capabilities via [spaCy](https://spacy.io/)
- Deployed on [Vercel](https://vercel.com/)

---

**Made with ❤️ for the developer community**
