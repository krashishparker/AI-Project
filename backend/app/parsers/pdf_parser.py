import PyPDF2
import pdfplunger
from typing import Dict, Any, Optional
import re


class PDFParser:
    """Parser for PDF resume files."""
    
    @staticmethod
    def extract_text(file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            # Try pdfplumber first (better for tables and layouts)
            try:
                with pdfplumber.open(file_path) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"
                    return text.strip()
            except:
                # Fallback to PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    return text.strip()
        except Exception as e:
            raise Exception(f"PDF parsing error: {str(e)}")
    
    @staticmethod
    def parse_resume(text: str) -> Dict[str, Any]:
        """Parse resume text into structured data."""
        parsed_data = {
            "name": PDFParser._extract_name(text),
            "email": PDFParser._extract_email(text),
            "phone": PDFParser._extract_phone(text),
            "skills": PDFParser._extract_skills(text),
            "education": PDFParser._extract_education(text),
            "experience": PDFParser._extract_experience(text),
            "projects": PDFParser._extract_projects(text),
            "certifications": PDFParser._extract_certifications(text)
        }
        return parsed_data
    
    @staticmethod
    def _extract_name(text: str) -> Optional[str]:
        """Extract name from resume text."""
        # Simple heuristic: first line or look for name patterns
        lines = text.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if line and len(line.split()) <= 4 and not any(char.isdigit() for char in line):
                return line
        return None
    
    @staticmethod
    def _extract_email(text: str) -> Optional[str]:
        """Extract email from resume text."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group() if match else None
    
    @staticmethod
    def _extract_phone(text: str) -> Optional[str]:
        """Extract phone number from resume text."""
        phone_pattern = r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}'
        match = re.search(phone_pattern, text)
        return match.group() if match else None
    
    @staticmethod
    def _extract_skills(text: str) -> list:
        """Extract skills from resume text."""
        skills_keywords = [
            "skills", "technologies", "programming languages", "tools", "frameworks",
            "languages", "technical skills", "core competencies"
        ]
        
        skills = []
        lines = text.lower().split('\n')
        
        for i, line in enumerate(lines):
            if any(keyword in line for keyword in skills_keywords):
                # Get next few lines as potential skills
                for j in range(i+1, min(i+5, len(lines))):
                    skill_line = lines[j].strip()
                    if skill_line and not skill_line.startswith(('experience', 'education', 'projects')):
                        # Split by common delimiters
                        potential_skills = re.split(r'[,•\-\n]', skill_line)
                        skills.extend([s.strip() for s in potential_skills if s.strip()])
                    else:
                        break
                break
        
        # Clean and deduplicate
        skills = list(set([s for s in skills if len(s) > 2]))
        return skills[:20]  # Limit to top 20 skills
    
    @staticmethod
    def _extract_education(text: str) -> list:
        """Extract education from resume text."""
        education_keywords = ["education", "academic", "university", "college", "degree"]
        education = []
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in education_keywords):
                # Get next few lines
                for j in range(i, min(i+4, len(lines))):
                    if lines[j].strip():
                        education.append(lines[j].strip())
                break
        
        return education
    
    @staticmethod
    def _extract_experience(text: str) -> list:
        """Extract work experience from resume text."""
        experience_keywords = ["experience", "work history", "employment", "professional experience"]
        experience = []
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in experience_keywords):
                # Get next several lines
                for j in range(i+1, min(i+10, len(lines))):
                    if lines[j].strip():
                        experience.append(lines[j].strip())
                    elif len(experience) > 0:
                        break
                break
        
        return experience
    
    @staticmethod
    def _extract_projects(text: str) -> list:
        """Extract projects from resume text."""
        project_keywords = ["projects", "project experience", "key projects"]
        projects = []
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in project_keywords):
                # Get next several lines
                for j in range(i+1, min(i+10, len(lines))):
                    if lines[j].strip():
                        projects.append(lines[j].strip())
                    elif len(projects) > 0:
                        break
                break
        
        return projects
    
    @staticmethod
    def _extract_certifications(text: str) -> list:
        """Extract certifications from resume text."""
        cert_keywords = ["certification", "certified", "certificate", "credentials"]
        certifications = []
        
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in cert_keywords):
                # Get next several lines
                for j in range(i+1, min(i+8, len(lines))):
                    if lines[j].strip():
                        certifications.append(lines[j].strip())
                    elif len(certifications) > 0:
                        break
                break
        
        return certifications
