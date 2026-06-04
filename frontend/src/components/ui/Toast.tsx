import { CheckCircle, XCircle, AlertCircle, Info, X } from 'lucide-react'
import { useToastStore, type ToastType } from '@/store/useToastStore'
import { cn } from '@/utils/cn'

const config: Record<ToastType, { icon: React.ReactNode; classes: string }> = {
  success: { icon: <CheckCircle size={16} />, classes: 'bg-green-50 border-green-200 text-green-800' },
  error:   { icon: <XCircle     size={16} />, classes: 'bg-red-50 border-red-200 text-red-800' },
  warning: { icon: <AlertCircle size={16} />, classes: 'bg-yellow-50 border-yellow-200 text-yellow-800' },
  info:    { icon: <Info        size={16} />, classes: 'bg-blue-50 border-blue-200 text-blue-800' },
}

export function ToastContainer() {
  const { toasts, remove } = useToastStore()

  return (
    <div className="fixed top-4 right-4 z-[100] flex flex-col gap-2 pointer-events-none">
      {toasts.map((t) => {
        const c = config[t.type]
        return (
          <div
            key={t.id}
            className={cn(
              'flex items-center gap-3 px-4 py-3 rounded-xl border shadow-lg text-sm font-medium',
              'min-w-[280px] max-w-sm pointer-events-auto',
              'animate-in slide-in-from-right-full duration-300',
              c.classes
            )}
          >
            {c.icon}
            <span className="flex-1">{t.message}</span>
            <button onClick={() => remove(t.id)} className="opacity-60 hover:opacity-100 transition-opacity">
              <X size={14} />
            </button>
          </div>
        )
      })}
    </div>
  )
}
