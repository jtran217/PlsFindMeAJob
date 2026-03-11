# Resume Optimization System - Implementation Roadmap

## Project Overview
Building a standalone resume optimization system integrated with the existing job dashboard. The system will:
- Allow manual resume input with full CRUD operations
- Score and select top 5 experiences/projects based on job relevance
- Use OpenRouter AI for content optimization (terminology + quantification)
- Generate professional PDFs using LaTeX
- Provide single-page interface with expandable sections
- Use file-based storage for simplicity

## User Requirements Summary
1. **Keyword matching** as well as **technology overlap** for scoring
2. **Terminology alignment** as well as **quantified metrics**, even if forced but realistic
3. Users should be able to **override top 5 selections** and **edit optimized bullet points**
4. **Standalone** system (not integrated into job dashboard workflow)
5. Store **resume versions only** (not multiple resume types)

## Technical Specifications
- **Data Entry**: Manual input forms
- **AI Service**: OpenRouter 
- **PDF Generation**: LaTeX
- **UI Design**: Single page with expandable sections
- **Storage**: File-based JSON storage
- **Integration**: New navigation menu item

---

# Phase 1: Backend Foundation

## 1.1 Data Models & Storage (DONE)

### Files to Create:
- `backend/app/models/resume.py` - Pydantic models
- `backend/data/user_resume.json` - Master resume storage
- `backend/data/resume_versions/` - Job-specific versions directory

### Data Structure:

#### Master Resume Schema (`user_resume.json`):
```json
{
  "personal_info": {
    "name": "string",
    "phone": "string", 
    "email": "string",
    "linkedin": "string",
    "github": "string"
  },
  "education": [
    {
      "id": "uuid",
      "institution": "string",
      "location": "string", 
      "degree": "string",
      "duration": "string"
    }
  ],
  "technical_skills": {
    "languages": ["Java", "Python", "JavaScript"],
    "frameworks": ["React", "Flask", "FastAPI"],
    "developer_tools": ["Git", "Docker", "VS Code"],
    "libraries": ["pandas", "NumPy", "React"]
  },
  "experiences": [
    {
      "id": "uuid",
      "title": "Software Engineer",
      "company": "Google",
      "location": "Mountain View, CA",
      "duration": "June 2020 -- Present",
      "bullet_points": [
        {
          "id": "uuid",
          "text": "Developed REST APIs using FastAPI and PostgreSQL",
          "keywords": ["REST", "API", "FastAPI", "PostgreSQL"],
          "category": "technical"
        }
      ],
      "overall_keywords": ["backend", "api", "database", "python"],
      "relevance_score": 0.0
    }
  ],
  "projects": [
    {
      "id": "uuid", 
      "name": "Gitlytics",
      "technologies": "Python, Flask, React, PostgreSQL",
      "duration": "June 2020 -- Present",
      "bullet_points": [
        {
          "id": "uuid",
          "text": "Developed full-stack web application with Flask serving REST API",
          "keywords": ["full-stack", "Flask", "REST", "API"],
          "category": "technical"
        }
      ],
      "overall_keywords": ["full-stack", "web", "api", "database"],
      "relevance_score": 0.0
    }
  ]
}
```

#### Job-Specific Version Schema (`resume_versions/job_123_optimized.json`):
```json
{
  "job_id": "job_123",
  "generated_at": "2024-01-15T10:30:00Z",
  "selected_experiences": ["exp_1", "exp_2", "exp_3"],
  "selected_projects": ["proj_1", "proj_2"],
  "optimized_content": {
    "experiences": {
      "exp_1": {
        "optimized_bullet_points": [
          {
            "bullet_id": "bullet_uuid",
            "original": "Developed APIs",
            "optimized": "Architected scalable REST APIs serving 10M+ requests/day using FastAPI and PostgreSQL, improving response time by 40%"
          }
        ]
      }
    },
    "projects": {
      "proj_1": {
        "optimized_bullet_points": [
          {
            "bullet_id": "bullet_uuid",
            "original": "Built web application",
            "optimized": "Developed full-stack web application serving 1000+ users with React frontend and Flask REST API, achieving 99.9% uptime"
          }
        ]
      }
    }
  }
}
```

## 1.2 API Endpoints (DONE)

