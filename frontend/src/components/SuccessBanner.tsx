import React, { useEffect, useState } from 'react'

interface SuccessBannerProps {
  message: string
  isVisible: boolean
  onHide?: () => void
  duration?: number
}

const SuccessBanner: React.FC<SuccessBannerProps> = ({
  message,
  isVisible,
  onHide,
  duration = 3000,
}) => {
  const [shouldRender, setShouldRender] = useState(false)
  const [isAnimating, setIsAnimating] = useState(false)

  useEffect(() => {
    if (isVisible) {
      setShouldRender(true)
      // Start animation after component mounts
      const animationTimer = setTimeout(() => setIsAnimating(true), 10)
      
      // Auto hide after duration
      const hideTimer = setTimeout(() => {
        handleHide()
      }, duration)

      return () => {
        clearTimeout(animationTimer)
        clearTimeout(hideTimer)
      }
    } else {
      handleHide()
    }
  }, [isVisible, duration])

  const handleHide = () => {
    setIsAnimating(false)
    setTimeout(() => {
      setShouldRender(false)
      onHide?.()
    }, 300) // Match animation duration
  }

  if (!shouldRender) {
    return null
  }

  return (
    <div
      className={`
        mt-4 p-4 rounded-lg border transition-all duration-300 ease-in-out
        bg-green-500/10 border-green-500/20 text-green-400
        ${isAnimating 
          ? 'opacity-100 transform translate-y-0' 
          : 'opacity-0 transform translate-y-2'
        }
      `}
      role="status"
      aria-live="polite"
      aria-atomic="true"
    >
      <div className="flex items-center gap-3">
        <div className="flex-shrink-0">
          <svg 
            className="w-5 h-5 text-green-400" 
            fill="currentColor" 
            viewBox="0 0 20 20"
            aria-hidden="true"
          >
            <path 
              fillRule="evenodd" 
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" 
              clipRule="evenodd" 
            />
          </svg>
        </div>
        
        <div className="flex-1">
          <p className="text-sm font-medium leading-5">
            {message}
          </p>
        </div>

        <button
          onClick={handleHide}
          className="flex-shrink-0 rounded-md p-1 hover:bg-green-500/10 focus:outline-none focus:ring-2 focus:ring-green-500/20 transition-colors"
          aria-label="Close success message"
        >
          <svg className="w-4 h-4 text-green-400" fill="currentColor" viewBox="0 0 20 20">
            <path 
              fillRule="evenodd" 
              d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" 
              clipRule="evenodd" 
            />
          </svg>
        </button>
      </div>
    </div>
  )
}

export default SuccessBanner