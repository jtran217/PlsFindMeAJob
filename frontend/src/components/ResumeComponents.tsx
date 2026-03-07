/**
 * Enhanced UI components for the resume builder
 */
import { useState } from 'react'

interface SkillRatingProps {
  level: number
  onChange: (level: number) => void
  showNumeric?: boolean
  type?: 'stars' | 'bars' | 'dots'
}

export function SkillRating({ level, onChange, showNumeric = true, type = 'bars' }: SkillRatingProps) {
  const [hoverLevel, setHoverLevel] = useState<number | null>(null)
  
  const displayLevel = hoverLevel !== null ? hoverLevel : level
  const maxLevel = 5
  
  if (type === 'stars') {
    return (
      <div className="flex items-center gap-2">
        <div className="flex gap-1">
          {Array.from({ length: maxLevel }, (_, i) => {
            const starLevel = i + 1
            const isFilled = starLevel <= displayLevel
            const isHovered = hoverLevel !== null && starLevel <= hoverLevel
            
            return (
              <button
                key={i}
                type="button"
                onClick={() => onChange(starLevel)}
                onMouseEnter={() => setHoverLevel(starLevel)}
                onMouseLeave={() => setHoverLevel(null)}
                className={`w-5 h-5 transition-colors ${
                  isFilled 
                    ? isHovered ? 'text-yellow-400' : 'text-yellow-500' 
                    : 'text-slate-600 hover:text-slate-500'
                }`}
              >
                <svg fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              </button>
            )
          })}
        </div>
        {showNumeric && (
          <span className="text-sm text-slate-400 min-w-[3ch]">{displayLevel}/5</span>
        )}
      </div>
    )
  }
  
  if (type === 'dots') {
    return (
      <div className="flex items-center gap-2">
        <div className="flex gap-1">
          {Array.from({ length: maxLevel }, (_, i) => {
            const dotLevel = i + 1
            const isFilled = dotLevel <= displayLevel
            const isHovered = hoverLevel !== null && dotLevel <= hoverLevel
            
            return (
              <button
                key={i}
                type="button"
                onClick={() => onChange(dotLevel)}
                onMouseEnter={() => setHoverLevel(dotLevel)}
                onMouseLeave={() => setHoverLevel(null)}
                className={`w-3 h-3 rounded-full transition-colors ${
                  isFilled 
                    ? isHovered ? 'bg-indigo-400' : 'bg-indigo-500' 
                    : 'bg-slate-600 hover:bg-slate-500'
                }`}
              />
            )
          })}
        </div>
        {showNumeric && (
          <span className="text-sm text-slate-400 min-w-[3ch]">{displayLevel}/5</span>
        )}
      </div>
    )
  }
  
  // Default: bars
  return (
    <div className="flex items-center gap-3">
      <div className="flex gap-1">
        {Array.from({ length: maxLevel }, (_, i) => {
          const barLevel = i + 1
          const isFilled = barLevel <= displayLevel
          const isHovered = hoverLevel !== null && barLevel <= hoverLevel
          
          return (
            <button
              key={i}
              type="button"
              onClick={() => onChange(barLevel)}
              onMouseEnter={() => setHoverLevel(barLevel)}
              onMouseLeave={() => setHoverLevel(null)}
              className={`w-6 h-2 rounded-sm transition-colors ${
                isFilled 
                  ? isHovered ? 'bg-indigo-400' : 'bg-indigo-500' 
                  : 'bg-slate-600 hover:bg-slate-500'
              }`}
            />
          )
        })}
      </div>
      {showNumeric && (
        <span className="text-sm text-slate-400 min-w-[3ch]">{displayLevel}/5</span>
      )}
    </div>
  )
}

interface EnhancedTextareaProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  rows?: number
  maxLength?: number
  showTips?: boolean
  label?: string
  helpText?: string
}

