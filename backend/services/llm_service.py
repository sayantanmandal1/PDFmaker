"""
LLM service for AI-powered content generation and refinement using OpenAI API.
"""
import os
import time
from typing import Optional, List
from openai import OpenAI, RateLimitError, APIError, APIConnectionError
from dotenv import load_dotenv

load_dotenv()


class LLMService:
    """Service for handling LLM-based content generation and refinement."""
    
    def __init__(self):
        """Initialize the LLM service with OpenAI client (supports OpenRouter and Ollama)."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        # Support for OpenRouter, Ollama, or custom base URL
        base_url = os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
        # Allow custom model via environment variable (useful for OpenRouter/Ollama)
        self.model = os.getenv("OPENAI_MODEL", "qwen2.5:14b")
        self.max_retries = 3
        self.initial_retry_delay = 1  # seconds
    
    def _call_openai(
        self,
        prompt: str,
        system_message: str = "You are a helpful assistant that generates professional business document content.",
        max_tokens: int = 1000
    ) -> str:
        """
        Make an API call to OpenAI with retry logic and exponential backoff.
        
        Args:
            prompt: The user prompt to send to the LLM
            system_message: The system message to set context
            max_tokens: Maximum tokens in the response
            
        Returns:
            Generated text content from the LLM
            
        Raises:
            RateLimitError: If rate limit is exceeded after all retries
            APIError: If API error occurs after all retries
            APIConnectionError: If connection fails after all retries
        """
        retry_delay = self.initial_retry_delay
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.7
                )
                
                # Extract and return the generated content
                content = response.choices[0].message.content
                if content is None:
                    content = ""
                return content.strip()
                
            except RateLimitError as e:
                # Rate limit error - retry with exponential backoff
                if attempt < self.max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    # All retries exhausted
                    raise e
                    
            except (APIError, APIConnectionError) as e:
                # API or connection error - retry with exponential backoff
                if attempt < self.max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    # All retries exhausted
                    raise e
    
    def generate_section_content(
        self,
        topic: str,
        section_header: str,
        context: Optional[str] = None
    ) -> str:
        """
        Generate content for a Word document section.
        
        Args:
            topic: The main topic of the document
            section_header: The header/title of this specific section
            context: Optional additional context about the document
            
        Returns:
            Generated content for the section
            
        Raises:
            RateLimitError: If rate limit is exceeded
            APIError: If API error occurs
            APIConnectionError: If connection fails
        """
        # Build context-aware prompt
        prompt = f"""Generate professional content for a business document section.

Document Topic: {topic}
Section Header: {section_header}"""
        
        if context:
            prompt += f"\nAdditional Context: {context}"
        
        prompt += """

Please write 2-3 paragraphs of well-structured, professional content for this section. 
The content should be informative, clear, and appropriate for a business document.
Focus on providing valuable information related to the section header and main topic."""
        
        system_message = "You are a professional business writer creating high-quality document content."
        
        return self._call_openai(prompt, system_message, max_tokens=800)
    
    def generate_slide_content(
        self,
        topic: str,
        slide_title: str,
        context: Optional[str] = None
    ) -> str:
        """
        Generate content for a PowerPoint slide.
        
        Args:
            topic: The main topic of the presentation
            slide_title: The title of this specific slide
            context: Optional additional context about the presentation
            
        Returns:
            Generated content for the slide
            
        Raises:
            RateLimitError: If rate limit is exceeded
            APIError: If API error occurs
            APIConnectionError: If connection fails
        """
        # Build context-aware prompt
        prompt = f"""Generate professional content for a PowerPoint presentation slide.

Presentation Topic: {topic}
Slide Title: {slide_title}"""
        
        if context:
            prompt += f"\nAdditional Context: {context}"
        
        prompt += """

Please write concise, impactful bullet points or short paragraphs for this slide.
The content should be:
- Clear and easy to understand
- Suitable for visual presentation
- Professional and engaging
- Limited to 3-5 key points or 1-2 short paragraphs

Format the content appropriately for a slide presentation."""
        
        system_message = "You are a professional presentation designer creating engaging slide content."
        
        return self._call_openai(prompt, system_message, max_tokens=500)
    
    def refine_content(
        self,
        current_content: str,
        refinement_prompt: str
    ) -> str:
        """
        Refine existing content based on user instructions.
        
        Args:
            current_content: The current content to be refined
            refinement_prompt: User's instructions for refinement
            
        Returns:
            Refined content
            
        Raises:
            RateLimitError: If rate limit is exceeded
            APIError: If API error occurs
            APIConnectionError: If connection fails
        """
        prompt = f"""Please refine the following content based on the user's instructions.

Current Content:
{current_content}

Refinement Instructions:
{refinement_prompt}

Please provide the refined version of the content, incorporating the requested changes while maintaining professional quality and coherence."""
        
        system_message = "You are a professional editor helping to refine and improve document content."
        
        return self._call_openai(prompt, system_message, max_tokens=1000)
    
    def generate_template(
        self,
        topic: str,
        document_type: str
    ) -> List[str]:
        """
        Generate a document structure template (section headers or slide titles).
        
        Args:
            topic: The main topic for the document
            document_type: Either "word" or "powerpoint"
            
        Returns:
            List of section headers (for Word) or slide titles (for PowerPoint)
            
        Raises:
            RateLimitError: If rate limit is exceeded
            APIError: If API error occurs
            APIConnectionError: If connection fails
            ValueError: If document_type is invalid
        """
        if document_type not in ["word", "powerpoint"]:
            raise ValueError("document_type must be 'word' or 'powerpoint'")
        
        if document_type == "word":
            prompt = f"""Generate a professional outline for a Word document about: {topic}

Please provide 5-7 section headers that would create a comprehensive, well-structured document.
Return ONLY the section headers, one per line, without numbering or bullet points.
Make the headers clear, professional, and appropriate for a business document.

Example format:
Introduction
Background and Context
Key Findings
Recommendations
Conclusion"""
            
        else:  # powerpoint
            prompt = f"""Generate a professional outline for a PowerPoint presentation about: {topic}

Please provide 6-10 slide titles that would create a comprehensive, engaging presentation.
Return ONLY the slide titles, one per line, without numbering or bullet points.
Make the titles clear, concise, and appropriate for a business presentation.

Example format:
Introduction
Problem Statement
Current Situation
Proposed Solution
Implementation Plan
Expected Outcomes
Next Steps
Conclusion"""
        
        system_message = "You are a professional document strategist creating well-structured outlines."
        
        response = self._call_openai(prompt, system_message, max_tokens=500)
        
        # Parse the response into a list of headers/titles
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        # Filter out any lines that might be numbering or formatting
        headers = [line for line in lines if not line[0].isdigit() and line[0] != '-' and line[0] != '*']
        
        return headers if headers else lines  # Fallback to all lines if filtering removes everything
