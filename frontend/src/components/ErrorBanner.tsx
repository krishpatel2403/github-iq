export function ErrorBanner({
  message,
  onDismiss,
}: {
  message: string
  onDismiss: () => void
}) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-4 mb-4 flex items-start gap-3">
      <span className="text-red-600 flex-shrink-0">⚠</span>
      <div>
        <p className="text-sm text-red-800">{message}</p>
      </div>
      <button
        onClick={onDismiss}
        className="ml-auto text-red-600 hover:text-red-800 text-sm"
      >
        Dismiss
      </button>
    </div>
  )
}