### Extend `backend/app/main.py`:
```python
# Resume CRUD
@app.get("/api/resume")
async def get_resume():
    """Get user's master resume"""

@app.post("/api/resume") 
async def save_resume(resume_data: Resume):
    """Save/update user's master resume"""

@app.put("/api/resume")
async def update_resume(resume_data: Resume):
    """Update specific parts of resume"""

# Job-specific optimization
@app.post("/api/resume/analyze/{job_id}")
async def analyze_job_for_resume(job_id: str):
    """
    Analyze job description and score all experiences/projects
    Returns ranked lists with relevance scores
    """

@app.post("/api/resume/optimize/{job_id}")
async def optimize_resume_for_job(
    job_id: str, 
    selected_experiences: List[str],
    selected_projects: List[str]
):
    """
    Send selected items + job description to AI for optimization
    Returns optimized bullet points for review
    """

@app.post("/api/resume/generate-pdf/{job_id}")
async def generate_resume_pdf(
    job_id: str,
    finalized_content: OptimizedContent
):
    """Generate final LaTeX PDF with optimized content"""

# Resume versions management  
@app.get("/api/resume/versions")
async def get_resume_versions():
    """List all job-specific resume versions"""

@app.get("/api/resume/versions/{job_id}")
async def get_resume_version(job_id: str):
    """Get specific job resume version"""
```

## 1.3 Services to Create (DONE)

### `backend/app/services/resume_service.py`:
```python
class ResumeService:
    def load_master_resume() -> Resume
    def save_master_resume(resume: Resume) -> bool
    def load_resume_version(job_id: str) -> OptimizedResume
    def save_resume_version(job_id: str, optimized: OptimizedResume) -> bool
```

### `backend/app/services/scoring_service.py`:
```python
def calculate_relevance_score(
    item: Union[Experience, Project],
    job_keywords: List[str],
    job_technologies: List[str]
) -> float:
    """
    Score based on user requirements:
    1. Keyword matching (40% weight)
    2. Technology overlap (35% weight) 
    3. Other factors (25% weight)
    """
    keyword_score = len(set(item.overall_keywords) & set(job_keywords)) / len(job_keywords)
    tech_score = len(set(extract_technologies(item)) & set(job_technologies)) / len(job_technologies)
    
    # Other factors: recency, role level, industry alignment
    other_score = calculate_other_factors(item, job_context)
    
    return (keyword_score * 0.4) + (tech_score * 0.35) + (other_score * 0.25)

def rank_experiences_and_projects(
    resume: Resume, 
    job_description: str
) -> Tuple[List[Experience], List[Project]]:
    """Return ranked lists of experiences and projects"""
```

### `backend/app/services/optimization_service.py`:
```python
class OptimizationService:
    def __init__(self, openrouter_api_key: str):
        self.api_key = openrouter_api_key
    
    async def optimize_resume_items(
        selected_experiences: List[Experience],
        selected_projects: List[Project],
        job_description: str,
        job_title: str,
        company: str
    ) -> OptimizedContent:
        """
        Per-item batching strategy: one API call per experience/project.
        All bullet points for an item are sent in a single prompt and
        returned as a structured JSON array. Calls are fired concurrently
        via asyncio.gather (~5 calls vs ~18 for per-bullet approach).
        
        Cost: ~$0.010 per full optimization run with claude-3.5-haiku.
        On failure for any item: falls back to original bullet text.
        """
```

### `backend/app/services/pdf_service.py`:
```python
class PDFService:
    def generate_resume_pdf(
        job_id: str,
        resume_data: Resume,
        optimized_content: OptimizedContent
    ) -> str:
        """
        1. Load LaTeX template
        2. Inject user data + optimizations
        3. Compile with pdflatex
        4. Save to resume_versions/
        5. Return file path
        """
```

---

# Phase 2: Frontend Foundation

## 2.1 Navigation Integration

### Modify `frontend/src/App.tsx`:
- Add "Resume Builder" to main navigation
- Add routing for `/resume` path
- Maintain existing job dashboard functionality

### UI Changes:
```tsx
// Add to navigation
<nav className="mb-8">
  <div className="flex gap-4">
    <NavLink to="/" className="...">Job Dashboard</NavLink>
    <NavLink to="/resume" className="...">Resume Builder</NavLink>
  </div>
</nav>
```

## 2.2 Component Structure

