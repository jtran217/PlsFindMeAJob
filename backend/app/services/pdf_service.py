"""
PDF generation service for resume optimization system.

Renders the master resume data + optimized bullet points into a LaTeX template,
then compiles to PDF using pdflatex. Uses Jinja2 with custom delimiters
(<< >> and <@ @>) to avoid conflicts with LaTeX curly braces.

Template location: backend/templates/jake_resume.tex
Output location:   backend/data/resume_versions/{name}_{job_id}_{timestamp}.pdf
"""

import logging
import os
import re
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional

from jinja2 import Environment, FileSystemLoader

from app.models.resume import (
    Education,
    Experience,
    OptimizedContent,
    PersonalInfo,
    Project,
    TechnicalSkills,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# LaTeX special character escaping
# ---------------------------------------------------------------------------

_LATEX_SPECIAL = {
    '&':  r'\&',
    '%':  r'\%',
    '$':  r'\$',
    '#':  r'\#',
    '_':  r'\_',
    '{':  r'\{',
    '}':  r'\}',
    '~':  r'\textasciitilde{}',
    '^':  r'\textasciicircum{}',
    '\\': r'\textbackslash{}',
}

_LATEX_ESCAPE_RE = re.compile(
    '(' + '|'.join(re.escape(k) for k in sorted(_LATEX_SPECIAL, key=len, reverse=True)) + ')'
)


def latex_escape(text: str) -> str:
    """Escape special LaTeX characters in a string."""
    if not text:
        return ''
    return _LATEX_ESCAPE_RE.sub(lambda m: _LATEX_SPECIAL[m.group()], str(text))


# ---------------------------------------------------------------------------
# PDF Service
# ---------------------------------------------------------------------------

class PDFService:
    """
    Generates PDF resumes from a LaTeX template using Jinja2 + pdflatex.

    Template rendering uses custom Jinja2 delimiters to avoid conflicts with
    LaTeX syntax:
        Variables:  << variable >>   (instead of {{ }})
        Blocks:     <@ block @>      (instead of {% %})
        Comments:   <# comment #>    (instead of {# #})
    """

    def __init__(self) -> None:
        backend_dir = Path(__file__).parent.parent.parent
        self.template_dir = backend_dir / "templates"
        self.output_dir = backend_dir / "data" / "resume_versions"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            # Custom delimiters — no conflict with LaTeX braces
            block_start_string='<@',
            block_end_string='@>',
            variable_start_string='<<',
            variable_end_string='>>',
            comment_start_string='<#',
            comment_end_string='#>',
            # Keep LaTeX whitespace intact
            trim_blocks=True,
            lstrip_blocks=True,
        )
        self.jinja_env.filters['latex_escape'] = latex_escape

    def generate_resume_pdf(
        self,
        job_id: str,
        personal_info: PersonalInfo,
        education: List[Education],
        technical_skills: TechnicalSkills,
        selected_experience_ids: List[str],
        selected_project_ids: List[str],
        all_experiences: List[Experience],
        all_projects: List[Project],
        optimized_content: OptimizedContent,
    ) -> Path:
        """
        Generate a PDF resume for a specific job.

        Args:
            job_id:                   Target job identifier.
            personal_info:            Personal contact info.
            education:                Education entries.
            technical_skills:         Technical skills by category.
            selected_experience_ids:  IDs of selected experiences (ordered).
            selected_project_ids:     IDs of selected projects (ordered).
            all_experiences:          Full list of experiences (for lookup).
            all_projects:             Full list of projects (for lookup).
            optimized_content:        AI-optimized bullet points keyed by ID.

        Returns:
            Path to the generated PDF file.

        Raises:
            FileNotFoundError: If the LaTeX template is missing.
            RuntimeError:      If pdflatex compilation fails.
        """
        # Build template context
        context = self._build_template_context(
            personal_info=personal_info,
            education=education,
            technical_skills=technical_skills,
            selected_experience_ids=selected_experience_ids,
            selected_project_ids=selected_project_ids,
            all_experiences=all_experiences,
            all_projects=all_projects,
            optimized_content=optimized_content,
        )

        # Render LaTeX
        template = self.jinja_env.get_template("jake_resume.tex")
        latex_content = template.render(**context)

        # Compile to PDF in a temp directory
        pdf_path = self._compile_to_pdf(
            latex_content=latex_content,
            job_id=job_id,
            name=personal_info.name,
        )

        logger.info(f"PDF generated: {pdf_path}")
        return pdf_path

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_template_context(
        self,
        personal_info: PersonalInfo,
        education: List[Education],
        technical_skills: TechnicalSkills,
        selected_experience_ids: List[str],
        selected_project_ids: List[str],
        all_experiences: List[Experience],
        all_projects: List[Project],
        optimized_content: OptimizedContent,
    ) -> dict:
        """Build the Jinja2 template rendering context."""
        exp_lookup: Dict[str, Experience] = {e.id: e for e in all_experiences}
        proj_lookup: Dict[str, Project] = {p.id: p for p in all_projects}

        selected_experiences = []
        for exp_id in selected_experience_ids:
            exp = exp_lookup.get(exp_id)
            if not exp:
                continue
            opt = optimized_content.experiences.get(exp_id)
            if opt:
                bullets = [b.optimized for b in opt.optimized_bullet_points if b.optimized]
            else:
                bullets = [b.text for b in exp.bullet_points if b.text]
            selected_experiences.append({
                'title':                   exp.title,
                'company':                 exp.company,
                'location':                exp.location,
                'duration':                exp.duration,
                'optimized_bullet_points': bullets,
            })

        selected_projects = []
        for proj_id in selected_project_ids:
            proj = proj_lookup.get(proj_id)
            if not proj:
                continue
            opt = optimized_content.projects.get(proj_id)
            if opt:
                bullets = [b.optimized for b in opt.optimized_bullet_points if b.optimized]
            else:
                bullets = [b.text for b in proj.bullet_points if b.text]
            selected_projects.append({
                'name':                    proj.name,
                'technologies':            proj.technologies,
                'duration':                proj.duration,
                'optimized_bullet_points': bullets,
            })

        return {
            'personal_info':        personal_info,
            'education':            education,
            'technical_skills':     technical_skills,
            'selected_experiences': selected_experiences,
            'selected_projects':    selected_projects,
        }

    def _compile_to_pdf(self, latex_content: str, job_id: str, name: str) -> Path:
        """
        Write the LaTeX source to a temp directory, run pdflatex twice,
        copy the resulting PDF to the output directory, and clean up.

        Running pdflatex twice ensures correct resolution of internal
        references (e.g., hyperlinks, page numbers).
        """
        # Sanitize name for use in filename
        safe_name = re.sub(r'[^\w\-]', '_', name).strip('_') or 'resume'
        timestamp = int(time.time())
        output_filename = f"{safe_name}_{job_id}_{timestamp}.pdf"
        final_pdf_path = self.output_dir / output_filename

        with tempfile.TemporaryDirectory() as tmpdir:
            tex_path = Path(tmpdir) / "resume.tex"
            tex_path.write_text(latex_content, encoding='utf-8')

            for run in range(2):
                result = subprocess.run(
                    [
                        'pdflatex',
                        '-interaction=nonstopmode',
                        '-halt-on-error',
                        f'-output-directory={tmpdir}',
                        str(tex_path),
                    ],
                    capture_output=True,
                    text=True,
                    cwd=tmpdir,
                )
                if result.returncode != 0:
                    # Include last 30 lines of pdflatex output for diagnostics
                    log_tail = '\n'.join(result.stdout.splitlines()[-30:])
                    raise RuntimeError(
                        f"pdflatex compilation failed (run {run + 1}):\n{log_tail}"
                    )

            compiled_pdf = Path(tmpdir) / "resume.pdf"
            if not compiled_pdf.exists():
                raise RuntimeError("pdflatex ran successfully but produced no PDF file.")

            import shutil
            shutil.copy2(compiled_pdf, final_pdf_path)

        return final_pdf_path

    def find_latest_pdf(self, job_id: str) -> Optional[Path]:
        """
        Find the most recently generated PDF for a given job ID.

        Args:
            job_id: Job identifier to search for.

        Returns:
            Path to the most recent PDF, or None if not found.
        """
        pdfs = list(self.output_dir.glob(f"*_{job_id}_*.pdf"))
        if not pdfs:
            return None
        # Return the newest by modification time
        return max(pdfs, key=lambda p: p.stat().st_mtime)
