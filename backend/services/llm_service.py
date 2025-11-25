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
        prompt = f"""Generate comprehensive, detailed content for a Word document section.

Document Topic: {topic}
Section Header: {section_header}"""
        
        if context:
            prompt += f"\nAdditional Context: {context}"
        
        prompt += """

Please write 3-5 well-developed paragraphs of professional content for this section.
The content should be:
- Detailed and informative with substantial depth
- Written in complete, flowing paragraphs (not bullet points)
- Professional and appropriate for a formal business document
- Rich in information and analysis
- Between 300-500 words to provide thorough coverage

Focus on providing comprehensive information, explanations, and insights related to the section header and main topic.
Write in a narrative style suitable for reading in a Word document."""
        
        system_message = "You are a professional business writer creating comprehensive, detailed document content for Word documents. Write in full paragraphs with substantial depth and detail."
        
        return self._call_openai(prompt, system_message, max_tokens=1200)
    
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
        prompt = f"""Generate concise, impactful content for a PowerPoint presentation slide.

Presentation Topic: {topic}
Slide Title: {slide_title}"""
        
        if context:
            prompt += f"\nAdditional Context: {context}"
        
        prompt += """

Please write concise, punchy bullet points for this slide.
The content should be:
- Brief and scannable (3-6 bullet points)
- Each bullet point should be 1-2 short sentences maximum
- Clear, impactful, and easy to read at a glance
- Suitable for visual presentation on a slide
- Professional and engaging
- Total content should be 50-100 words maximum

Format as bullet points, each on a new line.
Remember: slides are visual aids, not documents. Keep it concise!"""
        
        system_message = "You are a professional presentation designer creating concise, impactful slide content. Keep bullet points short and scannable - slides are visual aids, not documents."
        
        return self._call_openai(prompt, system_message, max_tokens=300)
    
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
    
    def determine_image_need(self, content: str) -> bool:
        """
        Determine if the given content would benefit from images.
        
        Args:
            content: The content to analyze (section text or slide content)
            
        Returns:
            True if images would enhance the content, False otherwise
            
        Raises:
            RateLimitError: If rate limit is exceeded
            APIError: If API error occurs
            APIConnectionError: If connection fails
        """
        prompt = f"""Analyze the following content and determine if it would benefit from images.

Content:
{content}

Consider:
- Would images make this content more engaging or easier to understand?
- Is the content visual in nature (describing objects, places, processes, data)?
- Would images add value beyond the text?

Respond with ONLY "YES" or "NO" - nothing else."""
        
        system_message = "You are a professional document designer analyzing whether content needs images. Respond with only YES or NO."
        
        response = self._call_openai(prompt, system_message, max_tokens=10)
        
        # Parse the response - look for YES/NO
        response_upper = response.upper().strip()
        return "YES" in response_upper
    
    def generate_image_search_query(self, content: str) -> str:
        """
        Generate an effective image search query based on content.
        
        Args:
            content: The content to generate a search query for
            
        Returns:
            A concise, effective search query string
            
        Raises:
            RateLimitError: If rate limit is exceeded
            APIError: If API error occurs
            APIConnectionError: If connection fails
        """
        prompt = f"""Generate a concise image search query for the following content.

Content:
{content}

Requirements:
- MAXIMUM 5 words
- Focus on the main visual concept
- Use simple, descriptive keywords
- Professional and appropriate

Examples:
- "Eiffel Tower Paris"
- "business team meeting"
- "mountain landscape sunset"

Respond with ONLY the search query (2-5 words) - nothing else."""
        
        system_message = "You are a professional image researcher. Create a short search query of 2-5 words maximum. Respond with only the query."
        
        response = self._call_openai(prompt, system_message, max_tokens=20)
        
        # Clean up the response and ensure it's concise
        query = response.strip()
        words = query.split()
        
        # If response is too long, take first 5 words
        if len(words) > 5:
            query = ' '.join(words[:5])
        
        return query
    
    def determine_slide_layout(self, content: str, has_image: bool) -> str:
        """
        Determine the optimal slide layout based on content and image presence.
        
        Args:
            content: The slide content
            has_image: Whether an image will be included
            
        Returns:
            Layout name: "title_slide", "title_and_content", "two_content", 
                        "content_with_caption", or "blank"
            
        Raises:
            RateLimitError: If rate limit is exceeded
            APIError: If API error occurs
            APIConnectionError: If connection fails
        """
        prompt = f"""Determine the optimal PowerPoint slide layout for the following content.

Content:
{content}

Has Image: {"Yes" if has_image else "No"}

Available layouts:
- title_slide: For introductions and section breaks (minimal content, large title)
- title_and_content: Standard layout for most slides (title + bullet points)
- two_content: For comparisons or parallel concepts (two columns)
- content_with_caption: For image-heavy slides (large image with caption)
- blank: For custom layouts with background images (no predefined structure)

Consider:
- Amount of text content
- Whether an image is present
- Content structure (single topic vs comparison)
- Visual balance

Respond with ONLY the layout name - nothing else."""
        
        system_message = "You are a professional presentation designer selecting optimal slide layouts. Respond with only the layout name."
        
        response = self._call_openai(prompt, system_message, max_tokens=20)
        
        # Parse and validate the response
        response_lower = response.strip().lower()
        valid_layouts = ["title_slide", "title_and_content", "two_content", "content_with_caption", "blank"]
        
        for layout in valid_layouts:
            if layout in response_lower:
                return layout
        
        # Default fallback
        return "title_and_content"
    
    def determine_image_placement(self, content: str, doc_type: str) -> str:
        """
        Determine whether an image should be placed in the background or foreground.
        
        Args:
            content: The content that will accompany the image
            doc_type: Either "word" or "powerpoint"
            
        Returns:
            Placement strategy: "background", "foreground", "inline", or "wrapped"
            
        Raises:
            RateLimitError: If rate limit is exceeded
            APIError: If API error occurs
            APIConnectionError: If connection fails
            ValueError: If doc_type is invalid
        """
        if doc_type not in ["word", "powerpoint"]:
            raise ValueError("doc_type must be 'word' or 'powerpoint'")
        
        if doc_type == "powerpoint":
            prompt = f"""Determine the optimal image placement for a PowerPoint slide.

Content:
{content}

Placement options:
- background: Image behind all content with transparency (for inspirational/atmospheric images)
- foreground: Image positioned in content area alongside text (for specific objects/diagrams)

Consider:
- Content density (heavy text = foreground; light text = background)
- Content type (data/facts = foreground; inspirational = background)
- Image purpose (illustrative = foreground; atmospheric = background)

Respond with ONLY "background" or "foreground" - nothing else."""
            
        else:  # word
            prompt = f"""Determine the optimal image placement for a Word document.

Content:
{content}

Placement options:
- inline: Image embedded directly in text flow (breaks text)
- wrapped: Image with text wrapping around it (text flows around image)

Consider:
- Content flow and readability
- Image relevance to surrounding text
- Document structure

Respond with ONLY "inline" or "wrapped" - nothing else."""
        
        system_message = "You are a professional document designer determining optimal image placement. Respond with only the placement option."
        
        response = self._call_openai(prompt, system_message, max_tokens=10)
        
        # Parse and validate the response
        response_lower = response.strip().lower()
        
        if doc_type == "powerpoint":
            if "background" in response_lower:
                return "background"
            else:
                return "foreground"
        else:  # word
            if "wrapped" in response_lower:
                return "wrapped"
            else:
                return "inline"