### Files to Create:
```
frontend/src/components/resume/
├── ResumeBuilder.tsx           # Main single-page interface
├── sections/
│   ├── PersonalInfoSection.tsx # Collapsible personal info
│   ├── EducationSection.tsx    # Collapsible education
│   ├── SkillsSection.tsx       # Collapsible skills  
│   ├── ExperienceSection.tsx   # Collapsible experiences list
│   └── ProjectSection.tsx      # Collapsible projects list
├── forms/
│   ├── ExperienceForm.tsx      # Add/edit experience modal
│   ├── ProjectForm.tsx         # Add/edit project modal
│   └── BulletPointForm.tsx     # Individual bullet editing
└── optimization/
    ├── JobOptimizer.tsx        # Job-specific optimization flow
    ├── ContentSelector.tsx     # Top 5 selection with override
    ├── OptimizationReview.tsx  # Review and edit AI output
    └── PDFPreview.tsx          # Final preview before generation
```

### Hooks to Create:
```
frontend/src/hooks/
├── useResume.ts                # Resume CRUD operations
├── useOptimization.ts          # Job optimization flow
└── useResumeVersions.ts        # Version management
```

### Types to Create:
```
frontend/src/types/Resume.ts    # TypeScript interfaces matching backend
```

## 2.3 Single-Page Layout Design

### `ResumeBuilder.tsx` Structure:
```tsx
const ResumeBuilder = () => {
  const [expandedSections, setExpandedSections] = useState({
    personal: true,
    education: false, 
    skills: false,
    experience: false,
    projects: false
  });

  const [resume, setResume] = useState<Resume | null>(null);

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Header with save/load actions */}
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Resume Builder</h1>
        <div className="flex gap-2">
          <button onClick={saveResume}>Save Resume</button>
          <button onClick={loadResume}>Load Resume</button>
        </div>
      </div>
      
      {/* Collapsible Sections */}
      <PersonalInfoSection 
        data={resume?.personal_info}
        expanded={expandedSections.personal}
        onToggle={() => toggleSection('personal')}
        onChange={updatePersonalInfo}
      />
      
      <EducationSection 
        data={resume?.education}
        expanded={expandedSections.education}
        onToggle={() => toggleSection('education')}
        onChange={updateEducation}
      />
      
      <SkillsSection 
        data={resume?.technical_skills}
        expanded={expandedSections.skills}
        onToggle={() => toggleSection('skills')}
        onChange={updateSkills}
      />
      
      <ExperienceSection 
        data={resume?.experiences}
        expanded={expandedSections.experience}
        onToggle={() => toggleSection('experience')}
        onChange={updateExperiences}
      />
      
      <ProjectSection 
        data={resume?.projects}
        expanded={expandedSections.projects}
        onToggle={() => toggleSection('projects')}
        onChange={updateProjects}
      />
      
      {/* Job Optimization Panel */}
      <JobOptimizationPanel resume={resume} />
    </div>
  );
};
```

---

# Phase 3: Core Features Implementation

## 3.1 Resume Builder Interface Features

### Personal Info Section:
- Name, phone, email, LinkedIn, GitHub
- Simple form with validation
- Real-time preview

### Education Section:
- Add/edit/remove education entries
- Institution, location, degree, duration
- No optimization (per user requirement)

### Skills Section:
- Four categories: Languages, Frameworks, Developer Tools, Libraries
- Tag-based input with auto-suggestions
- No optimization (per user requirement)

### Experience Section:
- Add/edit/remove work experiences
- Each experience: title, company, location, duration
- Bullet points with CRUD operations
- Keyword extraction and categorization
- Visual indicators for completeness

### Project Section:
- Similar to experience section
- Project name, technologies, duration
- Bullet points with CRUD operations
- Keyword extraction

## 3.2 Job Optimization Workflow

### Integration Path:
```
Option A: From Job Dashboard
Job Dashboard → Select Job → "Generate Resume" → Resume Optimization Flow

Option B: From Resume Builder
Resume Builder → "Optimize for Job" → Select Job → Optimization Flow
```

### Optimization Steps:
1. **Job Analysis**: Extract keywords and technologies from job description
2. **Auto-Scoring**: Score all experiences and projects
3. **Smart Selection**: Show top 5 recommendations with override capability
4. **AI Optimization**: Send to OpenRouter for enhancement
5. **Review & Edit**: Allow user editing of optimized content
6. **PDF Generation**: Create final LaTeX PDF

## 3.3 Smart Selection Interface

