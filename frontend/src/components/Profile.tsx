import { useNavigate } from 'react-router-dom'

export default function Profile() {
  const navigate = useNavigate()
  return (
    <div className="relative">
      <button
        onClick={() => navigate('/profile')}
        title={"Profile"}
        className="inline-flex items-center gap-2 rounded-full border border-slate-800 bg-white/5 px-3 py-1 text-sm text-slate-200 hover:bg-white/10"
      >
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-600 text-sm font-semibold text-white">
          {"P"}
        </div>
        <span className="hidden sm:inline">{"Profile"}</span>
      </button>

    </div>
  )
}
