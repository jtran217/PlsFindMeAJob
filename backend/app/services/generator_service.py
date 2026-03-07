import logging
from app.core.config import settings
from app.utils.openai_client import OpenAIClient
logger = logging.getLogger(__name__)

class GeneratorService:
    """Service class for handling generator-related operations."""
    
    def __init__(self):
        self.client = OpenAIClient()

    def optimize_resume(self, job_description: str, profile_json: dict) -> dict:
        """Optimize resume based on job description and user profile."""
        try:
            prompt_template = self.client.load_prompt("app/prompts/resume_optimization.txt")
            schema = self.client.load_schema("app/schemas/resume_optimization_schema.json")

            data = {
                "job_description": job_description,
                "profile_json": profile_json,
                "schema": schema
            }

            prompt = self.client.inject_prompt(prompt_template, data)
            # Call OpenAI API to get optimized resume
            response = self.client.client.chat.completions.create(
                model=self.client.default_model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=self.client.max_tokens
            )

            # Extract optimized resume from response
            optimized_resume = response.choices[0].message.content

            return {
                "optimized_resume": optimized_resume
            }

        except Exception as e:
            logger.error(f"Error optimizing resume: {str(e)}")
            raise e
  
 