### `ContentSelector.tsx` Features:
```tsx
const ContentSelector = ({ 
  experiences, 
  projects, 
  jobAnalysis, 
  onSelectionChange 
}) => {
  const [selectedExperiences, setSelectedExperiences] = useState<string[]>([]);
  const [selectedProjects, setSelectedProjects] = useState<string[]>([]);

  return (
    <div className="grid grid-cols-2 gap-6">
      {/* Experiences */}
      <div>
        <h3>Select Experiences (5 max)</h3>
        <div className="space-y-2">
          <div className="bg-green-50 p-4 rounded">
            <h4>Auto-Selected ({selectedExperiences.length}/5)</h4>
            {topExperiences.map(exp => (
              <ExperienceCard 
                key={exp.id}
                experience={exp}
                selected={true}
                score={exp.relevance_score}
                onToggle={() => toggleExperience(exp.id)}
              />
            ))}
          </div>
          
          <div className="bg-gray-50 p-4 rounded">
            <h4>Available</h4>
            {remainingExperiences.map(exp => (
              <ExperienceCard 
                key={exp.id}
                experience={exp}
                selected={false}
                score={exp.relevance_score}
                onToggle={() => toggleExperience(exp.id)}
              />
            ))}
          </div>
        </div>
      </div>
      
      {/* Projects - Similar structure */}
    </div>
  );
};
```

### UI Design Mockup:
```
┌─ Content Selection for Software Engineer @ Google ──┐
│                                                      │
│ ┌─ Experiences (3 of 8 selected) ──────────────────┐ │
│ │ ✅ Auto-Selected                                  │ │
│ │ ┌─ Software Engineer @ Meta ─── Score: 0.92 ───┐ │ │
│ │ │ • Built scalable APIs...                      │ │ │
│ │ │ • Led team of 5 engineers...                  │ │ │
│ │ └─ [Edit] [Remove] ────────────────────────────┘ │ │
│ │                                                   │ │
│ │ ⚪ Available                                      │ │
│ │ ┌─ Intern @ Facebook ─────── Score: 0.45 ──────┐ │ │
│ │ │ • Worked on frontend components...            │ │ │
│ │ └─ [Add] ──────────────────────────────────────┘ │ │
│ └─────────────────────────────────────────────────┘ │
│                                                      │
│ ┌─ Projects (2 of 5 selected) ─────────────────────┐ │
│ │ [Similar structure]                               │ │
│ └─────────────────────────────────────────────────┘ │
│                                                      │
│ [Reset Auto-Selection] [Continue to Optimization] ──┘
└──────────────────────────────────────────────────────┘
```

---

# Phase 4: AI Optimization Integration

## 4.1 OpenRouter Service Setup

### Environment Configuration:
```env
# Add to .env
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=anthropic/claude-3.5-haiku
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MAX_TOKENS=4096
OPENROUTER_TIMEOUT=30
```

### Batching Strategy Decision:
**Per-item batching** was chosen over per-bullet calls after a cost/architecture analysis:

| Strategy | API Calls | Est. Cost/Run | Notes |
|---|---|---|---|
| Per-bullet | ~18 | ~$0.016 | Max flexibility, highest call count |
| **Per-item batch** | **~5** | **~$0.010** | Best balance — chosen approach |
| Single call | 1 | ~$0.005 | Cheapest, hardest to parse/regenerate |

Per-item batching sends all bullet points for one experience/project in a single
prompt requesting a structured JSON array response `[{bullet_id, optimized_text}]`.
Calls are fired concurrently via `asyncio.gather`. This preserves per-bullet
regeneration capability in the review UI while reducing API calls ~3.5×.

### Service Configuration:
```python
# backend/app/services/optimization_service.py
class OptimizationService:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3-sonnet")
        self.client = OpenRouter(api_key=self.api_key)
    
    async def optimize_bullet_points(
        self, 
        bullet_points: List[str], 
        job_description: str,
        job_title: str,
        company: str,
        context: dict
    ) -> List[OptimizedBullet]:
        # Implementation with error handling and rate limiting
```

## 4.2 Optimization Prompt Strategy

