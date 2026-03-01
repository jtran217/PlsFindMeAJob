import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import defaultProfile from '../data/profileDefault.json'

const STORAGE_KEY = 'pfm_profile_v1'

export default function ProfilePage() {
  const navigate = useNavigate()
  const [profile, setProfile] = useState(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (raw) return JSON.parse(raw)
    } catch (e) {}
    return defaultProfile
  })

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(profile))
    } catch (e) {}
  }, [profile])

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
              <input value={profile.basics.name} onChange={(e) => setProfile((p:any)=>({...p, basics:{...p.basics, name:e.target.value}}))} className="mt-1 w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white" />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-slate-300">Email</label>
                <input value={profile.basics.email} onChange={(e)=>setProfile((p:any)=>({...p, basics:{...p.basics, email:e.target.value}}))} className="mt-1 w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white" />
              </div>
              <div>
                <label className="text-sm text-slate-300">Phone</label>
                <input value={profile.basics.phone} onChange={(e)=>setProfile((p:any)=>({...p, basics:{...p.basics, phone:e.target.value}}))} className="mt-1 w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white" />
              </div>
            </div>

            <div>
              <label className="text-sm text-slate-300">Skills (comma separated)</label>
              <input value={(profile.skills||[]).join(', ')} onChange={(e)=>setProfile((p:any)=>({...p, skills: e.target.value.split(',').map((s:string)=>s.trim()).filter(Boolean)}))} className="mt-1 w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white" />
            </div>

            <div>
              <label className="text-sm text-slate-300">Experiences</label>
              <div className="mt-2 flex flex-col gap-2">
                {(profile.experiences||[]).map((exp:any, idx:number)=> (
                  <div key={idx} className="rounded border border-slate-700 bg-[#061024] p-3">
                    <input value={exp.position||''} onChange={(e)=>{ const v=e.target.value; setProfile((p:any)=>{ const copy = {...p}; copy.experiences = copy.experiences.map((ee:any,i:number)=> i===idx?{...ee,position:v}:ee); return copy })}} placeholder="Position" className="mb-2 w-full rounded border border-slate-700 bg-transparent px-2 py-1 text-white" />
                    <input value={exp.company||''} onChange={(e)=>{ const v=e.target.value; setProfile((p:any)=>{ const copy = {...p}; copy.experiences = copy.experiences.map((ee:any,i:number)=> i===idx?{...ee,company:v}:ee); return copy })}} placeholder="Company" className="mb-2 w-full rounded border border-slate-700 bg-transparent px-2 py-1 text-white" />
                    <div className="flex gap-2">
                      <input value={exp.start_date||''} onChange={(e)=>{ const v=e.target.value; setProfile((p:any)=>{ const copy = {...p}; copy.experiences = copy.experiences.map((ee:any,i:number)=> i===idx?{...ee,start_date:v}:ee); return copy })}} placeholder="Start date" className="w-full rounded border border-slate-700 bg-transparent px-2 py-1 text-white" />
                      <input value={exp.end_date||''} onChange={(e)=>{ const v=e.target.value; setProfile((p:any)=>{ const copy = {...p}; copy.experiences = copy.experiences.map((ee:any,i:number)=> i===idx?{...ee,end_date:v}:ee); return copy })}} placeholder="End date" className="w-full rounded border border-slate-700 bg-transparent px-2 py-1 text-white" />
                    </div>
                    <div className="mt-2 flex justify-end">
                      <button onClick={()=> setProfile((p:any)=>({...p, experiences: p.experiences.filter((_:any,i:number)=> i!==idx)}))} className="text-sm text-rose-400 hover:underline">Remove</button>
                    </div>
                  </div>
                ))}

                <button onClick={()=> setProfile((p:any)=>({...p, experiences: [...(p.experiences||[]), {}]}))} className="mt-1 w-full rounded border border-slate-700 bg-white/5 px-3 py-2 text-sm text-slate-200">+ Add experience</button>
              </div>
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
          </div>
        </div>
      </div>
    </div>
  )
}