export function EnhancedTextarea({
  value,
  onChange,
  placeholder,
  rows = 4,
  maxLength,
  showTips = false,
  label,
  helpText
}: EnhancedTextareaProps) {
  const [isFocused, setIsFocused] = useState(false)
  const characterCount = value.length
  
  return (
    <div className="space-y-2">
      {label && (
        <label className="block text-sm font-medium text-slate-300">
          {label}
        </label>
      )}
      
      <div className="relative">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          placeholder={placeholder}
          rows={rows}
          maxLength={maxLength}
          className={`w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white transition-colors ${
            isFocused ? 'border-indigo-500 ring-1 ring-indigo-500/20' : 'focus:border-indigo-500'
          }`}
        />
        
        {maxLength && (
          <div className="absolute bottom-2 right-2">
            <span className={`text-xs ${
              characterCount > maxLength * 0.9 
                ? characterCount >= maxLength ? 'text-red-400' : 'text-yellow-400'
                : 'text-slate-500'
            }`}>
              {characterCount}/{maxLength}
            </span>
          </div>
        )}
      </div>
      
      {helpText && (
        <p className="text-xs text-slate-400">{helpText}</p>
      )}
      
      {showTips && isFocused && (
        <div className="rounded-lg bg-indigo-500/10 border border-indigo-500/30 p-3 text-xs text-indigo-300">
          <div className="font-medium mb-1">💡 Writing Tips:</div>
          <ul className="space-y-1 text-slate-400">
            <li>• Use action verbs (developed, implemented, improved)</li>
            <li>• Include quantifiable achievements when possible</li>
            <li>• Keep it concise and relevant to the role</li>
            <li>• Use bullet points for multiple accomplishments</li>
          </ul>
        </div>
      )}
    </div>
  )
}

interface SectionToggleProps {
  title: string
  hidden: boolean
  onToggle: (hidden: boolean) => void
  itemCount?: number
}

export function SectionToggle({ title, hidden, onToggle, itemCount }: SectionToggleProps) {
  return (
    <div className="flex items-center justify-between p-3 rounded-lg bg-slate-800/30 border border-slate-700">
      <div className="flex items-center gap-3">
        <div className={`w-3 h-3 rounded-full ${hidden ? 'bg-slate-500' : 'bg-green-500'}`} />
        <span className="font-medium text-slate-200">{title}</span>
        {itemCount !== undefined && (
          <span className="text-xs text-slate-400 bg-slate-700 px-2 py-1 rounded">
            {itemCount} item{itemCount !== 1 ? 's' : ''}
          </span>
        )}
      </div>
      
      <button
        onClick={() => onToggle(!hidden)}
        className={`px-3 py-1 text-xs rounded transition-colors ${
          hidden 
            ? 'bg-slate-600 text-slate-300 hover:bg-slate-500' 
            : 'bg-green-600 text-white hover:bg-green-700'
        }`}
      >
        {hidden ? 'Show' : 'Hide'}
      </button>
    </div>
  )
}

interface ProfessionalLevelProps {
  level: number
  label: string
  color?: 'indigo' | 'green' | 'blue' | 'purple' | 'yellow'
}

export function ProfessionalLevel({ level, label, color = 'indigo' }: ProfessionalLevelProps) {
  const colorClasses = {
    indigo: 'bg-indigo-500',
    green: 'bg-green-500', 
    blue: 'bg-blue-500',
    purple: 'bg-purple-500',
    yellow: 'bg-yellow-500'
  }
  
  const percentage = (level / 5) * 100
  
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="text-slate-300">{label}</span>
        <span className="text-slate-400">{level}/5</span>
      </div>
      <div className="w-full bg-slate-700 rounded-full h-2">
        <div 
          className={`h-2 rounded-full transition-all duration-300 ${colorClasses[color]}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}

interface DateInputProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  allowPresent?: boolean
}

export function DateInput({ value, onChange, placeholder = "MM/YYYY", allowPresent = false }: DateInputProps) {
  const [showPresets, setShowPresets] = useState(false)
  
  const currentYear = new Date().getFullYear()
  const currentMonth = new Date().getMonth() + 1
  
  const presets = [
    { label: 'Present', value: 'Present' },
    { label: 'Current Month', value: `${currentMonth.toString().padStart(2, '0')}/${currentYear}` },
    { label: 'Start of Year', value: `01/${currentYear}` },
    { label: 'Last Year', value: `12/${currentYear - 1}` }
  ]
  
  return (
    <div className="relative">
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onFocus={() => setShowPresets(true)}
        onBlur={() => setTimeout(() => setShowPresets(false), 200)}
        placeholder={placeholder}
        className="w-full rounded border border-slate-700 bg-[#071026] px-3 py-2 text-white focus:border-indigo-500"
      />
      
      {showPresets && (allowPresent || value === 'Present') && (
        <div className="absolute top-full left-0 mt-1 w-full bg-slate-800 border border-slate-600 rounded shadow-lg z-10">
          {presets.map((preset) => (
            <button
              key={preset.value}
              type="button"
              onClick={() => {
                onChange(preset.value)
                setShowPresets(false)
              }}
              className="w-full px-3 py-2 text-left text-sm text-slate-200 hover:bg-slate-700 first:rounded-t last:rounded-b"
            >
              {preset.label}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}