### Prompt Template for User Requirements:
```python
OPTIMIZATION_PROMPT_TEMPLATE = """
You are optimizing resume bullet points for a {job_title} position at {company}.

Job Description:
{job_description}

Original bullet point: "{original_text}"

Please optimize this bullet point following these guidelines:

1. TERMINOLOGY ALIGNMENT:
   - Use the exact technical terms and language from the job posting
   - Match the company's vocabulary and industry terminology
   - Align action verbs with those mentioned in the job requirements

2. QUANTIFICATION (add realistic metrics where possible):
   - Add specific numbers, percentages, or scales when truthfully possible
   - Use contextual estimates based on typical {job_level} roles at {company_size} companies
   - Examples: team sizes, user counts, performance improvements, timelines
   - Only add metrics that are realistically achievable and truthful

3. ACHIEVEMENT FOCUS:
   - Convert responsibilities into achievements and results
   - Emphasize business impact and value delivered
   - Use action verbs that demonstrate leadership and initiative

4. JOB RELEVANCE:
   - Highlight aspects most relevant to the target role
   - Emphasize skills and technologies mentioned in the job posting
   - Connect your experience to the company's likely needs

CONSTRAINTS:
- Maintain complete truthfulness - never exaggerate or fabricate
- Keep the core meaning and accuracy of the original statement
- Ensure all added details are realistic and verifiable
- Maximum 2 lines per bullet point

Return only the optimized bullet point, nothing else.
"""

# Usage example:
def create_optimization_prompt(
    original_text: str,
    job_description: str, 
    job_title: str,
    company: str,
    job_level: str = "mid-level",
    company_size: str = "large"
) -> str:
    return OPTIMIZATION_PROMPT_TEMPLATE.format(
        original_text=original_text,
        job_description=job_description,
        job_title=job_title,
        company=company,
        job_level=job_level,
        company_size=company_size
    )
```

## 4.3 Review & Edit Interface

### `OptimizationReview.tsx` Features:
```tsx
const OptimizationReview = ({ 
  originalContent, 
  optimizedContent, 
  onAccept, 
  onEdit, 
  onRegenerate 
}) => {
  const [editedContent, setEditedContent] = useState(optimizedContent);

  return (
    <div className="space-y-6">
      {optimizedContent.experiences.map(exp => (
        <div key={exp.id} className="border rounded-lg p-4">
          <h3 className="font-bold">{exp.title} @ {exp.company}</h3>
          
          {exp.bullet_points.map(bullet => (
            <div key={bullet.id} className="mt-4 p-4 bg-gray-50 rounded">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold text-red-600">Original:</h4>
                  <p className="text-sm">{bullet.original}</p>
                </div>
                <div>
                  <h4 className="font-semibold text-green-600">Optimized:</h4>
                  {editMode[bullet.id] ? (
                    <textarea 
                      value={editedContent[bullet.id]}
                      onChange={(e) => updateEdit(bullet.id, e.target.value)}
                      className="w-full text-sm"
                    />
                  ) : (
                    <p className="text-sm">{bullet.optimized}</p>
                  )}
                </div>
              </div>
              
              <div className="flex gap-2 mt-2">
                <button onClick={() => acceptBullet(bullet.id)}>
                  ✓ Accept
                </button>
                <button onClick={() => toggleEdit(bullet.id)}>
                  ✏ Edit
                </button>
                <button onClick={() => regenerateBullet(bullet.id)}>
                  ↺ Regenerate
                </button>
              </div>
            </div>
          ))}
        </div>
      ))}
      
      <div className="flex justify-between">
        <button onClick={goBack}>← Back to Selection</button>
        <button onClick={generatePDF}>Generate PDF →</button>
      </div>
    </div>
  );
};
```

---

# Phase 5: PDF Generation System

## 5.1 LaTeX Template Setup

### Files to Create:
- `backend/templates/jake_resume.tex` - Jinja2 template version of provided resume
- `backend/app/services/latex_service.py` - Template rendering service

