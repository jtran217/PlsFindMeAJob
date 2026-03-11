"""
Resume optimization service using OpenRouter AI.

This module provides AI-powered bullet point optimization using a per-item
batching strategy: all bullet points for a given experience or project are
sent in a single API call, reducing total calls from N_bullets to N_items
(~3.5x fewer calls, ~$0.010 vs ~$0.016 per full optimization run).

On any failure (API error, malformed JSON, missing bullet IDs), the affected
item silently falls back to original bullet text so the user always gets a
complete response they can edit in the review step.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Tuple, Union

from dotenv import load_dotenv
from openai import AsyncOpenAI

from app.models.resume import (
    BulletPoint,
    Experience,
    OptimizedBullet,
    OptimizedContent,
    OptimizedExperienceContent,
    OptimizedProjectContent,
    Project,
)

# Load .env from project root (two levels up from backend/app/)
_env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=_env_path)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are an expert resume writer specializing in optimizing bullet points for \
specific job applications. Your goal is to enhance bullet points so they \
closely align with the target role while remaining completely truthful and \
accurate to the original experience."""

_USER_PROMPT_TEMPLATE = """\
Optimize the following resume bullet points for a {job_title} position at \
{company}.

Job Description:
{job_description}

Bullet points to optimize (JSON array):
{bullets_json}

Guidelines:
1. TERMINOLOGY ALIGNMENT — use the exact technical terms and language from \
the job posting; match the company's vocabulary and industry terminology; \
align action verbs with those in the job requirements.
2. QUANTIFICATION — add specific numbers, percentages, or scales where \
realistic; use contextual estimates typical for this role and company size; \
only add metrics that are realistically achievable and truthful.
3. ACHIEVEMENT FOCUS — convert responsibilities into achievements and results; \
emphasize business impact and value delivered; use action verbs that \
demonstrate leadership and initiative.
4. JOB RELEVANCE — highlight aspects most relevant to the target role; \
emphasize skills and technologies mentioned in the job posting.

Constraints:
- Never exaggerate or fabricate — maintain complete truthfulness.
- Keep the core meaning and accuracy of each original statement.
- Maximum 2 lines per bullet point.
- Return ONLY a valid JSON array. Each element must have exactly two fields: \
"bullet_id" (string, unchanged from input) and "optimized_text" (string).

Example output format:
[
  {{"bullet_id": "abc-123", "optimized_text": "Optimized bullet text here"}},
  {{"bullet_id": "def-456", "optimized_text": "Another optimized bullet here"}}
]"""


