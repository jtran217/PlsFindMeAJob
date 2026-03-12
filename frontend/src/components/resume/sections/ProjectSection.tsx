import type { Project } from '../../../types/Resume'

interface ProjectSectionProps {
  data: Project[]
  expanded: boolean
  onToggle: () => void
  onChange: (updated: Project[]) => void
  onAdd: () => void
  onEdit: (id: string) => void
}

export function ProjectSection({
  data,
  expanded,
  onToggle,
  onChange,
  onAdd,
  onEdit,
}: ProjectSectionProps) {
  const removeEntry = (id: string) => {
    onChange(data.filter((p) => p.id !== id))
  }

  return (
    <div className="rounded-2xl border border-slate-800/80 bg-white/5 shadow-[0_30px_80px_-60px_rgba(0,0,0,0.65)]">
      <button
        onClick={onToggle}
        className="flex w-full items-center justify-between px-6 py-4 text-left transition hover:bg-white/5"
      >
        <div>
          <p className="text-xs uppercase tracking-[0.25em] text-slate-500">Resume</p>
          <p className="mt-0.5 text-base font-semibold text-white">
            Projects
            <span className="ml-2 rounded-lg bg-slate-800 px-2 py-0.5 text-xs font-semibold text-slate-300">
              {data.length}
            </span>
          </p>
        </div>
        <span className={`text-slate-400 transition-transform duration-200 ${expanded ? 'rotate-180' : ''}`}>
          ▼
        </span>
      </button>

      {expanded && (
        <div className="border-t border-slate-800/70 px-6 py-5 space-y-3">
          {data.map((project) => (
            <div
              key={project.id}
              className="flex items-start justify-between gap-3 rounded-xl border border-slate-800/70 bg-white/5 p-4"
            >
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold text-white truncate">
                  {project.name || <span className="italic text-slate-500">Unnamed project</span>}
                </p>
                {project.technologies && (
                  <p className="text-xs text-indigo-300/70">{project.technologies}</p>
                )}
                <p className="mt-0.5 text-xs text-slate-500">{project.duration}</p>
                <p className="mt-1.5 text-xs text-slate-500">
                  {project.bullet_points.length} bullet{project.bullet_points.length !== 1 ? 's' : ''}
                </p>
              </div>
              <div className="flex gap-2 shrink-0">
                <button
                  onClick={() => onEdit(project.id)}
                  className="rounded-lg border border-slate-700 bg-white/5 px-3 py-1 text-xs text-slate-300 transition hover:border-slate-500 hover:text-white"
                >
                  Edit
                </button>
                <button
                  onClick={() => removeEntry(project.id)}
                  className="rounded-lg border border-red-900/50 bg-red-900/10 px-3 py-1 text-xs text-red-400 transition hover:bg-red-900/20"
                >
                  Remove
                </button>
              </div>
            </div>
          ))}

          <button
            onClick={onAdd}
            className="flex w-full items-center justify-center gap-2 rounded-xl border border-dashed border-slate-700 py-3 text-sm text-slate-400 transition hover:border-indigo-500/50 hover:text-indigo-300"
          >
            <span className="text-lg leading-none">+</span> Add Project
          </button>
        </div>
      )}
    </div>
  )
}
