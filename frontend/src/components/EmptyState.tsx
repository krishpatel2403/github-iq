import { Inbox } from "lucide-react"

export function EmptyState({
  title,
  description,
  action,
}: {
  title: string
  description: string
  action?: React.ReactNode
}) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-slate-500">
      <Inbox className="w-10 h-10 mb-3 opacity-50" />
      <h3 className="font-medium">{title}</h3>
      <p className="text-sm mt-1">{description}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  )
}
