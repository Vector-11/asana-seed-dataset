"""
LLM-Enhanced Content Generation using Groq API
Provides realistic task descriptions, comments, and project details
"""

import os
import json
import logging
from typing import Optional
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)


class GroqEnhancer:
    """Enhance generated content using Groq's fast LLM inference"""

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.enabled = bool(self.api_key)

        if self.enabled:
            logger.info(f"Groq LLM enhancement enabled with model: {self.model}")
        else:
            logger.info("Groq API key not configured, using default content")

    def generate_task_description(self, task_name: str, project_type: str) -> str:
        """Generate realistic task description using Groq"""
        if not self.enabled:
            return None

        prompt = f"""Given this task: "{task_name}" in a {project_type} project, 
        generate a concise, professional task description (1-2 sentences max). 
        Be specific and actionable. Return only the description, no quotes."""

        return self._call_groq(prompt)

    def generate_comment(self, task_name: str, user_role: str) -> str:
        """Generate realistic task comment"""
        if not self.enabled:
            return None

        prompt = f"""Generate a brief, professional comment (1 sentence) from a {user_role} 
        about this task: "{task_name}". Include actionable feedback or status update.
        Return only the comment, no quotes."""

        return self._call_groq(prompt)

    def generate_project_description(self, project_name: str, project_type: str) -> str:
        """Generate project description"""
        if not self.enabled:
            return None

        prompt = f"""Create a concise project description for "{project_name}" ({project_type}). 
        2-3 sentences max. Be professional and specific about goals.
        Return only the description, no quotes."""

        return self._call_groq(prompt)

    def _call_groq(self, prompt: str) -> Optional[str]:
        """Call Groq API with error handling"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }

            payload = json.dumps(
                {
                    "model": self.model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7,
                    "max_tokens": 150,
                }
            ).encode("utf-8")

            req = urllib.request.Request(
                self.api_url, data=payload, headers=headers, method="POST"
            )

            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()

        except urllib.error.HTTPError as e:
            error_body = ""
            try:
                error_body = e.read().decode("utf-8")
            except:
                pass
            
            if e.status == 403:
                logger.warning(f"Groq API authentication error (403). Check API key validity.")
            elif e.status == 429:
                logger.warning(f"Groq API rate limited (429). Using default content.")
            else:
                logger.warning(f"Groq API error: {e.status}. Using default content.")
            return None
        except urllib.error.URLError as e:
            logger.warning(f"Network error calling Groq API: {e}. Using default content.")
            return None
        except json.JSONDecodeError:
            logger.warning("Failed to parse Groq response. Using default content.")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error with Groq: {e}. Using default content.")
            return None


# Global enhancer instance
_enhancer = None


def get_enhancer() -> GroqEnhancer:
    """Get or create global Groq enhancer instance"""
    global _enhancer
    if _enhancer is None:
        _enhancer = GroqEnhancer()
    return _enhancer


def enhance_task_description(task_name: str, project_type: str) -> Optional[str]:
    """Enhanced task description generation"""
    return get_enhancer().generate_task_description(task_name, project_type)


def enhance_comment(task_name: str, user_role: str) -> Optional[str]:
    """Enhanced comment generation"""
    return get_enhancer().generate_comment(task_name, user_role)


def enhance_project_description(project_name: str, project_type: str) -> Optional[str]:
    """Enhanced project description generation"""
    return get_enhancer().generate_project_description(project_name, project_type)
