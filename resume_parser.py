import io
import re
import logging
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime

# PDF processing
try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Word document processing
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# NLP processing
try:
    import spacy
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False

logger = logging.getLogger(__name__)

class ResumeParser:
    """Advanced resume parser with AI-powered text extraction and analysis"""

    def __init__(self):
        # Skills database
        self.skills_keywords = [
            # Programming Languages
            "python", "java", "javascript", "typescript", "c++", "c#", "php", "ruby", "go", "rust",
            "swift", "kotlin", "scala", "r", "matlab", "sql", "html", "css", "sass", "less",

            # Frameworks & Libraries
            "react", "angular", "vue", "node.js", "express", "django", "flask", "spring", "laravel",
            "rails", "asp.net", ".net", "fastapi", "nextjs", "nuxt", "svelte", "jquery",

            # Databases
            "mysql", "postgresql", "mongodb", "redis", "sqlite", "oracle", "sql server", "elasticsearch",
            "firebase", "dynamodb", "cassandra", "neo4j",

            # Cloud & DevOps
            "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "jenkins", "gitlab ci",
            "github actions", "terraform", "ansible", "vagrant", "chef", "puppet",

            # Data Science & AI
            "machine learning", "deep learning", "artificial intelligence", "data science", "pandas",
            "numpy", "scikit-learn", "tensorflow", "pytorch", "keras", "opencv", "nltk", "spacy",

            # Other Technical Skills
            "git", "linux", "unix", "windows", "macos", "bash", "powershell", "rest api", "graphql",
            "microservices", "agile", "scrum", "kanban", "jira", "confluence", "slack", "teams"
        ]

        # Education keywords
        self.education_keywords = [
            "bachelor", "master", "phd", "doctorate", "diploma", "certificate", "degree",
            "b.tech", "m.tech", "b.sc", "m.sc", "b.com", "m.com", "bca", "mca", "mba",
            "computer science", "information technology", "software engineering", "data science",
            "electrical engineering", "mechanical engineering", "civil engineering"
        ]

        # Experience level keywords
        self.experience_keywords = [
            "intern", "junior", "senior", "lead", "principal", "architect", "manager", "director",
            "ceo", "cto", "vp", "head", "specialist", "consultant", "analyst", "developer",
            "engineer", "programmer", "designer", "administrator"
        ]

        # Initialize NLP model if available
        self.nlp = None
        if NLP_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("spaCy model loaded successfully")
            except Exception as e:
                logger.warning(f"Could not load spaCy model: {e}")

    async def parse_resume_file(self, file) -> Dict[str, Any]:
        """Parse resume file and extract structured information"""
        try:
            # Extract text based on file type
            if file.content_type == "application/pdf":
                text = await self._extract_text_from_pdf(file)
            elif file.content_type in [
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/msword"
            ]:
                text = await self._extract_text_from_docx(file)
            else:
                raise ValueError(f"Unsupported file type: {file.content_type}")

            # Parse extracted text
            parsed_data = await self._parse_text(text)

            # Add metadata
            parsed_data["metadata"] = {
                "filename": file.filename,
                "file_type": file.content_type,
                "parsed_at": datetime.utcnow().isoformat(),
                "text_length": len(text),
                "parser_version": "1.0.0"
            }

            return parsed_data

        except Exception as e:
            logger.error(f"Error parsing resume file: {e}")
            raise

    async def _extract_text_from_pdf(self, file) -> str:
        """Extract text from PDF file"""
        if not PDF_AVAILABLE:
            raise ImportError("pdfplumber not available. Install with: pip install pdfplumber")

        try:
            content = await file.read()
            text = ""

            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise

    async def _extract_text_from_docx(self, file) -> str:
        """Extract text from DOCX file"""
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx not available. Install with: pip install python-docx")

        try:
            content = await file.read()
            doc = docx.Document(io.BytesIO(content))

            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"

            return text.strip()
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {e}")
            raise

    async def _parse_text(self, text: str) -> Dict[str, Any]:
        """Parse extracted text and return structured data"""

        # Clean text
        cleaned_text = self._clean_text(text)

        # Extract different sections
        result = {
            "personal_info": await self._extract_personal_info(cleaned_text),
            "contact_info": await self._extract_contact_info(cleaned_text),
            "skills": await self._extract_skills(cleaned_text),
            "education": await self._extract_education(cleaned_text),
            "experience": await self._extract_experience(cleaned_text),
            "summary": await self._extract_summary(cleaned_text),
            "raw_text": text[:1000] + "..." if len(text) > 1000 else text
        }

        return result

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()

    async def _extract_personal_info(self, text: str) -> Dict[str, Any]:
        """Extract personal information like name"""

        # Try to extract name from the first few lines
        lines = text.split('\n')[:5]  # First 5 lines

        name = None
        for line in lines:
            line = line.strip()
            if len(line) > 0 and not any(keyword in line.lower() for keyword in ['email', 'phone', 'address', 'linkedin']):
                # Simple heuristic: if it's short and contains proper nouns
                words = line.split()
                if 2 <= len(words) <= 4 and all(word.replace('.', '').isalpha() for word in words):
                    if any(word[0].isupper() for word in words):
                        name = line
                        break

        # Use spaCy if available for better name extraction
        if self.nlp and name is None:
            doc = self.nlp(text[:500])  # First 500 characters
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    name = ent.text
                    break

        return {
            "name": name,
            "extracted_from": "text_analysis"
        }

    async def _extract_contact_info(self, text: str) -> Dict[str, Any]:
        """Extract contact information"""

        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)

        # Phone extraction
        phone_patterns = [
            r'\+?1?[-.]?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}',  # US format
            r'\+?\d{1,3}[-.]?\(?\d{3,4}\)?[-.]?\d{3,4}[-.]?\d{3,4}',  # International
            r'\(\d{3}\)\s?\d{3}-\d{4}',  # (123) 456-7890
        ]

        phones = []
        for pattern in phone_patterns:
            phones.extend(re.findall(pattern, text))

        # LinkedIn extraction
        linkedin_pattern = r'linkedin\.com/in/([A-Za-z0-9-]+)'
        linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORECASE)

        # Location extraction (simple city, state pattern)
        location_pattern = r'\b([A-Za-z\s]+),\s*([A-Za-z\s]{2,})\b'
        locations = re.findall(location_pattern, text)

        return {
            "emails": list(set(emails)),  # Remove duplicates
            "phones": list(set(phones)),
            "linkedin": linkedin_matches[0] if linkedin_matches else None,
            "location": locations[0] if locations else None
        }

    async def _extract_skills(self, text: str) -> Dict[str, Any]:
        """Extract skills from text"""

        text_lower = text.lower()
        found_skills = []

        # Check for skills in our predefined list
        for skill in self.skills_keywords:
            if skill.lower() in text_lower:
                # Count occurrences for relevance scoring
                count = text_lower.count(skill.lower())
                found_skills.append({
                    "skill": skill.title(),
                    "mentions": count,
                    "category": self._categorize_skill(skill)
                })

        # Sort by mentions (relevance)
        found_skills.sort(key=lambda x: x["mentions"], reverse=True)

        return {
            "technical_skills": found_skills[:20],  # Top 20 skills
            "total_skills_found": len(found_skills)
        }

    def _categorize_skill(self, skill: str) -> str:
        """Categorize skill into type"""
        programming_langs = ["python", "java", "javascript", "c++", "php", "ruby"]
        frameworks = ["react", "angular", "django", "flask", "spring"]
        databases = ["mysql", "mongodb", "postgresql", "redis"]
        cloud = ["aws", "azure", "gcp", "docker", "kubernetes"]

        if skill.lower() in programming_langs:
            return "programming_language"
        elif skill.lower() in frameworks:
            return "framework"
        elif skill.lower() in databases:
            return "database"
        elif skill.lower() in cloud:
            return "cloud_devops"
        else:
            return "other"

    async def _extract_education(self, text: str) -> Dict[str, Any]:
        """Extract education information"""

        education_info = []

        # Find education patterns
        degree_pattern = r'(bachelor|master|phd|doctorate|diploma|b\.tech|m\.tech|b\.sc|m\.sc|mba|bca|mca).*?(?:in|of)\s+([\w\s]+)'
        degree_matches = re.findall(degree_pattern, text, re.IGNORECASE)

        for degree, field in degree_matches:
            education_info.append({
                "degree": degree.title(),
                "field": field.strip().title(),
                "type": "degree"
            })

        # Find years
        year_pattern = r'\b(19|20)\d{2}\b'
        years = re.findall(year_pattern, text)

        # Find university/college names (simple heuristic)
        university_keywords = ["university", "college", "institute", "school"]
        lines = text.split('\n')

        universities = []
        for line in lines:
            if any(keyword in line.lower() for keyword in university_keywords):
                # Clean up the line
                clean_line = re.sub(r'\d{4}', '', line).strip()
                if len(clean_line) > 5:
                    universities.append(clean_line)

        return {
            "degrees": education_info,
            "institutions": universities[:3],  # Top 3 institutions found
            "graduation_years": list(set(years))
        }

    async def _extract_experience(self, text: str) -> Dict[str, Any]:
        """Extract work experience information"""

        experience_info = []

        # Find years of experience
        exp_pattern = r'(\d+)\+?\s*(years?|yrs?)\s*of\s*experience'
        exp_matches = re.findall(exp_pattern, text, re.IGNORECASE)

        total_experience = None
        if exp_matches:
            # Take the highest number found
            years = [int(match[0]) for match in exp_matches]
            total_experience = max(years)

        # Find job titles
        job_titles = []
        for keyword in self.experience_keywords:
            pattern = f'\b{keyword}\s+(\w+\s*)*(?:engineer|developer|manager|analyst|designer|specialist)'
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                title = keyword + ' ' + ''.join(match).strip()
                job_titles.append(title.title())

        # Find company names (heuristic: capitalized words near job titles)
        companies = []
        # This is a simplified approach - in production, you'd use NER
        company_pattern = r'\bat\s+([A-Z][\w\s&.,]+(?:Inc|LLC|Corp|Ltd|Company|Co\.)?)'
        company_matches = re.findall(company_pattern, text)
        companies.extend(company_matches)

        return {
            "total_years_experience": total_experience,
            "job_titles": list(set(job_titles))[:5],
            "companies": list(set(companies))[:5],
            "experience_level": self._determine_experience_level(total_experience)
        }

    def _determine_experience_level(self, years: Optional[int]) -> str:
        """Determine experience level based on years"""
        if years is None:
            return "unknown"
        elif years < 2:
            return "entry_level"
        elif years < 5:
            return "junior"
        elif years < 10:
            return "mid_level"
        else:
            return "senior"

    async def _extract_summary(self, text: str) -> Dict[str, Any]:
        """Extract or generate summary"""

        # Look for summary/objective section
        summary_keywords = ["summary", "objective", "profile", "about"]
        lines = text.split('\n')

        summary_text = None
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in summary_keywords):
                # Take next few lines as summary
                summary_lines = lines[i+1:i+4]
                summary_text = '\n'.join(summary_lines).strip()
                break

        return {
            "summary": summary_text,
            "source": "extracted" if summary_text else "not_found"
        }