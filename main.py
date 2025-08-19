from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import io
import logging
from typing import Optional, List, Dict, Any
from resume_parser import ResumeParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Resume Parser API",
    description="AI-powered resume parsing service that extracts structured data from PDF and Word documents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize resume parser
resume_parser = ResumeParser()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Resume Parser API is running",
        "version": "1.0.0",
        "status": "healthy",
        "supported_formats": ["PDF", "DOC", "DOCX"]
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "resume-parser-api",
        "version": "1.0.0"
    }

@app.post("/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    """
    Parse resume and extract structured information

    Accepts: PDF, DOC, DOCX files
    Returns: Structured JSON with extracted resume data
    """
    try:
        # Validate file type
        allowed_types = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword"
        ]

        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}. Supported types: PDF, DOC, DOCX"
            )

        # Validate file size (max 10MB)
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=413,
                detail="File too large. Maximum size: 10MB"
            )

        # Reset file pointer
        await file.seek(0)

        # Parse resume
        parsed_data = await resume_parser.parse_resume_file(file)

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "Resume parsed successfully",
                "filename": file.filename,
                "file_size": len(content),
                "data": parsed_data
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error parsing resume: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error while parsing resume",
                "detail": str(e)
            }
        )

@app.post("/parse-resume-batch")
async def parse_resume_batch(files: List[UploadFile] = File(...)):
    """
    Parse multiple resumes in batch

    Accepts: Multiple PDF, DOC, DOCX files
    Returns: Array of parsed resume data
    """
    try:
        if len(files) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 files allowed per batch"
            )

        results = []

        for file in files:
            try:
                # Validate file type
                allowed_types = [
                    "application/pdf",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "application/msword"
                ]

                if file.content_type not in allowed_types:
                    results.append({
                        "filename": file.filename,
                        "status": "error",
                        "message": f"Unsupported file type: {file.content_type}"
                    })
                    continue

                # Parse individual file
                parsed_data = await resume_parser.parse_resume_file(file)

                results.append({
                    "filename": file.filename,
                    "status": "success",
                    "data": parsed_data
                })

            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "message": str(e)
                })

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": f"Processed {len(files)} files",
                "results": results
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Internal server error in batch processing",
                "detail": str(e)
            }
        )

# For Vercel deployment
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)