class OptimizationService:
    """
    AI-powered resume optimization using OpenRouter (OpenAI-compatible API).

    Uses per-item batching: one API call per selected experience/project,
    sending all bullet points for that item together and receiving a structured
    JSON array of optimized bullets in return.
    """

    def __init__(self) -> None:
        """
        Initialize the service from environment variables.

        Raises:
            EnvironmentError: If OPENROUTER_API_KEY is not set.
        """
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "OPENROUTER_API_KEY is not set. "
                "Add it to the .env file at the project root."
            )

        self.model = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-haiku")
        self.max_tokens = int(os.getenv("OPENROUTER_MAX_TOKENS", "4096"))
        self.timeout = float(os.getenv("OPENROUTER_TIMEOUT", "30"))
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=self.timeout,
        )

        logger.info(
            f"OptimizationService initialized — model: {self.model}, "
            f"max_tokens: {self.max_tokens}, timeout: {self.timeout}s"
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def optimize_resume_items(
        self,
        selected_experiences: List[Experience],
        selected_projects: List[Project],
        job_description: str,
        job_title: str,
        company: str,
    ) -> OptimizedContent:
        """
        Optimize all bullet points for selected experiences and projects.

        Fires one concurrent API call per item (experience or project) using
        asyncio.gather. On failure for any individual item, falls back to the
        original bullet text for that item without affecting the others.

        Args:
            selected_experiences: Experience objects whose bullets to optimize.
            selected_projects: Project objects whose bullets to optimize.
            job_description: Full job posting text for context.
            job_title: Target job title.
            company: Target company name.

        Returns:
            OptimizedContent with optimized bullets organized by item ID.
        """
        job_context = {
            "job_description": job_description,
            "job_title": job_title,
            "company": company,
        }

        # Build one coroutine per selected item
        exp_tasks = [
            self._optimize_item_bullets(exp, "experience", **job_context)
            for exp in selected_experiences
        ]
        proj_tasks = [
            self._optimize_item_bullets(proj, "project", **job_context)
            for proj in selected_projects
        ]

        all_tasks = exp_tasks + proj_tasks
        results: List[Tuple[str, str, List[OptimizedBullet]]] = await asyncio.gather(
            *all_tasks
        )

        # Split results back into experiences and projects
        n_exp = len(selected_experiences)
        exp_results = results[:n_exp]
        proj_results = results[n_exp:]

        optimized_experiences: Dict[str, OptimizedExperienceContent] = {
            item_id: OptimizedExperienceContent(optimized_bullet_points=bullets)
            for item_id, _item_type, bullets in exp_results
        }
        optimized_projects: Dict[str, OptimizedProjectContent] = {
            item_id: OptimizedProjectContent(optimized_bullet_points=bullets)
            for item_id, _item_type, bullets in proj_results
        }

        logger.info(
            f"Optimization complete — "
            f"{len(optimized_experiences)} experiences, "
            f"{len(optimized_projects)} projects"
        )

        return OptimizedContent(
            experiences=optimized_experiences,
            projects=optimized_projects,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _optimize_item_bullets(
        self,
        item: Union[Experience, Project],
        item_type: str,
        job_description: str,
        job_title: str,
        company: str,
    ) -> Tuple[str, str, List[OptimizedBullet]]:
        """
        Optimize all bullet points for a single experience or project.

        Sends all bullets in one API call and parses the structured JSON
        response. On any failure, falls back to original bullet text for
        every bullet in this item (partial success within an item is not
        supported — all or nothing per item).

        Args:
            item: Experience or Project to optimize.
            item_type: "experience" or "project" (used for logging only).
            job_description: Full job posting text.
            job_title: Target job title.
            company: Target company name.

        Returns:
            Tuple of (item.id, item_type, list_of_optimized_bullets).
        """
        item_label = getattr(item, "title", None) or getattr(item, "name", "unknown")

        if not item.bullet_points:
            logger.debug(f"No bullet points to optimize for {item_type} '{item_label}'")
            return item.id, item_type, []

        try:
            optimized_bullets = await self._call_openrouter(
                item=item,
                job_description=job_description,
                job_title=job_title,
                company=company,
            )
            logger.info(
                f"Optimized {len(optimized_bullets)} bullets for "
                f"{item_type} '{item_label}'"
            )
            return item.id, item_type, optimized_bullets

        except Exception as e:
            logger.error(
                f"Optimization failed for {item_type} '{item_label}': {e}. "
                f"Falling back to original bullet text."
            )
            fallback = self._build_fallback_bullets(item.bullet_points)
            return item.id, item_type, fallback

    async def _call_openrouter(
        self,
        item: Union[Experience, Project],
        job_description: str,
        job_title: str,
        company: str,
    ) -> List[OptimizedBullet]:
        """
        Make a single OpenRouter API call to optimize all bullets for an item.

        Builds the prompt, calls the API, parses and validates the JSON
        response, and matches optimized text back to original bullet IDs.

        Args:
            item: Experience or Project whose bullets to optimize.
            job_description: Full job posting text.
            job_title: Target job title.
            company: Target company name.

        Returns:
            List of OptimizedBullet objects.

        Raises:
            ValueError: If the API response cannot be parsed or matched.
            openai.APIError: If the API call itself fails.
        """
        # Build the bullets input for the prompt
        bullets_input = [
            {"bullet_id": bp.id, "original_text": bp.text}
            for bp in item.bullet_points
        ]
        bullets_json = json.dumps(bullets_input, indent=2)

        user_prompt = _USER_PROMPT_TEMPLATE.format(
            job_title=job_title,
            company=company,
            job_description=job_description,
            bullets_json=bullets_json,
        )

        response = await self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )

        raw_content = response.choices[0].message.content or ""
        return self._parse_optimized_bullets(
            raw_content=raw_content,
            original_bullets=item.bullet_points,
        )

    def _parse_optimized_bullets(
        self,
        raw_content: str,
        original_bullets: List[BulletPoint],
    ) -> List[OptimizedBullet]:
        """
        Parse the model's JSON response into OptimizedBullet objects.

        Attempts to extract a JSON array from the response (handles cases
        where the model wraps the array in markdown code fences). Matches
        each parsed entry back to an original bullet by ID. Any bullet whose
        ID is missing from the response falls back to its original text.

        Args:
            raw_content: Raw string response from the model.
            original_bullets: Original bullet points for fallback matching.

        Returns:
            List of OptimizedBullet objects (one per original bullet).

        Raises:
            ValueError: If the response contains no parseable JSON array.
        """
        # Strip markdown code fences if present (```json ... ``` or ``` ... ```)
        content = raw_content.strip()
        if content.startswith("```"):
            lines = content.splitlines()
            # Remove first and last fence lines
            content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        # Find the JSON array boundaries
        start = content.find("[")
        end = content.rfind("]")
        if start == -1 or end == -1:
            raise ValueError(
                f"No JSON array found in model response. Raw content: {raw_content[:200]}"
            )

        parsed: List[dict] = json.loads(content[start : end + 1])

        # Build a lookup from bullet_id → optimized_text
        optimized_map: Dict[str, str] = {}
        for entry in parsed:
            bullet_id = entry.get("bullet_id", "")
            optimized_text = entry.get("optimized_text", "")
            if bullet_id and optimized_text:
                optimized_map[bullet_id] = optimized_text

        # Match back to originals; fall back for any missing IDs
        result: List[OptimizedBullet] = []
        for bp in original_bullets:
            optimized_text = optimized_map.get(bp.id)
            if not optimized_text:
                logger.warning(
                    f"Bullet ID '{bp.id}' not found in model response — "
                    f"using original text."
                )
                optimized_text = bp.text
            result.append(
                OptimizedBullet(
                    bullet_id=bp.id,
                    original=bp.text,
                    optimized=optimized_text,
                )
            )

        return result

    @staticmethod
    def _build_fallback_bullets(
        bullet_points: List[BulletPoint],
    ) -> List[OptimizedBullet]:
        """
        Build OptimizedBullet objects using original text as the optimized text.

        Used when an API call fails entirely for an item.

        Args:
            bullet_points: Original bullet points to use as fallback.

        Returns:
            List of OptimizedBullet with optimized == original.
        """
        return [
            OptimizedBullet(
                bullet_id=bp.id,
                original=bp.text,
                optimized=bp.text,
            )
            for bp in bullet_points
        ]
