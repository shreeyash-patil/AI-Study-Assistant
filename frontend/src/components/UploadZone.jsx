import { useRef } from 'react'

export default function UploadZone({ onUpload, isUploading, sessionId, fileName }) {
  const inputRef = useRef(null)

  const handleFile = (file) => {
    if (file && file.type === 'application/pdf') {
      onUpload(file)
    } else {
      alert('Please upload a PDF file')
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    handleFile(file)
  }

  const handleChange = (e) => {
    const file = e.target.files[0]
    handleFile(file)
  }

  return (
    <div className="bg-slate-900 rounded-xl border border-slate-800 p-5 h-full">
      <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-4">
        Upload PDF
      </h2>

      <div
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        onClick={() => inputRef.current.click()}
        className="border-2 border-dashed border-slate-700 rounded-lg p-8 text-center cursor-pointer hover:border-indigo-500 hover:bg-slate-800 transition-all"
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          onChange={handleChange}
          className="hidden"
        />

        {isUploading ? (
          <div className="text-indigo-400 flex flex-col items-center">
            <div className="w-8 h-8 border-2 border-indigo-400 border-t-transparent rounded-full animate-spin mb-3" />
            <p className="text-sm">Processing PDF...</p>
          </div>
        ) : sessionId ? (
          <div className="text-green-400">
            <div className="text-2xl mb-2">✅</div>
            <p className="text-sm font-medium">{fileName}</p>
            <p className="text-xs text-slate-500 mt-1">Click to upload a different PDF</p>
          </div>
        ) : (
          <div className="text-slate-400">
            <div className="text-2xl mb-2">📄</div>
            <p className="text-sm font-medium">Drop your PDF here</p>
            <p className="text-xs text-slate-500 mt-1">or click to browse</p>
          </div>
        )}
      </div>

      {sessionId && (
        <div className="mt-4 p-3 bg-green-950 border border-green-800 rounded-lg">
          <p className="text-xs text-green-400">✅ PDF processed and ready for questions</p>
        </div>
      )}
    </div>
  )
}