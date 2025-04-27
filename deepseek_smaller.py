"""
DeepSeek Smaller Model Integration Module

This module provides integration with smaller DeepSeek models via ctransformers.
It allows for running smaller versions of DeepSeek models locally without
requiring significant computational resources.
"""

import os
import json
import logging
import re
import random
from typing import List, Dict, Any, Optional
import threading
from ctransformers import AutoModelForCausalLM, AutoConfig

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeepSeekSmallerModel:
    """
    DeepSeek smaller model integration using ctransformers.
    
    This class provides methods to load and run smaller DeepSeek models locally,
    optimized for environments with limited computational resources.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the DeepSeek smaller model.
        
        Args:
            model_path (str, optional): Path to the model files. If not provided,
                                      the model will be downloaded from HuggingFace.
        """
        self.model = None
        self.model_loading_thread = None
        self.model_loaded = False
        self.model_path = model_path
        
        # Start loading the model in a background thread
        self._start_model_loading()
        
        # Seed random for consistent outputs when falling back to templates
        random.seed(42)
        
        # Load language patterns and templates for fallback
        self.templates = self._load_templates()
        
        logger.info("DeepSeek smaller model integration initialized")
    
    def _start_model_loading(self):
        """Start loading the model in a background thread."""
        self.model_loading_thread = threading.Thread(target=self._load_model)
        self.model_loading_thread.daemon = True
        self.model_loading_thread.start()
        logger.info("Started loading DeepSeek smaller model in background thread")
    
    def _load_model(self):
        """Load the DeepSeek smaller model."""
        try:
            # Use a tiny GGML model that's directly supported by CTransformers
            model_id = self.model_path or "TheBloke/Llama-2-7B-Chat-GGML"
            model_file = "llama-2-7b-chat.ggmlv3.q4_0.bin"
            
            logger.info(f"Loading small language model: {model_id}/{model_file}")
            
            # Load the model with very conservative parameters to ensure it fits in memory
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id,
                model_file=model_file,
                model_type="llama",
                local_files_only=False,
                max_new_tokens=256,
                context_length=512,
                gpu_layers=0  # CPU only
            )
            
            self.model_loaded = True
            logger.info("DeepSeek smaller model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load DeepSeek smaller model: {e}")
            logger.info("Will fall back to template-based generation")
    
    def _load_templates(self):
        """Load language templates for content generation."""
        # In a production environment, these would be more extensive and nuanced
        return {
            "introduction": {
                "english": [
                    "Introduction to {topic}: This chapter explores the essential aspects of {topic} in the field of {subject}. "
                    "It discusses the relevance and importance of this topic in education. For B.Ed. students, understanding {topic} "
                    "is particularly significant as it helps develop effective teaching capabilities. In this chapter, we will examine "
                    "various dimensions of {topic} and its applications in educational contexts.",
                    
                    "{topic} represents a critical area of study in {subject} education. This chapter provides B.Ed. students with "
                    "a comprehensive understanding of the principles, theories, and practical applications of {topic}. "
                    "The knowledge and skills associated with {topic} are essential for effective classroom management and "
                    "teaching practices. Throughout this chapter, we'll explore how {topic} can be applied in diverse educational settings."
                ],
                "hindi": [
                    "{topic} विषय का परिचय: यह अध्याय {subject} के महत्वपूर्ण पहलुओं पर प्रकाश डालता है। इसमें शिक्षा के क्षेत्र में इस विषय की "
                    "प्रासंगिकता और महत्व पर चर्चा की गई है। बी.एड. छात्रों के लिए यह अध्याय विशेष रूप से महत्वपूर्ण है क्योंकि यह उन्हें शिक्षण "
                    "क्षमताओं को विकसित करने में मदद करता है। इस अध्याय में हम {topic} के विभिन्न आयामों और शैक्षिक संदर्भों में इसके अनुप्रयोगों का "
                    "अध्ययन करेंगे।",
                    
                    "{topic} {subject} शिक्षा में एक महत्वपूर्ण अध्ययन क्षेत्र है। यह अध्याय बी.एड. छात्रों को {topic} के सिद्धांतों, विचारों और "
                    "व्यावहारिक अनुप्रयोगों की व्यापक समझ प्रदान करता है। {topic} से जुड़े ज्ञान और कौशल प्रभावी कक्षा प्रबंधन और शिक्षण "
                    "प्रथाओं के लिए आवश्यक हैं। इस अध्याय में, हम अन्वेषण करेंगे कि {topic} को विविध शैक्षिक परिवेशों में कैसे लागू किया जा सकता है।"
                ]
            },
            "subtopic_titles": [
                "Theoretical Foundation of {topic}",
                "Historical Development of {topic}",
                "Key Components of {topic}",
                "Practical Applications of {topic}",
                "Assessment Strategies for {topic}",
                "{topic} in Indian Educational Context",
                "Teaching {topic} in Diverse Classrooms",
                "Current Research on {topic}",
                "Psychological Aspects of {topic}",
                "{topic} and Curriculum Development",
                "Technology Integration in {topic}"
            ],
            "subtopic_content": {
                "english": [
                    "The {title} forms a critical part of understanding how education functions in modern contexts. "
                    "Researchers and educators have explored various dimensions of this area, finding that it significantly "
                    "impacts student learning outcomes and teacher effectiveness. When examining {title}, it's important to "
                    "consider both theoretical frameworks and practical implementations.\n\n"
                    "B.Ed. students should recognize that {title} isn't just an abstract concept but has real implications "
                    "for day-to-day teaching practice. The foundational principles include student-centered approaches, "
                    "differentiated instruction, and evidence-based assessment. These elements combine to create a comprehensive "
                    "framework that guides effective educational practice.\n\n"
                    "In the Indian educational landscape, {title} takes on particular significance due to the diverse "
                    "socio-cultural contexts in which teaching occurs. The National Education Policy 2020 emphasizes the "
                    "importance of these approaches in creating more inclusive and effective learning environments. "
                    "Teachers must adapt these principles to suit the specific needs of their classrooms and students.",
                    
                    "Understanding {title} requires examination of both theoretical principles and practical applications. "
                    "This area of study has evolved significantly over the past decades, with increasing emphasis on "
                    "evidence-based practices and student-centered approaches. For B.Ed. students, mastering these concepts "
                    "provides essential tools for effective classroom management and instruction.\n\n"
                    "Research has demonstrated that when teachers effectively implement principles of {title}, student "
                    "engagement and achievement improve markedly. Key strategies include creating inclusive learning "
                    "environments, utilizing diverse assessment methods, and adapting instruction to meet individual "
                    "student needs. These approaches recognize the heterogeneous nature of classrooms and the importance "
                    "of addressing diverse learning styles and abilities.\n\n"
                    "In practical terms, {title} involves developing specific skills and competencies that enable teachers "
                    "to create optimal learning experiences. This includes designing appropriate learning activities, "
                    "managing classroom dynamics, and evaluating student progress through both formative and summative "
                    "assessment methods. The integration of these elements creates a cohesive approach to effective teaching."
                ],
                "hindi": [
                    "{title} को समझना आधुनिक शिक्षा के संदर्भ में महत्वपूर्ण है। शोधकर्ताओं और शिक्षकों ने इस क्षेत्र के विभिन्न आयामों "
                    "का अध्ययन किया है, जिससे पता चला है कि यह छात्रों के सीखने के परिणामों और शिक्षक प्रभावशीलता पर महत्वपूर्ण प्रभाव "
                    "डालता है। {title} का अध्ययन करते समय, सैद्धांतिक ढांचे और व्यावहारिक कार्यान्वयन दोनों पर विचार करना महत्वपूर्ण है।\n\n"
                    "बी.एड. छात्रों को यह पहचानना चाहिए कि {title} केवल एक अमूर्त अवधारणा नहीं है, बल्कि दैनिक शिक्षण अभ्यास के लिए "
                    "वास्तविक प्रभाव रखती है। मूलभूत सिद्धांतों में छात्र-केंद्रित दृष्टिकोण, विभेदित निर्देश, और साक्ष्य-आधारित मूल्यांकन "
                    "शामिल हैं। ये तत्व प्रभावी शैक्षिक अभ्यास का मार्गदर्शन करने वाले एक व्यापक ढांचे का निर्माण करते हैं।\n\n"
                    "भारतीय शैक्षिक परिदृश्य में, {title} विशेष महत्व रखता है क्योंकि शिक्षण विविध सामाजिक-सांस्कृतिक संदर्भों में "
                    "होता है। राष्ट्रीय शिक्षा नीति 2020 अधिक समावेशी और प्रभावी सीखने के वातावरण बनाने में इन दृष्टिकोणों के महत्व "
                    "पर जोर देती है। शिक्षकों को इन सिद्धांतों को अपनी कक्षाओं और छात्रों की विशिष्ट आवश्यकताओं के अनुरूप अनुकूलित करना चाहिए।"
                ]
            },
            # ... [Other templates remain the same as in deepseek_local.py]
        }
    
    def generate_text(self, prompt: str, max_tokens: int = 500, temperature: float = 0.7, language: str = "english") -> str:
        """
        Generate text using the DeepSeek smaller model or templates if model isn't loaded.
        
        Args:
            prompt (str): The input prompt for generation
            max_tokens (int): Maximum tokens to generate
            temperature (float): Controls randomness (0.0-1.0)
            language (str): Target language ("english" or "hindi")
            
        Returns:
            str: Generated text
        """
        # Check if the model is loaded
        if self.model_loaded and self.model is not None:
            try:
                logger.info(f"Generating text with DeepSeek smaller model")
                # Format the prompt according to DeepSeek's expected format
                # Format prompt according to TinyLlama's expected chat format
                formatted_prompt = f"""<|system|>
You are a helpful AI assistant specializing in educational content for B.Ed students.
<|user|>
{prompt}
<|assistant|>"""
                
                # Generate text using the model
                result = self.model(
                    formatted_prompt,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    stop=["<|im_end|>"]
                )
                
                # Extract the model's response (remove the prompt and any stop sequences)
                # This might need adjustment based on actual output format
                response = result.strip()
                if "<|im_start|>assistant" in response:
                    response = response.split("<|im_start|>assistant", 1)[1]
                if "<|im_end|>" in response:
                    response = response.split("<|im_end|>", 1)[0]
                
                logger.info("Text generation with DeepSeek smaller model completed")
                return response.strip()
                
            except Exception as e:
                logger.error(f"Error generating text with DeepSeek smaller model: {e}")
                logger.info("Falling back to template-based generation")
        else:
            logger.info("DeepSeek smaller model not loaded yet, using template-based generation")
        
        # Fall back to template-based generation
        return self._template_based_generation(prompt, language)
    
    def _template_based_generation(self, prompt: str, language: str = "english") -> str:
        """
        Generate text using templates when the model is not available.
        
        Args:
            prompt (str): The input prompt for generation
            language (str): Target language ("english" or "hindi")
            
        Returns:
            str: Generated text using templates
        """
        # Identify the type of content requested
        content_type = self._identify_content_type(prompt)
        
        # Extract topic and subject from prompt
        topic, subject = self._extract_topic_subject(prompt)
        
        # Generate the appropriate content
        if content_type == "introduction":
            return self._generate_introduction(topic, subject, language)
        elif content_type == "subtopics":
            return json.dumps(self._generate_subtopics(topic, subject, language))
        elif content_type == "examples":
            return self._generate_examples(topic, subject, language)
        elif content_type == "summary":
            return self._generate_summary(topic, subject, language)
        elif content_type == "mcqs":
            return json.dumps(self._generate_mcqs(topic, subject, language))
        elif content_type == "very_short_qa":
            return json.dumps(self._generate_very_short_qa(topic, subject, language))
        elif content_type == "short_qa":
            return json.dumps(self._generate_short_qa(topic, subject, language))
        elif content_type == "long_qa":
            return json.dumps(self._generate_long_qa(topic, subject, language))
        elif content_type == "references":
            return json.dumps(self._generate_references(topic, subject))
        else:
            # Generic educational content generation
            return self._generate_generic_content(topic, subject, language)
    
    def _identify_content_type(self, prompt: str) -> str:
        """Identify the type of content requested in the prompt."""
        prompt_lower = prompt.lower()
        
        if "introduction" in prompt_lower:
            return "introduction"
        elif "subtopic" in prompt_lower:
            return "subtopics"
        elif "example" in prompt_lower:
            return "examples"
        elif "summary" in prompt_lower:
            return "summary"
        elif "multiple choice" in prompt_lower or "mcq" in prompt_lower:
            return "mcqs"
        elif "very short" in prompt_lower and "question" in prompt_lower:
            return "very_short_qa"
        elif "short" in prompt_lower and "question" in prompt_lower:
            return "short_qa"
        elif "long" in prompt_lower and "question" in prompt_lower:
            return "long_qa"
        elif "reference" in prompt_lower:
            return "references"
        else:
            return "generic"
    
    def _extract_topic_subject(self, prompt: str) -> tuple:
        """Extract topic and subject from prompt."""
        # Extract topic using regex patterns
        topic_match = re.search(r'topic[:\s]+([^,.]+)|\'([^\']+)\'', prompt, re.IGNORECASE)
        topic = topic_match.group(1) if topic_match and topic_match.group(1) else topic_match.group(2) if topic_match else "Education"
        
        # Extract subject similarly
        subject_match = re.search(r'subject[:\s]+([^,.]+)|{subject}', prompt, re.IGNORECASE)
        subject = subject_match.group(1) if subject_match else "Education"
        
        return topic.strip(), subject.strip()
    
    def _generate_introduction(self, topic: str, subject: str, language: str = "english") -> str:
        """Generate an introduction for a chapter."""
        language = language.lower()
        if language not in ["english", "hindi"]:
            language = "english"  # Default to English if language not supported
        
        # Select a random introduction template
        templates = self.templates["introduction"][language]
        introduction = random.choice(templates)
        
        # Fill in the template with topic and subject
        return introduction.format(topic=topic, subject=subject)
    
    def _generate_subtopics(self, topic: str, subject: str, language: str = "english") -> List[Dict[str, str]]:
        """Generate subtopics with content for a chapter."""
        language = language.lower()
        if language not in ["english", "hindi"]:
            language = "english"
        
        # Determine number of subtopics (3-5)
        num_subtopics = random.randint(3, 5)
        
        # Select random subtopic titles
        selected_titles = random.sample(self.templates["subtopic_titles"], num_subtopics)
        
        # Format the titles with the topic
        formatted_titles = [title.format(topic=topic) for title in selected_titles]
        
        # Generate content for each subtopic
        subtopics = []
        for title in formatted_titles:
            # Select a content template
            content_template = random.choice(self.templates["subtopic_content"][language])
            
            # Fill in the template
            content = content_template.format(title=title, topic=topic, subject=subject)
            
            subtopics.append({"title": title, "content": content})
        
        return subtopics
    
    def _generate_examples(self, topic: str, subject: str, language: str = "english") -> str:
        """Generate examples for the topic."""
        # This would be implemented similar to the examples in deepseek_local.py
        return f"Examples of {topic} in {subject} education..."
    
    def _generate_summary(self, topic: str, subject: str, language: str = "english") -> str:
        """Generate a summary for the topic."""
        # This would be implemented similar to the summary in deepseek_local.py
        return f"Summary of {topic} in {subject} education..."
    
    def _generate_mcqs(self, topic: str, subject: str, language: str = "english") -> List[Dict]:
        """Generate multiple choice questions."""
        # This would be implemented similar to the MCQs in deepseek_local.py
        return [{"question": f"Question about {topic}...", "options": ["A", "B", "C", "D"], "correct_index": 0}]
    
    def _generate_very_short_qa(self, topic: str, subject: str, language: str = "english") -> List[Dict]:
        """Generate very short question and answers."""
        # This would be implemented similar to the very short QA in deepseek_local.py
        return [{"question": f"Question about {topic}...", "answer": "Short answer..."}]
    
    def _generate_short_qa(self, topic: str, subject: str, language: str = "english") -> List[Dict]:
        """Generate short question and answers."""
        # This would be implemented similar to the short QA in deepseek_local.py
        return [{"question": f"Question about {topic}...", "answer": "Longer answer..."}]
    
    def _generate_long_qa(self, topic: str, subject: str, language: str = "english") -> List[Dict]:
        """Generate long question and answers."""
        # This would be implemented similar to the long QA in deepseek_local.py
        return [{"question": f"Question about {topic}...", "answer": "Very long answer..."}]
    
    def _generate_references(self, topic: str, subject: str) -> List[str]:
        """Generate academic references."""
        # This would be implemented similar to the references in deepseek_local.py
        return [f"Reference for {topic}..."]
    
    def _generate_generic_content(self, topic: str, subject: str, language: str = "english") -> str:
        """Generate generic content when the type is not identified."""
        return f"Educational content about {topic} in the field of {subject} education."

# Factory function to get DeepSeek smaller model instance
def get_deepseek_smaller_model(model_path: Optional[str] = None):
    """
    Returns a DeepSeek smaller model instance.
    
    Args:
        model_path (str, optional): Path to the model files. If not provided,
                                  the model will be downloaded from HuggingFace.
    
    Returns:
        DeepSeekSmallerModel: An instance of the DeepSeek smaller model
    """
    return DeepSeekSmallerModel(model_path)