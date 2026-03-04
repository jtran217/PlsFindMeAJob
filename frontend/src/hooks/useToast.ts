import { useState, useCallback } from 'react'

interface Toast {
  id: string
  message: string
  type: 'error' | 'success' | 'info'
  duration?: number
}

export const useToast = () => {
  const [toasts, setToasts] = useState<Toast[]>([])

  const showToast = useCallback((message: string, type: 'error' | 'success' | 'info' = 'error', duration = 5000) => {
    const id = Math.random().toString(36).substr(2, 9)
    const toast: Toast = { id, message, type, duration }
    
    setToasts(prev => [...prev, toast])
    
    // Auto remove after duration + animation time
    setTimeout(() => {
      removeToast(id)
    }, duration + 300)
  }, [])

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }, [])

  const showError = useCallback((message: string, duration?: number) => {
    showToast(message, 'error', duration)
  }, [showToast])

  const showSuccess = useCallback((message: string, duration?: number) => {
    showToast(message, 'success', duration)
  }, [showToast])

  const showInfo = useCallback((message: string, duration?: number) => {
    showToast(message, 'info', duration)
  }, [showToast])

  return {
    toasts,
    showToast,
    showError,
    showSuccess,
    showInfo,
    removeToast,
  }
}