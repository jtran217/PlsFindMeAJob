import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useResume } from '../hooks/useResume.ts'
import { useToast } from '../hooks/useToast.ts'
import SuccessBanner from '../components/SuccessBanner.tsx'
import FieldError from '../components/FieldError.tsx'
import ToastContainer from '../components/ToastContainer.tsx'
import { 
  SkillRating, 
  EnhancedTextarea, 
  SectionToggle, 
  DateInput 
} from '../components/ResumeComponents.tsx'
import type { ProficiencyLevel, FluencyLevel } from '../types/resume'
import { proficiencyLevels, socialNetworks, fluencyLevels } from '../types/resume'

export default function EnhancedProfilePage() {
  const navigate = useNavigate()
  const {
    resume,
    loading,
    saving,
    error,
    validationErrors,
    saveResume,
    updateBasics,
    updateSummary,
    addExperience,
    updateExperience,
    removeExperience,
    addEducation,
    updateEducation,
    removeEducation,
    addProject,
    updateProject,
    removeProject,
    addSkill,
    updateSkill,
    removeSkill,
    addProfile,
    updateProfile,
    removeProfile,
    addLanguage,
    updateLanguage,
    removeLanguage,
    addCertification,
    updateCertification,
    removeCertification,
    addAward,
    updateAward,
    removeAward,
    addInterest,
    updateInterest,
    removeInterest,
    updateSectionVisibility,
    clearErrors
  } = useResume()
  
  const { toasts, showError, removeToast } = useToast()
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null)

  const handleSave = async () => {
    clearErrors()
    setSaveSuccess(null)
    
    const result = await saveResume()
    
    if (result) {
      setSaveSuccess('Resume saved successfully!')
      setTimeout(() => setSaveSuccess(null), 3000)
    } else {
      showError(error || 'Failed to save resume')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-linear-to-br from-[#0b1021] via-[#0b1228] to-[#0a0f20] text-slate-100 py-10">
        <div className="mx-auto max-w-4xl px-6 flex items-center justify-center">
          <div className="flex items-center gap-3">
            <svg className="w-6 h-6 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span>Loading Resume...</span>
          </div>
        </div>
      </div>
    )
  }

  if (!resume) {
    return (
      <div className="min-h-screen bg-linear-to-br from-[#0b1021] via-[#0b1228] to-[#0a0f20] text-slate-100 py-10">
        <div className="mx-auto max-w-4xl px-6">
          <div className="text-center">
            <p className="text-red-400">Failed to load resume data</p>
            <button onClick={() => window.location.reload()} className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded">
              Retry
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-linear-to-br from-[#0b1021] via-[#0b1228] to-[#0a0f20] text-slate-100 py-10">
      <div className="mx-auto max-w-5xl px-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Enhanced Resume Builder</h1>
            <p className="text-sm text-slate-400">Create your professional resume with our optimization system.</p>
          </div>
          <button 
            onClick={() => navigate('/')} 
            className="rounded border border-slate-700 bg-white/5 px-4 py-2 text-sm text-slate-200 hover:bg-white/10 transition-colors"
          >
            Back to Dashboard
          </button>
        </div>

        <div className="space-y-8">
          <section className="rounded-2xl border border-slate-800/80 bg-white/5 p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <span className="w-2 h-2 bg-indigo-500 rounded-full"></span>
              Basic Information
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Full Name</label>
                <input 
                  value={resume.data.basics.name} 
                  onChange={(e) => updateBasics({ name: e.target.value })}
                  className={`w-full rounded border px-3 py-2 text-white ${
                    validationErrors?.['data.basics.name'] 
                      ? 'border-red-500/50 bg-red-500/5 focus:border-red-400' 
                      : 'border-slate-700 bg-[#071026] focus:border-indigo-500'
                  }`}
                  placeholder="Your full name"
                />
                <FieldError error={validationErrors?.['data.basics.name']} />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Professional Headline</label>
                <input 
                  value={resume.data.basics.headline} 
                  onChange={(e) => updateBasics({ headline: e.target.value })}
                  className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                  placeholder="e.g., Senior Software Developer"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Email</label>
                <input 
                  value={resume.data.basics.email} 
                  onChange={(e) => updateBasics({ email: e.target.value })}
                  type="email"
                  className={`w-full rounded border px-3 py-2 text-white ${
                    validationErrors?.['data.basics.email'] 
                      ? 'border-red-500/50 bg-red-500/5 focus:border-red-400' 
                      : 'border-slate-700 bg-[#071026] focus:border-indigo-500'
                  }`}
                  placeholder="your.email@example.com"
                />
                <FieldError error={validationErrors?.['data.basics.email']} />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Phone</label>
                <input 
                  value={resume.data.basics.phone} 
                  onChange={(e) => updateBasics({ phone: e.target.value })}
                  className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                  placeholder="(555) 123-4567"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Location</label>
                <input 
                  value={resume.data.basics.location} 
                  onChange={(e) => updateBasics({ location: e.target.value })}
                  className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                  placeholder="City, State"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">Website URL</label>
                <input 
                  value={resume.data.basics.website.url} 
                  onChange={(e) => updateBasics({ 
                    website: { 
                      ...resume.data.basics.website, 
                      url: e.target.value,
                      label: e.target.value ? 'Personal Website' : ''
                    } 
                  })}
                  className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                  placeholder="https://yourwebsite.com"
                />
              </div>
            </div>
          </section>

          <section className="rounded-2xl border border-slate-800/80 bg-white/5 p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              Professional Summary
            </h2>
            
            <EnhancedTextarea
              value={resume.data.summary.content}
              onChange={(value) => updateSummary(value)}
              placeholder="Write a compelling professional summary that highlights your key skills and experience..."
              rows={4}
              maxLength={500}
              showTips={true}
              helpText="Keep it concise (2-3 sentences) and focus on your unique value proposition."
            />
          </section>

          <section className="rounded-2xl border border-slate-800/80 bg-white/5 p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
              Social Profiles
            </h2>
            
            <div className="space-y-4">
              {resume.data.sections.profiles.items.map((profile) => (
                <div key={profile.id} className="rounded border border-slate-700 bg-[#061024] p-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Network</label>
                      <select
                        value={profile.network}
                        onChange={(e) => updateProfile(profile.id, { network: e.target.value })}
                        className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                      >
                        <option value="">Select network...</option>
                        {socialNetworks.map(network => (
                          <option key={network} value={network}>{network}</option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Username</label>
                      <input 
                        value={profile.username} 
                        onChange={(e) => updateProfile(profile.id, { username: e.target.value })}
                        className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                        placeholder="your-username"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">URL</label>
                      <input 
                        value={profile.website.url} 
                        onChange={(e) => updateProfile(profile.id, { 
                          website: { ...profile.website, url: e.target.value }
                        })}
                        className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                        placeholder="https://..."
                      />
                    </div>
                  </div>
                  <div className="mt-3 flex justify-end">
                    <button 
                      onClick={() => removeProfile(profile.id)}
                      className="text-sm text-rose-400 hover:underline"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}
              
              <button 
                onClick={addProfile}
                className="w-full rounded border border-slate-700 bg-white/5 px-3 py-2 text-sm text-slate-200 hover:bg-white/10 transition-colors"
              >
                + Add Social Profile
              </button>
            </div>
          </section>

          <section className="rounded-2xl border border-slate-800/80 bg-white/5 p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <span className="w-2 h-2 bg-purple-500 rounded-full"></span>
              Work Experience
            </h2>
            
            <div className="space-y-4">
              {resume.data.sections.experience.items.map((exp) => (
                <div key={exp.id} className="rounded border border-slate-700 bg-[#061024] p-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Position</label>
                      <input 
                        value={exp.position} 
                        onChange={(e) => updateExperience(exp.id, { position: e.target.value })}
                        className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                        placeholder="Job Title"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Company</label>
                      <input 
                        value={exp.company} 
                        onChange={(e) => updateExperience(exp.id, { company: e.target.value })}
                        className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                        placeholder="Company Name"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Location</label>
                      <input 
                        value={exp.location} 
                        onChange={(e) => updateExperience(exp.id, { location: e.target.value })}
                        className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                        placeholder="City, State"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">Period</label>
                      <DateInput
                        value={exp.period}
                        onChange={(period) => updateExperience(exp.id, { period })}
                        placeholder="Jan 2020 - Present"
                        allowPresent={true}
                      />
                    </div>
                  </div>
                  
                  <div className="mb-4">
                    <EnhancedTextarea
                      value={exp.description}
                      onChange={(description) => updateExperience(exp.id, { description })}
                      placeholder="Describe your key responsibilities and achievements..."
                      rows={4}
                      maxLength={1000}
                      showTips={true}
                      label="Job Description"
                      helpText="Focus on quantifiable achievements and use action verbs"
                    />
                  </div>
                  
                  <div className="flex justify-end">
                    <button 
                      onClick={() => removeExperience(exp.id)}
                      className="text-sm text-rose-400 hover:underline"
                    >
                      Remove Experience
                    </button>
                  </div>
                </div>
              ))}
              
              <button 
                onClick={addExperience}
                className="w-full rounded border border-slate-700 bg-white/5 px-3 py-2 text-sm text-slate-200 hover:bg-white/10 transition-colors"
              >
                + Add Work Experience
              </button>
            </div>
          </section>

          <section className="rounded-2xl border border-slate-800/80 bg-white/5 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <span className="w-2 h-2 bg-yellow-500 rounded-full"></span>
                Technical Skills
              </h2>
              <SectionToggle
                title="Skills"
                hidden={resume.data.sections.skills.hidden}
                onToggle={(hidden) => updateSectionVisibility('skills', hidden)}
                itemCount={resume.data.sections.skills.items.length}
              />
            </div>
            
            {!resume.data.sections.skills.hidden && (
              <div className="space-y-4">
                {resume.data.sections.skills.items.map((skill) => (
                  <div key={skill.id} className="rounded border border-slate-700 bg-[#061024] p-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Skill Name</label>
                        <input 
                          value={skill.name} 
                          onChange={(e) => updateSkill(skill.id, { name: e.target.value })}
                          className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                          placeholder="e.g., React"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Proficiency Level</label>
                        <select
                          value={skill.proficiency}
                          onChange={(e) => {
                            const level = proficiencyLevels.indexOf(e.target.value as ProficiencyLevel) + 1
                            updateSkill(skill.id, { 
                              proficiency: e.target.value as ProficiencyLevel,
                              level
                            })
                          }}
                          className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                        >
                          {proficiencyLevels.map(level => (
                            <option key={level} value={level}>{level}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                    
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-slate-300 mb-2">Visual Rating</label>
                      <SkillRating
                        level={skill.level}
                        onChange={(level) => updateSkill(skill.id, { level })}
                        type="bars"
                      />
                    </div>
                    
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-slate-300 mb-2">Related Keywords</label>
                      <input 
                        value={skill.keywords.join(', ')} 
                        onChange={(e) => updateSkill(skill.id, { 
                          keywords: e.target.value.split(',').map(k => k.trim()).filter(Boolean)
                        })}
                        className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                        placeholder="frameworks, tools, libraries"
                      />
                    </div>
                    
                    <div className="flex justify-end">
                      <button 
                        onClick={() => removeSkill(skill.id)}
                        className="text-sm text-rose-400 hover:underline"
                      >
                        Remove Skill
                      </button>
                    </div>
                  </div>
                ))}
                
                <button 
                  onClick={addSkill}
                  className="w-full rounded border border-slate-700 bg-white/5 px-3 py-2 text-sm text-slate-200 hover:bg-white/10 transition-colors"
                >
                  + Add Technical Skill
                </button>
              </div>
            )}
          </section>

          <section className="rounded-2xl border border-slate-800/80 bg-white/5 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <span className="w-2 h-2 bg-emerald-500 rounded-full"></span>
                Education
              </h2>
              <SectionToggle
                title="Education"
                hidden={resume.data.sections.education.hidden}
                onToggle={(hidden) => updateSectionVisibility('education', hidden)}
                itemCount={resume.data.sections.education.items.length}
              />
            </div>
            
            {!resume.data.sections.education.hidden && (
              <div className="space-y-4">
                {resume.data.sections.education.items.map((edu) => (
                  <div key={edu.id} className="rounded border border-slate-700 bg-[#061024] p-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">School/Institution</label>
                        <input 
                          value={edu.school} 
                          onChange={(e) => updateEducation(edu.id, { school: e.target.value })}
                          className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                          placeholder="University or School Name"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Degree</label>
                        <input 
                          value={edu.degree} 
                          onChange={(e) => updateEducation(edu.id, { degree: e.target.value })}
                          className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                          placeholder="e.g., Bachelor of Science"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Field of Study</label>
                        <input 
                          value={edu.area} 
                          onChange={(e) => updateEducation(edu.id, { area: e.target.value })}
                          className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                          placeholder="e.g., Computer Science"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Grade/GPA</label>
                        <input 
                          value={edu.grade} 
                          onChange={(e) => updateEducation(edu.id, { grade: e.target.value })}
                          className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                          placeholder="e.g., 3.8 GPA"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Location</label>
                        <input 
                          value={edu.location} 
                          onChange={(e) => updateEducation(edu.id, { location: e.target.value })}
                          className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                          placeholder="City, State"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Period</label>
                        <DateInput
                          value={edu.period}
                          onChange={(value) => updateEducation(edu.id, { period: value })}
                          placeholder="Aug 2020 - May 2024"
                        />
                      </div>
                    </div>
                    
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-slate-300 mb-2">Description/Coursework</label>
                      <EnhancedTextarea
                        value={edu.description}
                        onChange={(value) => updateEducation(edu.id, { description: value })}
                        placeholder="Relevant coursework, achievements, or activities..."
                        maxLength={500}
                        showTips={true}
                        helpText="Highlight relevant coursework, academic achievements, projects, and extracurricular activities."
                      />
                    </div>
                    
                    <div className="flex justify-end">
                      <button 
                        onClick={() => removeEducation(edu.id)}
                        className="text-sm text-rose-400 hover:underline"
                      >
                        Remove Education
                      </button>
                    </div>
                  </div>
                ))}
                
                <button 
                  onClick={addEducation}
                  className="w-full rounded border border-slate-700 bg-white/5 px-3 py-2 text-sm text-slate-200 hover:bg-white/10 transition-colors"
                >
                  + Add Education
                </button>
              </div>
            )}
          </section>

          <section className="rounded-2xl border border-slate-800/80 bg-white/5 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
                Projects
              </h2>
              <SectionToggle
                title="Projects"
                hidden={resume.data.sections.projects.hidden}
                onToggle={(hidden) => updateSectionVisibility('projects', hidden)}
                itemCount={resume.data.sections.projects.items.length}
              />
            </div>
            
            {!resume.data.sections.projects.hidden && (
              <div className="space-y-4">
                {resume.data.sections.projects.items.map((project) => (
                  <div key={project.id} className="rounded border border-slate-700 bg-[#061024] p-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Project Name</label>
                        <input 
                          value={project.name} 
                          onChange={(e) => updateProject(project.id, { name: e.target.value })}
                          className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                          placeholder="Project Title"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Period</label>
                        <DateInput
                          value={project.period}
                          onChange={(value) => updateProject(project.id, { period: value })}
                          placeholder="Jan 2023 - Mar 2023"
                        />
                      </div>
                    </div>
                    
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-slate-300 mb-2">Project URL</label>
                      <input 
                        value={project.website.url} 
                        onChange={(e) => updateProject(project.id, { 
                          website: { ...project.website, url: e.target.value }
                        })}
                        className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                        placeholder="https://github.com/username/project or https://project-demo.com"
                      />
                    </div>
                    
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-slate-300 mb-2">Description</label>
                      <EnhancedTextarea
                        value={project.description}
                        onChange={(value) => updateProject(project.id, { description: value })}
                        placeholder="Describe the project, technologies used, and your role..."
                        maxLength={800}
                        showTips={true}
                        helpText="Focus on the problem you solved, technologies used, your specific contributions, and measurable outcomes."
                      />
                    </div>
                    
                    <div className="flex justify-end">
                      <button 
                        onClick={() => removeProject(project.id)}
                        className="text-sm text-rose-400 hover:underline"
                      >
                        Remove Project
                      </button>
                    </div>
                  </div>
                ))}
                
                <button 
                  onClick={addProject}
                  className="w-full rounded border border-slate-700 bg-white/5 px-3 py-2 text-sm text-slate-200 hover:bg-white/10 transition-colors"
                >
                  + Add Project
                </button>
              </div>
            )}
          </section>

          <section className="rounded-2xl border border-slate-800/80 bg-white/5 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <span className="w-2 h-2 bg-cyan-500 rounded-full"></span>
                Languages
              </h2>
              <SectionToggle
                title="Languages"
                hidden={resume.data.sections.languages.hidden}
                onToggle={(hidden) => updateSectionVisibility('languages', hidden)}
                itemCount={resume.data.sections.languages.items.length}
              />
            </div>
            
            {!resume.data.sections.languages.hidden && (
              <div className="space-y-4">
                {resume.data.sections.languages.items.map((language) => (
                  <div key={language.id} className="rounded border border-slate-700 bg-[#061024] p-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Language</label>
                        <input 
                          value={language.language} 
                          onChange={(e) => updateLanguage(language.id, { language: e.target.value })}
                          className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                          placeholder="e.g., Spanish"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Fluency Level</label>
                        <select
                          value={language.fluency}
                          onChange={(e) => {
                            const level = fluencyLevels.indexOf(e.target.value as FluencyLevel) + 1
                            updateLanguage(language.id, { 
                              fluency: e.target.value as FluencyLevel,
                              level
                            })
                          }}
                          className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                        >
                          {fluencyLevels.map(level => (
                            <option key={level} value={level}>{level}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                    
                    <div className="mb-4">
                      <label className="block text-sm font-medium text-slate-300 mb-2">Proficiency Rating</label>
                      <SkillRating
                        level={language.level}
                        onChange={(level) => updateLanguage(language.id, { level })}
                        type="stars"
                      />
                    </div>
                    
                    <div className="flex justify-end">
                      <button 
                        onClick={() => removeLanguage(language.id)}
                        className="text-sm text-rose-400 hover:underline"
                      >
                        Remove Language
                      </button>
                    </div>
                  </div>
                ))}
                
                <button 
                  onClick={addLanguage}
                  className="w-full rounded border border-slate-700 bg-white/5 px-3 py-2 text-sm text-slate-200 hover:bg-white/10 transition-colors"
                >
                  + Add Language
                </button>
              </div>
            )}
          </section>

          <section className="rounded-2xl border border-slate-800/80 bg-white/5 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <span className="w-2 h-2 bg-rose-500 rounded-full"></span>
                Certifications
              </h2>
              <SectionToggle
                title="Certifications"
                hidden={resume.data.sections.certifications.hidden}
                onToggle={(hidden) => updateSectionVisibility('certifications', hidden)}
                itemCount={resume.data.sections.certifications.items.length}
              />
            </div>
            
            {!resume.data.sections.certifications.hidden && (
              <div className="space-y-4">
                {resume.data.sections.certifications.items.map((cert) => (
                  <div key={cert.id} className="rounded border border-slate-700 bg-[#061024] p-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Certification Title</label>
                        <input 
                          value={cert.title} 
                          onChange={(e) => updateCertification(cert.id, { title: e.target.value })}
                          className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                          placeholder="e.g., AWS Certified Solutions Architect"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Issuing Organization</label>
                        <input 
                          value={cert.issuer} 
                          onChange={(e) => updateCertification(cert.id, { issuer: e.target.value })}
                          className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                          placeholder="e.g., Amazon Web Services"
                        />
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Date Obtained</label>
                        <DateInput
                          value={cert.date}
                          onChange={(date) => updateCertification(cert.id, { date })}
                          placeholder="MM/YYYY"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Verification URL</label>
                        <input 
                          value={cert.website.url} 
                          onChange={(e) => updateCertification(cert.id, { 
                            website: { ...cert.website, url: e.target.value }
                          })}
                          className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                          placeholder="https://verify.certification.com/..."
                        />
                      </div>
                    </div>
                    
                    <div className="mb-4">
                      <EnhancedTextarea
                        value={cert.description}
                        onChange={(desc) => updateCertification(cert.id, { description: desc })}
                        placeholder="Brief description of the certification and its relevance..."
                        rows={2}
                        maxLength={200}
                        label="Description"
                      />
                    </div>
                    
                    <div className="flex justify-end">
                      <button 
                        onClick={() => removeCertification(cert.id)}
                        className="text-sm text-rose-400 hover:underline"
                      >
                        Remove Certification
                      </button>
                    </div>
                  </div>
                ))}
                
                <button 
                  onClick={addCertification}
                  className="w-full rounded border border-slate-700 bg-white/5 px-3 py-2 text-sm text-slate-200 hover:bg-white/10 transition-colors"
                >
                  + Add Certification
                </button>
              </div>
            )}
          </section>

          <section className="rounded-2xl border border-slate-800/80 bg-white/5 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <span className="w-2 h-2 bg-amber-500 rounded-full"></span>
                Awards & Achievements
              </h2>
              <SectionToggle
                title="Awards"
                hidden={resume.data.sections.awards.hidden}
                onToggle={(hidden) => updateSectionVisibility('awards', hidden)}
                itemCount={resume.data.sections.awards.items.length}
              />
            </div>
            
            {!resume.data.sections.awards.hidden && (
              <div className="space-y-4">
                {resume.data.sections.awards.items.map((award) => (
                  <div key={award.id} className="rounded border border-slate-700 bg-[#061024] p-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Award Title</label>
                        <input 
                          value={award.title} 
                          onChange={(e) => updateAward(award.id, { title: e.target.value })}
                          className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                          placeholder="e.g., Employee of the Year"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Awarded By</label>
                        <input 
                          value={award.awarder} 
                          onChange={(e) => updateAward(award.id, { awarder: e.target.value })}
                          className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                          placeholder="e.g., Tech Corp Inc."
                        />
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Date Received</label>
                        <DateInput
                          value={award.date}
                          onChange={(date) => updateAward(award.id, { date })}
                          placeholder="MM/YYYY"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Award URL</label>
                        <input 
                          value={award.website.url} 
                          onChange={(e) => updateAward(award.id, { 
                            website: { ...award.website, url: e.target.value }
                          })}
                          className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                          placeholder="https://company.com/awards..."
                        />
                      </div>
                    </div>
                    
                    <div className="mb-4">
                      <EnhancedTextarea
                        value={award.description}
                        onChange={(desc) => updateAward(award.id, { description: desc })}
                        placeholder="Description of the achievement and its significance..."
                        rows={2}
                        maxLength={300}
                        label="Description"
                      />
                    </div>
                    
                    <div className="flex justify-end">
                      <button 
                        onClick={() => removeAward(award.id)}
                        className="text-sm text-rose-400 hover:underline"
                      >
                        Remove Award
                      </button>
                    </div>
                  </div>
                ))}
                
                <button 
                  onClick={addAward}
                  className="w-full rounded border border-slate-700 bg-white/5 px-3 py-2 text-sm text-slate-200 hover:bg-white/10 transition-colors"
                >
                  + Add Award
                </button>
              </div>
            )}
          </section>

          <section className="rounded-2xl border border-slate-800/80 bg-white/5 p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold flex items-center gap-2">
                <span className="w-2 h-2 bg-pink-500 rounded-full"></span>
                Interests & Hobbies
              </h2>
              <SectionToggle
                title="Interests"
                hidden={resume.data.sections.interests.hidden}
                onToggle={(hidden) => updateSectionVisibility('interests', hidden)}
                itemCount={resume.data.sections.interests.items.length}
              />
            </div>
            
            {!resume.data.sections.interests.hidden && (
              <div className="space-y-4">
                {resume.data.sections.interests.items.map((interest) => (
                  <div key={interest.id} className="rounded border border-slate-700 bg-[#061024] p-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Interest/Hobby</label>
                        <input 
                          value={interest.name} 
                          onChange={(e) => updateInterest(interest.id, { name: e.target.value })}
                          className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                          placeholder="e.g., Photography"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Related Keywords</label>
                        <input 
                          value={interest.keywords.join(', ')} 
                          onChange={(e) => updateInterest(interest.id, { 
                            keywords: e.target.value.split(',').map(k => k.trim()).filter(Boolean)
                          })}
                          className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
                          placeholder="digital photography, nature, travel"
                        />
                      </div>
                    </div>
                    
                    <div className="flex justify-end">
                      <button 
                        onClick={() => removeInterest(interest.id)}
                        className="text-sm text-rose-400 hover:underline"
                      >
                        Remove Interest
                      </button>
                    </div>
                  </div>
                ))}
                
                <button 
                  onClick={addInterest}
                  className="w-full rounded border border-slate-700 bg-white/5 px-3 py-2 text-sm text-slate-200 hover:bg-white/10 transition-colors"
                >
                  + Add Interest
                </button>
              </div>
            )}
          </section>

          {/* Save Button */}
          <div className="flex justify-center">
            <button
              onClick={handleSave}
              disabled={saving}
              className={`px-8 py-3 rounded-lg font-medium transition-all duration-200 ${
                saving
                  ? 'bg-indigo-600/20 text-indigo-300 cursor-not-allowed border border-indigo-600/50'
                  : 'bg-indigo-600 text-white hover:bg-indigo-700 border border-indigo-500'
              }`}
            >
              {saving ? (
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Saving Resume...
                </div>
              ) : (
                'Save Resume'
              )}
            </button>
          </div>

          <SuccessBanner 
            message={saveSuccess || ''}
            isVisible={!!saveSuccess}
            onHide={() => setSaveSuccess(null)}
          />

          {error && (
            <div className="rounded-lg bg-red-500/10 border border-red-500/50 p-4 text-red-400 text-center">
              {error}
            </div>
          )}
        </div>

        <ToastContainer toasts={toasts} onRemove={removeToast} />
      </div>
    </div>
  )
}