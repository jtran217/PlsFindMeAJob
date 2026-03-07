
from openai import OpenAI
from app.core.config import settings
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class OpenAIClient:

    def __init__(self):
        self.client = OpenAI(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            timeout=settings.openrouter_timeout
        )
        self.default_model = settings.openrouter_model
        self.max_tokens = settings.openrouter_max_tokens

    def load_schema(self, schema_path: str) -> dict:
        """Load JSON schema from file with proper path resolution and error handling."""
        resolved_path = None
        try:
            # Convert to absolute path from project root
            if not schema_path.startswith('/'):
                resolved_path = settings.BASE_DIR / schema_path
            else:
                resolved_path = Path(schema_path)
            
            if not resolved_path.exists():
                raise FileNotFoundError(f"Schema file not found: {resolved_path}")
            
            with open(resolved_path, 'r') as file:
                schema = json.load(file)
            
            logger.debug(f"Successfully loaded schema from {resolved_path}")
            return schema
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in schema file {resolved_path}: {e}")
            raise ValueError(f"Invalid JSON in schema file: {e}")
        except Exception as e:
            logger.error(f"Error loading schema from {resolved_path or schema_path}: {e}")
            raise

    def load_prompt(self, prompt_path: str) -> str:
        """Load prompt template from file with proper path resolution and error handling."""
        resolved_path = None
        try:
            # Convert to absolute path from project root
            if not prompt_path.startswith('/'):
                resolved_path = settings.BASE_DIR / prompt_path
            else:
                resolved_path = Path(prompt_path)
            
            if not resolved_path.exists():
                raise FileNotFoundError(f"Prompt file not found: {resolved_path}")
            
            with open(resolved_path, 'r') as file:
                prompt = file.read()
            
            logger.debug(f"Successfully loaded prompt from {resolved_path}")
            return prompt
            
        except Exception as e:
            logger.error(f"Error loading prompt from {resolved_path or prompt_path}: {e}")
            raise

    def inject_prompt(self, prompt: str, data: dict) -> str:
        """Inject data into prompt template with proper error handling."""
        try:
            return prompt.format(
                job_description=data["job_description"],
                profile_json=json.dumps(data["profile_json"], indent=2),
                payload_schema=json.dumps(data["schema"], indent=2)
            )
        except KeyError as e:
            logger.error(f"Missing key in data for prompt injection: {e}")
            raise ValueError(f"Missing required data key: {e}")
        except Exception as e:
            logger.error(f"Error injecting prompt data: {e}")
            raise






