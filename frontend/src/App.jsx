import { useState } from 'react'
import axios from 'axios'
import UploadZone from './components/UploadZone'
import ChatWindow from './components/ChatWindow'
import Toast from './components/Toast'

const API = 'http://localhost:8000'

export default function App() {
  const [sessionId, setSessionId] = useState(null)
  const [fileName, setFileName] = useState('')
  const [messages, setMessages] = useState([])
  const [isUploading, setIsUploading] = useState(false)
  const [isAsking, setIsAsking] = useState(false)
  const [error, setError] = useState(null)

  const handleUpload = async (file) => {
    setIsUploading(true)
    setMessages([])
    setSessionId(null)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const res = await axios.post(`${API}/upload`, formData)
      setSessionId(res.data.session_id)
      setFileName(file.name)
    } catch (err) {
      setError('Failed to upload PDF. Make sure the backend is running.')
    } finally {
      setIsUploading(false)
    }
  }

  const handleAsk = async (question) => {
    setMessages(prev => [...prev, { role: 'user', content: question }])
    setIsAsking(true)
    try {
      const res = await axios.post(`${API}/ask`, {
        question,
        session_id: sessionId
      })
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.answer }])
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: '❌ Failed to get answer. Please try again.' }])
      setError('Something went wrong while asking the question.')
    } finally {
      setIsAsking(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}
      className="bg-slate-950 text-white">

      <Toast message={error} onClose={() => setError(null)} />

      <div className="px-4 py-4 border-b border-slate-800 shrink-0">
        <h1 className="text-xl font-bold text-white">Study Assistant</h1>
        <p className="text-slate-400 text-sm mt-0.5">Upload a PDF and ask questions about it</p>
      </div>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '16px', gap: '16px', maxWidth: '900px', width: '100%', margin: '0 auto', boxSizing: 'border-box' }}>

        <div className="shrink-0">
          <UploadZone
            onUpload={handleUpload}
            isUploading={isUploading}
            sessionId={sessionId}
            fileName={fileName}
          />
        </div>

        <div style={{ flex: 1, overflow: 'hidden', minHeight: '400px' }}>
          <ChatWindow
            onAsk={handleAsk}
            isAsking={isAsking}
            messages={messages}
            sessionId={sessionId}
          />
        </div>

      </div>
    </div>
  )
}