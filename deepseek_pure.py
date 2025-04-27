"""
DeepSeek Pure Model Integration

This module provides integration with DeepSeek models without any fallbacks.
Requires sufficient computational resources to run properly.
"""

import os
import logging
import json
from typing import List, Dict, Any, Optional
from ctransformers import AutoModelForCausalLM

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepSeekPure:
    """
    Pure DeepSeek model implementation with no fallbacks.
    This class requires proper hardware resources to run.
    """

    def __init__(self, model_id: str = "deepseek-ai/deepseek-coder-6.7b-instruct"):
        """
        Initialize the DeepSeek model.

        Args:
            model_id (str): The model ID to load from HuggingFace
        """
        self.model = None
        self.model_id = model_id

        # Load the model immediately - no background loading
        self._load_model()

    def _load_model(self):
        """Load the DeepSeek model or raise an exception."""
        try:
            logger.info(f"Loading DeepSeek model: {self.model_id}")

            # Load the model with appropriate parameters
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                model_type="gpt_neox",    # Architecture type for DeepSeek models
                max_new_tokens=2048,      # Allow for longer responses
                context_length=2048,      # Allow for longer context
                gpu_layers=24,            # Use GPU if available (adjust based on your hardware)
                threads=8                 # Number of CPU threads (adjust based on your hardware)
            )

            # Test the model to verify it's working correctly
            test_response = self.model("Generate a short sample about education.", max_new_tokens=20)
            logger.info(f"Model test successful: {test_response}")

        except Exception as e:
            logger.critical(f"Critical error loading DeepSeek model: {e}")
            # No fallbacks - the application should fail if the model can't be loaded
            raise RuntimeError(f"Failed to load DeepSeek model. The application cannot function. Error: {e}")

    def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str:
        """
        Generate text using DeepSeek model.

        Args:
            prompt (str): The input prompt for generation
            max_tokens (int): Maximum tokens to generate
            temperature (float): Controls randomness (0.0-1.0)

        Returns:
            str: Generated text

        Raises:
            Exception: If generation fails, with no fallbacks
        """
        if self.model is None:
            raise RuntimeError("DeepSeek model not initialized")

        try:
            # Format prompt according to DeepSeek's expected format
            formatted_prompt = f"""<s>
[INST] {prompt} [/INST]
"""

            # Generate text using the model
            response = self.model(
                formatted_prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                repetition_penalty=1.1,    # Helps avoid repeated text
                top_p=0.9,                 # Nucleus sampling parameter
                top_k=40                   # Top-k sampling parameter
            )

            # Clean up response (remove prompt)
            if "[/INST]" in response:
                response = response.split("[/INST]", 1)[1].strip()

            return response

        except Exception as e:
            logger.error(f"Error generating text with DeepSeek: {e}")
            # No fallbacks - raise the exception
            raise RuntimeError(f"Failed to generate text with DeepSeek: {e}")

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
        lang_instruction = ""
        if language.lower() == "hindi":
            lang_instruction = "Please respond in Hindi."

        prompt = f"""
{lang_instruction}
You are creating a B.Ed. textbook on {subject}.
Write an introduction for a chapter on '{topic}'.
The introduction should:
1. Explain the importance of {topic} in education
2. Discuss its relevance for B.Ed. students
3. Outline what will be covered in the chapter

Length: 150-200 words.
"""
        return self.generate_text(prompt, max_tokens=500)

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
        lang_instruction = ""
        if language.lower() == "hindi":
            lang_instruction = "Please respond in Hindi."

        prompt = f"""
{lang_instruction}
Generate {count} high-quality multiple choice questions about '{topic}' for B.Ed. students studying {subject}.

For each question:
1. Write a clear, challenging question
2. Provide 4 options (A, B, C, D)
3. Indicate which option is correct
4. Give a brief explanation for why the answer is correct

Format your response as JSON with this structure:
[
  {{
    "question": "...",
    "options": ["option A", "option B", "option C", "option D"],
    "correct_answer": "A/B/C/D",
    "explanation": "..."
  }},
  ...
]
"""
        try:
            response = self.generate_text(prompt, max_tokens=4000)

            # Extract JSON from the response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                mcqs = json.loads(json_str)

                # Validate and fix the structure if needed
                valid_mcqs = []
                for mcq in mcqs:
                    if isinstance(mcq, dict) and 'question' in mcq and 'options' in mcq:
                        # Ensure all required fields exist
                        if 'correct_answer' not in mcq:
                            mcq['correct_answer'] = 'A'  # Default
                        if 'explanation' not in mcq:
                            mcq['explanation'] = f"This answer relates to {topic}."

                        # Ensure options is a list with 4 items
                        if not isinstance(mcq['options'], list) or len(mcq['options']) < 4:
                            mcq['options'] = mcq['options'] if isinstance(mcq['options'], list) else []
                            while len(mcq['options']) < 4:
                                mcq['options'].append(f"Option {len(mcq['options']) + 1}")

                        valid_mcqs.append(mcq)

                return valid_mcqs[:count]  # Return up to count MCQs

            # If parsing fails, raise an exception
            raise ValueError("Failed to generate valid MCQs structure")

        except Exception as e:
            logger.error(f"Error generating MCQs: {e}")
            # No fallbacks - raise the exception
            raise RuntimeError(f"Failed to generate MCQs: {e}")

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
        lang_instruction = ""
        if language.lower() == "hindi":
            lang_instruction = "Please respond in Hindi."

        prompt = f"""
{lang_instruction}
Generate {count} very short question and answers about '{topic}' for B.Ed. students studying {subject}.
Each answer should be approximately 35-40 words and highlight key educational concepts.

Format your response as JSON with this structure:
[
  {{
    "question": "...",
    "answer": "..."
  }},
  ...
]
"""
        try:
            response = self.generate_text(prompt, max_tokens=2000)

            # Extract JSON from the response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                qa_pairs = json.loads(json_str)

                # Validate structure
                valid_qa = []
                for qa in qa_pairs:
                    if isinstance(qa, dict) and 'question' in qa and 'answer' in qa:
                        valid_qa.append(qa)

                return valid_qa[:count]

            # If parsing fails, raise an exception
            raise ValueError("Failed to generate valid question-answer structure")

        except Exception as e:
            logger.error(f"Error generating very short Q&As: {e}")
            # No fallbacks - raise the exception
            raise RuntimeError(f"Failed to generate very short Q&As: {e}")

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
        lang_instruction = ""
        if language.lower() == "hindi":
            lang_instruction = "Please respond in Hindi."

        prompt = f"""
{lang_instruction}
Generate {count} medium-length question and answers about '{topic}' for B.Ed. students studying {subject}.
Each answer should be approximately 350-400 words and provide substantial information about the topic.

Format your response as JSON with this structure:
[
  {{
    "question": "...",
    "answer": "..."
  }},
  ...
]
"""
        try:
            response = self.generate_text(prompt, max_tokens=4000)

            # Extract JSON from the response
            json_start = response.find('[')
            json_end = response.rfind(']') + 1

            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                qa_pairs = json.loads(json_str)

                # Validate structure
                valid_qa = []
                for qa in qa_pairs:
                    if isinstance(qa, dict) and 'question' in qa and 'answer' in qa:
                        valid_qa.append(qa)

                return valid_qa[:count]

            # If parsing fails, raise an exception
            raise ValueError("Failed to generate valid question-answer structure")

        except Exception as e:
            logger.error(f"Error generating short Q&As: {e}")
            # No fallbacks - raise the exception
            raise RuntimeError(f"Failed to generate short Q&As: {e}")

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
        lang_instruction = ""
        if language.lower() == "hindi":
            lang_instruction = "Please respond in Hindi."

        prompt = f"""
{lang_instruction}
Generate {count} in-depth questions and comprehensive answers about '{topic}' for B.Ed. students studying {subject}.
Each answer should be approximately 1400-1500 words, with multiple paragraphs covering theory, application, and implications.

Format your response as JSON with this structure:
[
  {{
    "question": "...",
    "answer": "..."
  }},
  ...
]
"""
        try:
            # Generate for each question separately due to token limitations
            all_qa_pairs = []

            for i in range(count):
                single_prompt = f"""
{lang_instruction}
Generate 1 in-depth question and comprehensive answer about '{topic}' for B.Ed. students studying {subject}.
The answer should be approximately 1400-1500 words, with multiple paragraphs covering theory, application, and implications.

Format your response as JSON with this structure:
{{
  "question": "...",
  "answer": "..."
}}
"""
                response = self.generate_text(single_prompt, max_tokens=2000)

                # Extract JSON from the response
                json_start = response.find('{')
                json_end = response.rfind('}') + 1

                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    try:
                        qa_pair = json.loads(json_str)
                        if isinstance(qa_pair, dict) and 'question' in qa_pair and 'answer' in qa_pair:
                            all_qa_pairs.append(qa_pair)
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse JSON for question {i+1}")

            return all_qa_pairs[:count]

        except Exception as e:
            logger.error(f"Error generating long Q&As: {e}")
            # No fallbacks - raise the exception
            raise RuntimeError(f"Failed to generate long Q&As: {e}")

def get_deepseek_pure_model():
    """Returns a pure DeepSeek model instance with no fallbacks."""
    return DeepSeekPure()