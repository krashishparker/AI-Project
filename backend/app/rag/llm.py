from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from app.core.config import settings


class LLMService:
    """Service for LLM operations using Ollama."""
    
    def __init__(self):
        self.llm = Ollama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_LLM_MODEL,
            temperature=0.1  # Low temperature for more factual responses
        )
        
        # System prompt
        self.system_prompt = """You are an AI assistant that answers questions about resumes. 
Your role is to provide accurate information based ONLY on the resume content provided.

IMPORTANT RULES:
1. Answer questions using ONLY the information from the provided resume context.
2. If the information is not available in the resume, clearly state: "The uploaded resume does not contain this information."
3. Do not make up, hallucinate, or infer information that is not explicitly stated in the resume.
4. Be concise and direct in your answers.
5. If you're unsure about something, admit it rather than guessing.
6. Provide specific details from the resume when available (e.g., exact years, specific technologies, project names).
7. Maintain a professional and helpful tone."""
        
        # RAG prompt template
        self.rag_prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""{system_prompt}

CONTEXT FROM RESUME:
{context}

QUESTION: {question}

ANSWER:"""
        )
    
    def generate_response(self, context: str, question: str) -> str:
        """Generate a response using RAG."""
        # Format the prompt
        prompt = self.rag_prompt_template.format(
            system_prompt=self.system_prompt,
            context=context,
            question=question
        )
        
        # Generate response
        response = self.llm.invoke(prompt)
        
        return response
    
    def generate_response_with_chain(self, context: str, question: str) -> str:
        """Generate response using LangChain chain."""
        chain = LLMChain(
            llm=self.llm,
            prompt=self.rag_prompt_template
        )
        
        response = chain.invoke({
            "system_prompt": self.system_prompt,
            "context": context,
            "question": question
        })
        
        return response["text"]
