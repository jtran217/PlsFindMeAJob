
from openai import AsyncOpenAI
from app.core.config import settings, Settings
import json



class OpenAIClient:

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openrouter_api_key,
                                  base_url=settings.openrouter_base_url, 
                                  timeout=settings.openrouter_timeout)
        self.default_model = settings.openrouter_model
        self.max_tokens = settings.openrouter_max_tokens

    def load_schema(self, schema_path: str) -> str:
        with open(schema_path, 'r') as file:
            return json.load(file)

    def load_prompt(self, prompt_path: str) -> str:
        with open(prompt_path, 'r') as file:
            return file.read()

    def inject_prompt(self, prompt: str, data: dict) -> str:
        return prompt.format(
            job_description=data["job_description"],
            profile_json=json.dumps(data["profile_json"], indent=2),
            payload_schema=json.dumps(data["schema"], indent=2)
        )