### Template Conversion:
```latex
% backend/templates/jake_resume.tex
\documentclass[letterpaper,11pt]{article}

% [Include all the original preamble and styling]

\begin{document}

%----------HEADING----------
\begin{center}
    \textbf{\Huge \scshape {{ personal_info.name }}} \\ \vspace{1pt}
    \small {{ personal_info.phone }} $|$ \href{mailto:{{ personal_info.email }}}{\underline{{{ personal_info.email }}}} $|$ 
    \href{{{ personal_info.linkedin }}}{\underline{linkedin.com/in/...}} $|$
    \href{{{ personal_info.github }}}{\underline{github.com/...}}
\end{center}

%-----------EDUCATION-----------
\section{Education}
  \resumeSubHeadingListStart
    {% for edu in education %}
    \resumeSubheading
      {{{ edu.institution }}}{{{ edu.location }}}
      {{{ edu.degree }}}{{{ edu.duration }}}
    {% endfor %}
  \resumeSubHeadingListEnd

%-----------EXPERIENCE-----------
\section{Experience}
  \resumeSubHeadingListStart
    {% for exp in selected_experiences %}
    \resumeSubheading
      {{{ exp.title }}}{{{ exp.duration }}}
      {{{ exp.company }}}{{{ exp.location }}}
      \resumeItemListStart
        {% for bullet in exp.optimized_bullet_points %}
        \resumeItem{{{ bullet.optimized_text }}}
        {% endfor %}
      \resumeItemListEnd
    {% endfor %}
  \resumeSubHeadingListEnd

%-----------PROJECTS-----------
\section{Projects}
    \resumeSubHeadingListStart
      {% for project in selected_projects %}
      \resumeProjectHeading
          {\textbf{{{ project.name }}} $|$ \emph{{{ project.technologies }}}}{{{ project.duration }}}
          \resumeItemListStart
            {% for bullet in project.optimized_bullet_points %}
            \resumeItem{{{ bullet.optimized_text }}}
            {% endfor %}
          \resumeItemListEnd
      {% endfor %}
    \resumeSubHeadingListEnd

%-----------TECHNICAL SKILLS-----------
\section{Technical Skills}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \small{\item{
     \textbf{Languages}{: {{ technical_skills.languages | join(', ') }}} \\
     \textbf{Frameworks}{: {{ technical_skills.frameworks | join(', ') }}} \\
     \textbf{Developer Tools}{: {{ technical_skills.developer_tools | join(', ') }}} \\
     \textbf{Libraries}{: {{ technical_skills.libraries | join(', ') }}}
    }}
 \end{itemize}

\end{document}
```

## 5.2 PDF Generation Pipeline

### `backend/app/services/pdf_service.py`:
```python
from jinja2 import Environment, FileSystemLoader
import subprocess
import os
from pathlib import Path

class PDFService:
    def __init__(self):
        self.template_dir = Path("backend/templates")
        self.output_dir = Path("backend/data/resume_versions")
        self.jinja_env = Environment(loader=FileSystemLoader(self.template_dir))
    
    def generate_resume_pdf(
        self,
        job_id: str,
        personal_info: PersonalInfo,
        education: List[Education],
        technical_skills: TechnicalSkills,
        selected_experiences: List[Experience],
        selected_projects: List[Project],
        optimized_content: OptimizedContent
    ) -> str:
        """
        Generate PDF from LaTeX template
        Returns: file path to generated PDF
        """
        
        # 1. Prepare template data
        template_data = {
            "personal_info": personal_info,
            "education": education,
            "technical_skills": technical_skills,
            "selected_experiences": self._merge_optimized_content(
                selected_experiences, 
                optimized_content.experiences
            ),
            "selected_projects": self._merge_optimized_content(
                selected_projects, 
                optimized_content.projects
            )
        }
        
        # 2. Render LaTeX template
        template = self.jinja_env.get_template("jake_resume.tex")
        latex_content = template.render(**template_data)
        
        # 3. Write to temporary .tex file
        tex_filename = f"resume_{job_id}_{int(time.time())}.tex"
        tex_path = self.output_dir / tex_filename
        
        with open(tex_path, 'w') as f:
            f.write(latex_content)
        
        # 4. Compile with pdflatex
        pdf_path = self._compile_latex(tex_path)
        
        # 5. Clean up temporary files
        self._cleanup_temp_files(tex_path)
        
        return str(pdf_path)
    
    def _compile_latex(self, tex_path: Path) -> Path:
        """Compile LaTeX file to PDF using pdflatex"""
        try:
            # Run pdflatex twice for proper references
            for _ in range(2):
                result = subprocess.run([
                    'pdflatex', 
                    '-output-directory', str(tex_path.parent),
                    '-interaction=nonstopmode',
                    str(tex_path)
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    raise Exception(f"LaTeX compilation failed: {result.stderr}")
            
            pdf_path = tex_path.with_suffix('.pdf')
            if not pdf_path.exists():
                raise Exception("PDF was not generated")
                
            return pdf_path
            
        except Exception as e:
            raise Exception(f"PDF generation failed: {str(e)}")
    
    def _merge_optimized_content(
        self, 
        original_items: List[Union[Experience, Project]], 
        optimized_content: Dict[str, Any]
    ) -> List[Dict]:
        """Merge original data with optimized bullet points"""
        result = []
        for item in original_items:
            item_dict = item.dict()
            if item.id in optimized_content:
                # Replace bullet points with optimized versions
                item_dict['optimized_bullet_points'] = optimized_content[item.id]['optimized_bullet_points']
            else:
                # Use original bullet points if not optimized
                item_dict['optimized_bullet_points'] = [
                    {"optimized_text": bp.text} for bp in item.bullet_points
                ]
            result.append(item_dict)
        return result
    
    def _cleanup_temp_files(self, tex_path: Path):
        """Remove auxiliary LaTeX files"""
        aux_extensions = ['.aux', '.log', '.out', '.fdb_latexmk', '.fls']
        for ext in aux_extensions:
            aux_file = tex_path.with_suffix(ext)
            if aux_file.exists():
                aux_file.unlink()
```

