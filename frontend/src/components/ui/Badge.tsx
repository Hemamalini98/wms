import { cn } from '@/utils/cn'

type BadgeVariant = 'in-progress' | 'completed' | 'delayed' | 'inquiry' | 'hold' | 'planning' | 'active' | 'default'

const variantMap: Record<BadgeVariant, string> = {
  'in-progress': 'bg-blue-100 text-blue-700 border-blue-200',
  'completed':   'bg-green-100 text-green-700 border-green-200',
  'delayed':     'bg-red-100 text-red-700 border-red-200',
  'inquiry':     'bg-orange-100 text-orange-700 border-orange-200',
  'hold':        'bg-yellow-100 text-yellow-700 border-yellow-200',
  'planning':    'bg-purple-100 text-purple-700 border-purple-200',
  'active':      'bg-green-100 text-green-700 border-green-200',
  'default':     'bg-gray-100 text-gray-600 border-gray-200',
}

interface BadgeProps {
  variant?: BadgeVariant
  children: React.ReactNode
  className?: string
}

export function Badge({ variant = 'default', children, className }: BadgeProps) {
  return (
    <span className={cn(
      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border',
      variantMap[variant],
      className
    )}>
      {children}
    </span>
  )
}

export function statusToBadge(status: string): BadgeVariant {
  const map: Record<string, BadgeVariant> = {
    'in-progress': 'in-progress',
    'in progress': 'in-progress',
    'complete':    'completed',
    'completed':   'completed',
    'hold':        'hold',
    'in-query':    'inquiry',
    'planning':    'planning',
    'active':      'active',
    'delayed':     'delayed',
  }
  return map[status.toLowerCase()] ?? 'default'
}
