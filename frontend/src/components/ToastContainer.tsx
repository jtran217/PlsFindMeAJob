import React from 'react'
import Toast from './Toast.tsx'

interface ToastData {
  id: string
  message: string
  type: 'error' | 'success' | 'info'
  duration?: number
}

interface ToastContainerProps {
  toasts: ToastData[]
  onRemove: (id: string) => void
}

const ToastContainer: React.FC<ToastContainerProps> = ({ toasts, onRemove }) => {
  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-sm">
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          message={toast.message}
          type={toast.type}
          duration={toast.duration}
          onClose={() => onRemove(toast.id)}
        />
      ))}
    </div>
  )
}

export default ToastContainer