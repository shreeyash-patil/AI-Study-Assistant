export default function Toast({ message, onClose }) {
  if (!message) return null

  return (
    <div className="fixed top-4 right-4 z-50 flex items-center gap-3 bg-red-950 border border-red-800 text-red-300 text-sm px-4 py-3 rounded-lg shadow-lg max-w-sm">
      <span>⚠️</span>
      <span className="flex-1">{message}</span>
      <button
        onClick={onClose}
        className="text-red-400 hover:text-red-200 transition-colors ml-2"
      >
        ✕
      </button>
    </div>
  )
}