## 5.3 PDF Download & Storage

### File Naming Convention:
```
backend/data/resume_versions/
├── {name}_{job_id}_{timestamp}.pdf
├── job_123_optimized.json          # Optimization metadata
└── job_456_optimized.json
```

### API Endpoint for PDF Download:
```python
@app.get("/api/resume/download/{job_id}")
async def download_resume_pdf(job_id: str):
    """Download generated PDF for specific job"""
    pdf_path = get_pdf_path_for_job(job_id)
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF not found")
    
    return FileResponse(
        pdf_path,
        media_type='application/pdf',
        filename=f"resume_{job_id}.pdf"
    )
```

---

# Phase 6: Integration & Polish

## 6.1 Navigation Enhancement

### Modify `frontend/src/App.tsx`:
```tsx
const App = () => {
  const [currentView, setCurrentView] = useState<'jobs' | 'resume'>('jobs');
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0b1021] via-[#0b1228] to-[#0a0f20] text-slate-100">
      <div className="mx-auto max-w-6xl px-6 py-10">
        {/* Navigation Header */}
        <div className="mb-8 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <div>
              <p className="text-sm uppercase tracking-[0.3em] text-slate-500">Dashboard</p>
              <h1 className="mt-2 text-3xl font-semibold text-white">PlsFindMeAJob</h1>
            </div>
            
            {/* Navigation Tabs */}
            <nav className="flex gap-2">
              <button
                onClick={() => setCurrentView('jobs')}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  currentView === 'jobs'
                    ? 'bg-indigo-500/20 text-white border border-indigo-500/50'
                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                }`}
              >
                Job Dashboard
              </button>
              <button
                onClick={() => setCurrentView('resume')}
                className={`px-4 py-2 rounded-lg font-medium transition ${
                  currentView === 'resume'
                    ? 'bg-indigo-500/20 text-white border border-indigo-500/50'
                    : 'text-slate-400 hover:text-white hover:bg-white/5'
                }`}
              >
                Resume Builder
              </button>
            </nav>
          </div>
        </div>

        {/* Content */}
        {currentView === 'jobs' ? <JobDashboard /> : <ResumeBuilder />}
      </div>
    </div>
  );
};
```

## 6.2 State Management

### Resume Data Flow:
```tsx
// frontend/src/hooks/useResume.ts
export const useResume = () => {
  const [resume, setResume] = useState<Resume | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadResume = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/resume');
      if (response.ok) {
        const data = await response.json();
        setResume(data);
      } else {
        // Initialize empty resume if none exists
        setResume(createEmptyResume());
      }
    } catch (err) {
      setError('Failed to load resume');
    } finally {
      setLoading(false);
    }
  };

  const saveResume = async (resumeData: Resume) => {
    setLoading(true);
    try {
      const response = await fetch('/api/resume', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(resumeData)
      });
      
      if (response.ok) {
        setResume(resumeData);
        // Show success notification
      } else {
        throw new Error('Failed to save resume');
      }
    } catch (err) {
      setError('Failed to save resume');
    } finally {
      setLoading(false);
    }
  };

  return { resume, loading, error, loadResume, saveResume };
};
```

## 6.3 Error Handling & UX Improvements

### Loading States:
- Resume data loading spinner
- AI optimization progress indicator
- PDF generation progress bar
- Auto-save status indicator

### Error Recovery:
- API failure fallbacks
- Validation error handling
- LaTeX compilation error messages
- OpenRouter API error handling

### Success Notifications:
- Resume saved successfully
- PDF generated and ready for download
- Optimization completed
- Content auto-saved

### Progressive Enhancement:
- Auto-save every 30 seconds while editing
- Keyboard shortcuts for common actions
- Undo/redo functionality for content changes
- Draft mode vs. finalized mode

---

# Implementation Checklist

## Backend Tasks:
- [ ] Create Pydantic models in `models/resume.py`
- [ ] Implement resume service with file I/O operations
- [ ] Build scoring algorithm with keyword/technology matching
- [ ] Integrate OpenRouter API for content optimization
- [ ] Convert Jake resume template to Jinja2
- [ ] Implement LaTeX PDF compilation service
- [ ] Add all resume API endpoints to main.py
- [ ] Set up environment variables for OpenRouter
- [ ] Create resume storage directories
- [ ] Add error handling and logging

## Frontend Tasks:
- [ ] Create resume builder main page component
- [ ] Build collapsible section components
- [ ] Implement CRUD forms for experiences/projects
- [ ] Create job optimization workflow components
- [ ] Build content selection interface with override
- [ ] Implement optimization review and editing
- [ ] Add PDF preview and download functionality
- [ ] Create resume data hooks
- [ ] Add navigation integration to main app
- [ ] Implement loading states and error handling

## Integration Tasks:
- [ ] Connect resume builder to job dashboard
- [ ] Test end-to-end optimization workflow
- [ ] Verify PDF generation with real data
- [ ] Test OpenRouter API integration
- [ ] Validate LaTeX template with various inputs
- [ ] Set up file storage and permissions
- [ ] Test mobile responsiveness
- [ ] Performance testing with large resumes

## Testing & Polish:
- [ ] Create sample resume data for testing
- [ ] Test scoring algorithm accuracy
- [ ] Verify AI optimization quality
- [ ] Test PDF generation edge cases
- [ ] User experience testing
- [ ] Cross-browser compatibility
- [ ] Performance optimization
- [ ] Documentation and README updates

---

# Future Enhancements (Post-MVP)

## Advanced Features:
- Multiple resume templates (beyond Jake resume)
- ATS (Applicant Tracking System) optimization scoring
- Resume analytics and improvement suggestions
- Integration with job application tracking
- Bulk optimization for multiple jobs
- Resume version comparison tool
- Export to other formats (Word, plain text)
- Resume sharing and collaboration features

## AI Improvements:
- Industry-specific optimization models
- Role-level aware optimization (junior vs senior)
- Company culture adaptation
- Achievement quantification suggestions
- Skill gap analysis based on job requirements
- Automated keyword extraction improvement

## UX Enhancements:
- Drag-and-drop resume section reordering
- Real-time collaboration on resume content
- Resume templates and themes
- Mobile app for quick edits
- Integration with LinkedIn for data import
- Resume performance analytics

---

# Technical Questions & Decisions

## Immediate Decisions Needed:
1. **OpenRouter Model**: Which specific model? (GPT-4, Claude 3.5 Sonnet, etc.)
2. **LaTeX Dependencies**: Confirm pdflatex installation or provide setup guide
3. **Sample Data**: Should we create example resume data for testing?
4. **Keyword Extraction**: Automatic (AI-based) or manual user tagging?
5. **Optimization Style**: Conservative terminology alignment vs. more aggressive rewrites?

## Architecture Decisions:
6. **Multi-user Support**: Design for single-user now, but consider multi-user later?
7. **Data Backup**: Should we implement resume backup/restore functionality?
8. **API Versioning**: Keep resume APIs under `/api/v2/` or use `/api/`?
9. **File Storage**: Organize by user ID for future multi-user support?
10. **Caching**: Should we cache optimization results to avoid repeated API calls?

---

# Getting Started

## Prerequisites:
- Python 3.9+ with FastAPI dependencies
- Node.js 18+ for React frontend  
- pdflatex for PDF generation
- OpenRouter API key
- Git for version control

## Quick Start:
1. Review this roadmap thoroughly
2. Set up development environment
3. Create OpenRouter API account and get key
4. Start with Phase 1: Backend Foundation
5. Implement in order: Backend → Frontend → Integration
6. Test each phase before moving to next

## Development Order:
1. **Week 1**: Phase 1 - Backend models and basic API
2. **Week 2**: Phase 2 - Frontend components and basic UI
3. **Week 3**: Phase 3 - Core resume builder functionality
4. **Week 4**: Phase 4 - AI optimization integration  
5. **Week 5**: Phase 5 - PDF generation system
6. **Week 6**: Phase 6 - Integration, testing, and polish

---

*This roadmap serves as a comprehensive guide for building the resume optimization system. Each phase can be implemented incrementally, allowing for testing and iteration at each step.*
