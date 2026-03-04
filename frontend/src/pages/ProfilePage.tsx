import { useNavigate } from 'react-router-dom'
import { useProfile } from '../hooks/useProfile.ts'
import { useToast } from '../hooks/useToast.ts'
import SuccessBanner from '../components/SuccessBanner.tsx'
import FieldError from '../components/FieldError.tsx'
import ToastContainer from '../components/ToastContainer.tsx'

export default function ProfilePage() {
  const navigate = useNavigate()
  const {
    profile,
    setProfile,
    isSaving,
    saveSuccess,
    fieldErrors,
    saveProfile,
    clearFeedback
  } = useProfile()
  
  const { toasts, showError, removeToast } = useToast()

  const handleSave = async () => {
    clearFeedback()
    const result = await saveProfile(profile)
    
    if (!result.success && result.message) {
      showError(result.message)
    }
  }

  return (
    <div className="min-h-screen bg-linear-to-br from-[#0b1021] via-[#0b1228] to-[#0a0f20] text-slate-100 py-10">
      <div className="mx-auto max-w-4xl px-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Profile</h1>
            <p className="text-sm text-slate-400">Edit your personal information used for resume generation.</p>
          </div>
          <div>
            <button onClick={() => navigate('/')} className="rounded border border-slate-700 bg-white/5 px-3 py-2 text-sm text-slate-200">Back</button>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800/80 bg-white/5 p-6">
          <div className="grid grid-cols-1 gap-4">
            <div>
              <label className="text-sm text-slate-300">Name</label>
              <input 
                value={profile.basics.name} 
                onChange={(e) => setProfile((p:any)=>({...p, basics:{...p.basics, name:e.target.value}}))} 
                className={`mt-1 w-full rounded border px-3 py-2 text-white ${
                  fieldErrors.name 
                    ? 'border-red-500/50 bg-red-500/5 focus:border-red-400' 
                    : 'border-slate-700 bg-[#071026] focus:border-indigo-500'
                }`}
                aria-invalid={!!fieldErrors.name}
                aria-describedby={fieldErrors.name ? 'name-error' : undefined}
              />
              <FieldError error={fieldErrors.name} />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-slate-300">Email</label>
                <input 
                  value={profile.basics.email} 
                  onChange={(e)=>setProfile((p:any)=>({...p, basics:{...p.basics, email:e.target.value}}))} 
                  type="email"
                  className={`mt-1 w-full rounded border px-3 py-2 text-white ${
                    fieldErrors.email 
                      ? 'border-red-500/50 bg-red-500/5 focus:border-red-400' 
                      : 'border-slate-700 bg-[#071026] focus:border-indigo-500'
                  }`}
                  aria-invalid={!!fieldErrors.email}
                  aria-describedby={fieldErrors.email ? 'email-error' : undefined}
                />
                <FieldError error={fieldErrors.email} />
              </div>
              <div>
                <label className="text-sm text-slate-300">Phone</label>
                <input value={profile.basics.phone} onChange={(e)=>setProfile((p:any)=>({...p, basics:{...p.basics, phone:e.target.value}}))} className="mt-1 w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white" />
              </div>
              <div>
                <label className="text-sm text-slate-300">LinkedIn URL</label>
                <input value={profile.basics.linkedin || ''} onChange={(e)=>setProfile((p:any)=>({...p, basics:{...p.basics, linkedin:e.target.value}}))} placeholder="https://linkedin.com/in/your-profile" className="mt-1 w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white" />
              </div>
              <div>
                <label className="text-sm text-slate-300">GitHub URL</label>
                <input value={profile.basics.github || ''} onChange={(e)=>setProfile((p:any)=>({...p, basics:{...p.basics, github:e.target.value}}))} placeholder="https://github.com/your-username" className="mt-1 w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white" />
              </div>
            </div>

            <div>
              <label className="text-sm text-slate-300">Skills (comma separated)</label>
              <input 
                value={(profile.skills||[]).join(', ')} 
                onChange={(e)=>setProfile((p:any)=>({...p, skills: e.target.value.split(',').map((s:string)=>s.trim()).filter(Boolean)}))} 
                className={`mt-1 w-full rounded border px-3 py-2 text-white ${
                  fieldErrors.skills 
                    ? 'border-red-500/50 bg-red-500/5 focus:border-red-400' 
                    : 'border-slate-700 bg-[#071026] focus:border-indigo-500'
                }`}
                placeholder="React, TypeScript, Python, etc."
                aria-invalid={!!fieldErrors.skills}
                aria-describedby={fieldErrors.skills ? 'skills-error' : undefined}
              />
              <FieldError error={fieldErrors.skills} />
            </div>

            <div>
              <label className="text-sm text-slate-300">Experiences</label>
              <div className="mt-2 flex flex-col gap-2">
                {(profile.experiences||[]).map((exp:any, idx:number)=> (
                  <div key={idx} className="rounded border border-slate-700 bg-[#061024] p-3">
                    <input value={exp.position||''} onChange={(e)=>{ const v=e.target.value; setProfile((p:any)=>{ const copy = {...p}; copy.experiences = copy.experiences.map((ee:any,i:number)=> i===idx?{...ee,position:v}:ee); return copy })}} placeholder="Position" className="mb-2 w-full rounded border border-slate-700 bg-transparent px-2 py-1 text-white focus:border-indigo-500" />
                    <input value={exp.company||''} onChange={(e)=>{ const v=e.target.value; setProfile((p:any)=>{ const copy = {...p}; copy.experiences = copy.experiences.map((ee:any,i:number)=> i===idx?{...ee,company:v}:ee); return copy })}} placeholder="Company" className="mb-2 w-full rounded border border-slate-700 bg-transparent px-2 py-1 text-white focus:border-indigo-500" />
                    <div className="flex gap-2">
                      <input value={exp.start_date||''} onChange={(e)=>{ const v=e.target.value; setProfile((p:any)=>{ const copy = {...p}; copy.experiences = copy.experiences.map((ee:any,i:number)=> i===idx?{...ee,start_date:v}:ee); return copy })}} placeholder="Start date" className="w-full rounded border border-slate-700 bg-transparent px-2 py-1 text-white focus:border-indigo-500" />
                      <input value={exp.end_date||''} onChange={(e)=>{ const v=e.target.value; setProfile((p:any)=>{ const copy = {...p}; copy.experiences = copy.experiences.map((ee:any,i:number)=> i===idx?{...ee,end_date:v}:ee); return copy })}} placeholder="End date" className="w-full rounded border border-slate-700 bg-transparent px-2 py-1 text-white focus:border-indigo-500" />
                    </div>
                    <div className="mt-2 flex justify-end">
                      <button onClick={()=> setProfile((p:any)=>({...p, experiences: p.experiences.filter((_:any,i:number)=> i!==idx)}))} className="text-sm text-rose-400 hover:underline">Remove</button>
                    </div>
                  </div>
                ))}

                <button onClick={()=> setProfile((p:any)=>({...p, experiences: [...(p.experiences||[]), {}]}))} className="mt-1 w-full rounded border border-slate-700 bg-white/5 px-3 py-2 text-sm text-slate-200 hover:bg-white/10 transition-colors">+ Add experience</button>
              </div>
              <FieldError error={fieldErrors.experiences} />
            </div>

            <div>
              <label className="text-sm text-slate-300">Education</label>
              <div className="mt-2 flex flex-col gap-2">
                {(profile.education||[]).map((edu:any, idx:number)=> (
                  <div key={idx} className="rounded border border-slate-700 bg-[#061024] p-3">
                    <input value={edu.institution||''} onChange={(e)=>{ const v=e.target.value; setProfile((p:any)=>{ const copy = {...p}; copy.education = copy.education.map((ee:any,i:number)=> i===idx?{...ee,institution:v}:ee); return copy })}} placeholder="Institution" className="mb-2 w-full rounded border border-slate-700 bg-transparent px-2 py-1 text-white focus:border-indigo-500" />
                    <input value={edu.location||''} onChange={(e)=>{ const v=e.target.value; setProfile((p:any)=>{ const copy = {...p}; copy.education = copy.education.map((ee:any,i:number)=> i===idx?{...ee,location:v}:ee); return copy })}} placeholder="Location" className="mb-2 w-full rounded border border-slate-700 bg-transparent px-2 py-1 text-white focus:border-indigo-500" />
                    <input value={edu.degree||''} onChange={(e)=>{ const v=e.target.value; setProfile((p:any)=>{ const copy = {...p}; copy.education = copy.education.map((ee:any,i:number)=> i===idx?{...ee,degree:v}:ee); return copy })}} placeholder="Degree" className="mb-2 w-full rounded border border-slate-700 bg-transparent px-2 py-1 text-white focus:border-indigo-500" />
                    <div className="flex gap-2 mb-2">
                      <input value={edu.expected_date||''} onChange={(e)=>{ const v=e.target.value; setProfile((p:any)=>{ const copy = {...p}; copy.education = copy.education.map((ee:any,i:number)=> i===idx?{...ee,expected_date:v}:ee); return copy })}} placeholder="Expected Date" className="w-full rounded border border-slate-700 bg-transparent px-2 py-1 text-white focus:border-indigo-500" />
                      <input value={edu.start_date||''} onChange={(e)=>{ const v=e.target.value; setProfile((p:any)=>{ const copy = {...p}; copy.education = copy.education.map((ee:any,i:number)=> i===idx?{...ee,start_date:v}:ee); return copy })}} placeholder="Start Date" className="w-full rounded border border-slate-700 bg-transparent px-2 py-1 text-white focus:border-indigo-500" />
                    </div>
                    <textarea value={edu.coursework||''} onChange={(e)=>{ const v=e.target.value; setProfile((p:any)=>{ const copy = {...p}; copy.education = copy.education.map((ee:any,i:number)=> i===idx?{...ee,coursework:v}:ee); return copy })}} placeholder="Relevant Coursework" className="mb-2 w-full rounded border border-slate-700 bg-transparent px-2 py-1 text-white focus:border-indigo-500" rows={3} />
                    <div className="mt-2 flex justify-end">
                      <button onClick={()=> setProfile((p:any)=>({...p, education: p.education.filter((_:any,i:number)=> i!==idx)}))} className="text-sm text-rose-400 hover:underline">Remove</button>
                    </div>
                  </div>
                ))}

                <button onClick={()=> setProfile((p:any)=>({...p, education: [...(p.education||[]), {}]}))} className="mt-1 w-full rounded border border-slate-700 bg-white/5 px-3 py-2 text-sm text-slate-200 hover:bg-white/10 transition-colors">+ Add education</button>
              </div>
              <FieldError error={fieldErrors.education} />
            </div>

            <div>
              <label className="text-sm text-slate-300">Projects</label>
              <div className="mt-2 flex flex-col gap-2">
                {(profile.projects||[]).map((proj:any, idx:number)=> (
                  <div key={idx} className="rounded border border-slate-700 bg-[#061024] p-3">
                    <input value={proj.name||''} onChange={(e)=>{ const v=e.target.value; setProfile((p:any)=>{ const copy = {...p}; copy.projects = copy.projects.map((pp:any,i:number)=> i===idx?{...pp,name:v}:pp); return copy })}} placeholder="Name" className="mb-2 w-full rounded border border-slate-700 bg-transparent px-2 py-1 text-white" />
                    <textarea value={proj.description||''} onChange={(e)=>{ const v=e.target.value; setProfile((p:any)=>{ const copy = {...p}; copy.projects = copy.projects.map((pp:any,i:number)=> i===idx?{...pp,description:v}:pp); return copy })}} placeholder="Description" className="w-full rounded border border-slate-700 bg-transparent px-2 py-1 text-white" />
                    <div className="mt-2 flex justify-end">
                      <button onClick={()=> setProfile((p:any)=>({...p, projects: p.projects.filter((_:any,i:number)=> i!==idx)}))} className="text-sm text-rose-400 hover:underline">Remove</button>
                    </div>
                  </div>
                ))}

                <button onClick={()=> setProfile((p:any)=>({...p, projects: [...(p.projects||[]), {}]}))} className="mt-1 w-full rounded border border-slate-700 bg-white/5 px-3 py-2 text-sm text-slate-200">+ Add project</button>
              </div>
            </div>
            <div>
              <button
                onClick={handleSave}
                disabled={isSaving}
                className={`mt-3 w-full rounded border px-3 py-2 text-sm font-medium transition-all duration-200 ${
                  isSaving
                    ? 'border-indigo-600/50 bg-indigo-600/20 text-indigo-300 cursor-not-allowed'
                    : 'border-slate-700 bg-white/10 text-slate-200 hover:bg-white/20 hover:border-slate-600'
                }`}
                aria-disabled={isSaving}
              >
                {isSaving ? (
                  <div className="flex items-center justify-center gap-2">
                    <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="m4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span>Saving Profile...</span>
                  </div>
                ) : (
                  'Save Profile'
                )}
              </button>
              
              {/* Success Banner */}
              <SuccessBanner 
                message={saveSuccess || ''}
                isVisible={!!saveSuccess}
                onHide={clearFeedback}
              />
            </div>
          </div>
        </div>

        {/* Toast Container */}
        <ToastContainer toasts={toasts} onRemove={removeToast} />
      </div>
    </div>
  )
}
