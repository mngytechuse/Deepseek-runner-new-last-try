"""
DeepSeek V3 API Integration Module

This module provides the integration with DeepSeek V3 API for educational content generation.
"""

import os
import json
import logging
import requests
from typing import Dict, List, Union, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepSeekV3:
    """
    DeepSeek V3 API client for educational content generation.
    
    This class handles requests to the DeepSeek V3 API for generating educational content.
    It provides methods for generating various types of educational content such as
    introductions, subtopics, question-answers, etc.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the DeepSeek V3 API client.
        
        Args:
            api_key (str, optional): The API key for DeepSeek V3. If not provided,
                                    it will look for DEEPSEEK_API_KEY in environment variables.
        """
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        
        if not self.api_key:
            logger.warning("No DeepSeek API key provided. API calls will fail.")
    
    def generate(self, 
                 prompt: str, 
                 max_tokens: int = 1000, 
                 temperature: float = 0.7) -> str:
        """
        Generate text using DeepSeek V3 API.
        
        Args:
            prompt (str): The input prompt for generation
            max_tokens (int): Maximum tokens to generate
            temperature (float): Controls randomness (0.0-1.0)
            
        Returns:
            str: Generated text
        
        Raises:
            Exception: If the API request fails
        """
        # Prepare the request payload
        payload = {
            "model": "deepseek-v3",
            "messages": [
                {"role": "system", "content": "You are an expert educational content generator for B.Ed. students in India. You create high-quality, informative content related to educational topics."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        response = None
        try:
            # Make the API request
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload
            )
            
            # Check for successful response
            response.raise_for_status()
            
            # Parse and return the generated text
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error occurred: {e}")
            if response and response.status_code == 401:
                logger.error("Authentication error. Check your API key.")
            elif response and response.status_code == 429:
                logger.error("Rate limit exceeded. Please try again later.")
            raise Exception(f"DeepSeek API request failed: {str(e)}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error occurred: {e}")
            raise Exception(f"DeepSeek API request failed: {str(e)}")
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise Exception(f"DeepSeek API request failed: {str(e)}")
    
    def generate_introduction(self, topic: str, subject: str, language: str = "english") -> str:
        """
        Generate an introduction for a chapter.
        
        Args:
            topic (str): The topic/chapter title
            subject (str): The subject of the book
            language (str): The language for content generation
            
        Returns:
            str: Generated introduction
        """
        prompt = f"""
        Generate an introduction for a chapter on '{topic}' for a B.Ed. textbook on {subject}.
        The introduction should explain the importance of the topic in education,
        its relevance for B.Ed. students, and briefly outline what will be covered in the chapter.
        Length: Approximately 150-200 words.
        Language: {language}
        """
        
        return self.generate(prompt, max_tokens=300)
    
    def generate_subtopics(self, topic: str, subject: str, language: str = "english") -> List[Dict[str, str]]:
        """
        Generate subtopics for a chapter with detailed content.
        
        Args:
            topic (str): The topic/chapter title
            subject (str): The subject of the book
            language (str): The language for content generation
            
        Returns:
            List[Dict[str, str]]: List of subtopics with title and content
        """
        prompt = f"""
        Generate 3-5 subtopics for a chapter on '{topic}' in a B.Ed. textbook about {subject}.
        For each subtopic, provide:
        1. A clear, descriptive title
        2. Detailed content (400-600 words) explaining the subtopic in the context of {subject} education
        
        Format your response as JSON with the following structure:
        [
            {{
                "title": "Subtopic Title 1",
                "content": "Subtopic content..."
            }},
            ...
        ]
        
        Language: {language}
        """
        
        try:
            result = self.generate(prompt, max_tokens=2000)
            # Parse the JSON response
            return json.loads(result)
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from API response")
            # Fallback
            return [
                {
                    "title": f"Key Aspects of {topic}",
                    "content": f"This section explores the fundamental aspects of {topic} in the context of {subject} education..."
                },
                {
                    "title": f"Implementing {topic} in Classrooms",
                    "content": f"This section discusses practical approaches to implementing {topic} in educational settings..."
                },
                {
                    "title": f"{topic} in Indian Educational Context",
                    "content": f"This section examines how {topic} is relevant in the Indian educational landscape..."
                }
            ]
    
    def generate_examples(self, topic: str, subject: str, language: str = "english") -> str:
        """
        Generate practical examples for a chapter.
        
        Args:
            topic (str): The topic/chapter title
            subject (str): The subject of the book
            language (str): The language for content generation
            
        Returns:
            str: Generated examples
        """
        prompt = f"""
        Generate 3-5 practical examples demonstrating the application of '{topic}' in {subject} education.
        Each example should be relevant for B.Ed. students in India and include:
        1. A practical classroom scenario or case study
        2. How the concept is applied
        3. Expected outcomes or benefits
        
        Format as a list with clear headings and brief descriptions.
        Language: {language}
        """
        
        return self.generate(prompt, max_tokens=800)
    
    def generate_summary(self, topic: str, subject: str, language: str = "english") -> str:
        """
        Generate a chapter summary.
        
        Args:
            topic (str): The topic/chapter title
            subject (str): The subject of the book
            language (str): The language for content generation
            
        Returns:
            str: Generated summary
        """
        prompt = f"""
        Generate a comprehensive summary for a chapter on '{topic}' in a B.Ed. textbook about {subject}.
        The summary should:
        1. Recap the key points covered in the chapter
        2. Emphasize the importance of the topic for teaching practice
        3. Connect the topic to broader educational principles
        
        Length: Approximately 200-250 words.
        Language: {language}
        """
        
        return self.generate(prompt, max_tokens=400)
    
    def generate_mcqs(self, topic: str, subject: str, language: str = "english", count: int = 20) -> List[Dict]:
        """
        Generate multiple choice questions.
        
        Args:
            topic (str): The topic/chapter title
            subject (str): The subject of the book
            language (str): The language for content generation
            count (int): Number of MCQs to generate
            
        Returns:
            List[Dict]: List of MCQs with question, options, correct answer, and explanation
        """
        prompt = f"""
        Generate {count} multiple-choice questions (MCQs) for assessing understanding of '{topic}' in {subject} education.
        Each MCQ should:
        1. Have a clear question
        2. Include 4 options (labeled A, B, C, D)
        3. Indicate the correct answer
        4. Provide a brief explanation for why the answer is correct
        
        Format your response as JSON with the following structure:
        [
            {{
                "question": "Question text",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_index": 0,
                "explanation": "Explanation for correct answer"
            }},
            ...
        ]
        
        Language: {language}
        """
        
        try:
            result = self.generate(prompt, max_tokens=3000)
            # Parse the JSON response
            return json.loads(result)
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from API response for MCQs")
            # Return a minimal placeholder to prevent application failure
            return [
                {
                    "question": f"Which of the following best describes {topic}?",
                    "options": [
                        f"{topic} is a fundamental concept in {subject} education",
                        f"{topic} is only relevant for primary education",
                        f"{topic} was developed in the 20th century",
                        f"{topic} cannot be applied in Indian educational context"
                    ],
                    "correct_index": 0,
                    "explanation": f"{topic} is indeed a fundamental concept in {subject} education as it forms the basis for effective teaching and learning practices."
                }
            ]
    
    def generate_very_short_qa(self, topic: str, subject: str, language: str = "english", count: int = 10) -> List[Dict]:
        """
        Generate very short question and answers (35-40 words).
        
        Args:
            topic (str): The topic/chapter title
            subject (str): The subject of the book
            language (str): The language for content generation
            count (int): Number of questions to generate
            
        Returns:
            List[Dict]: List of question-answer pairs
        """
        prompt = f"""
        Generate {count} very short question and answer pairs about '{topic}' for a B.Ed. textbook on {subject}.
        Each answer should be approximately 35-40 words long.
        Questions should cover key concepts, applications, and implications of the topic.
        
        Format your response as JSON with the following structure:
        [
            {{
                "question": "Question text",
                "answer": "Short answer (35-40 words)"
            }},
            ...
        ]
        
        Language: {language}
        """
        
        try:
            result = self.generate(prompt, max_tokens=2000)
            # Parse the JSON response
            return json.loads(result)
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from API response for very short QA")
            # Return minimal placeholder
            return [
                {
                    "question": f"What is the importance of {topic} in {subject} education?",
                    "answer": f"{topic} provides essential frameworks for effective teaching in {subject}. It helps B.Ed. students develop structured approaches to classroom instruction and student assessment."
                }
            ]
    
    def generate_short_qa(self, topic: str, subject: str, language: str = "english", count: int = 5) -> List[Dict]:
        """
        Generate short question and answers (350-400 words).
        
        Args:
            topic (str): The topic/chapter title
            subject (str): The subject of the book
            language (str): The language for content generation
            count (int): Number of questions to generate
            
        Returns:
            List[Dict]: List of question-answer pairs
        """
        prompt = f"""
        Generate {count} short question and answer pairs about '{topic}' for a B.Ed. textbook on {subject}.
        Each answer should be approximately 350-400 words long.
        Questions should require explanation, analysis, or application of concepts related to the topic.
        
        Format your response as JSON with the following structure:
        [
            {{
                "question": "Question text",
                "answer": "Short answer (350-400 words)"
            }},
            ...
        ]
        
        Language: {language}
        """
        
        try:
            result = self.generate(prompt, max_tokens=3000)
            # Parse the JSON response
            return json.loads(result)
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from API response for short QA")
            # Return minimal placeholder
            return [
                {
                    "question": f"Explain how {topic} can be implemented in {subject} classrooms.",
                    "answer": f"The implementation of {topic} in {subject} classrooms involves several key strategies and approaches. First, teachers must understand the theoretical underpinnings of {topic} and how it relates to student learning in {subject}. This includes recognizing that effective implementation requires careful planning and adaptation to specific classroom contexts.\n\nSecond, educators should develop clear learning objectives aligned with {topic} principles. These objectives guide the selection of appropriate teaching methods and assessment strategies. For example, when teaching {subject} through the lens of {topic}, educators might employ collaborative learning activities, hands-on demonstrations, or technology-enhanced instruction.\n\nThird, assessment methods should align with {topic} approaches. This might include formative assessments throughout the learning process as well as summative evaluations that measure student achievement of learning objectives. The assessment data can inform future instructional decisions and adaptations.\n\nFinally, successful implementation requires ongoing professional development and reflection. B.Ed. students should be encouraged to continuously evaluate their teaching practices, seek feedback, and make necessary adjustments to better serve their students' learning needs."
                }
            ]
    
    def generate_long_qa(self, topic: str, subject: str, language: str = "english", count: int = 4) -> List[Dict]:
        """
        Generate long question and answers (1400-1500 words).
        
        Args:
            topic (str): The topic/chapter title
            subject (str): The subject of the book
            language (str): The language for content generation
            count (int): Number of questions to generate
            
        Returns:
            List[Dict]: List of question-answer pairs
        """
        prompt = f"""
        Generate {count} comprehensive question and answer pairs about '{topic}' for a B.Ed. textbook on {subject}.
        Each answer should be approximately 1400-1500 words long.
        Questions should require in-depth analysis, critical evaluation, or detailed discussion of the topic.
        Include relevant theories, research, practical applications, and connections to the Indian educational context.
        
        Format your response as JSON with the following structure:
        [
            {{
                "question": "Question text",
                "answer": "Long answer (1400-1500 words)"
            }},
            ...
        ]
        
        Language: {language}
        """
        
        try:
            # For long answers, generate one at a time to avoid token limits
            all_qa_pairs = []
            for i in range(count):
                single_prompt = f"""
                Generate 1 comprehensive question and answer pair about '{topic}' for a B.Ed. textbook on {subject}.
                The answer should be approximately 1400-1500 words long.
                The question should require in-depth analysis, critical evaluation, or detailed discussion of the topic.
                Include relevant theories, research, practical applications, and connections to the Indian educational context.
                
                Format your response as JSON with the following structure:
                {{
                    "question": "Question text",
                    "answer": "Long answer (1400-1500 words)"
                }}
                
                Language: {language}
                """
                
                result = self.generate(single_prompt, max_tokens=2000)
                try:
                    qa_pair = json.loads(result)
                    all_qa_pairs.append(qa_pair)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON from API response for long QA pair {i+1}")
            
            return all_qa_pairs
            
        except Exception as e:
            logger.error(f"Error generating long QA pairs: {e}")
            # Return minimal placeholder
            return [
                {
                    "question": f"Critically analyze the role of {topic} in {subject} education in the Indian context.",
                    "answer": f"The role of {topic} in {subject} education in India is multifaceted and deeply influential... [This would be a 1400-1500 word response in an actual implementation]"
                }
            ]
    
    def generate_references(self, topic: str, subject: str) -> List[str]:
        """
        Generate academic references in APA format.
        
        Args:
            topic (str): The topic/chapter title
            subject (str): The subject of the book
            
        Returns:
            List[str]: List of references in APA format
        """
        prompt = f"""
        Generate 7-10 academic references in APA format for a chapter on '{topic}' in a B.Ed. textbook about {subject}.
        Include a mix of:
        - Recent research articles (within the last 5 years)
        - Classic works in the field
        - Books and textbooks
        - Government documents (e.g., National Education Policy)
        - Publications from educational bodies in India (e.g., NCERT)
        
        Format each reference according to the APA 7th edition guidelines.
        """
        
        result = self.generate(prompt, max_tokens=800)
        
        # Process the result to get a list of references
        references = [ref.strip() for ref in result.split('\n') if ref.strip()]
        
        # Filter out any lines that don't look like references
        references = [ref for ref in references if '(' in ref and ')' in ref]
        
        return references


# Get DeepSeek V3 client instance
def get_deepseek_client():
    """
    Returns a DeepSeek V3 client instance.
    
    Returns:
        DeepSeekV3: An instance of the DeepSeek V3 client
    """
    return DeepSeekV3()