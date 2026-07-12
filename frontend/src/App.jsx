import { useState } from 'react'
import axios from 'axios'
import UploadZone from './components/UploadZone'
import ChatWindow from './components/ChatWindow'

const API = 'http://localhost:8000'

export default function App() {
  const [sessionId, setSessionId] = useState(null)
  const [fileName, setFileName] = useState('')
  const [messages, setMessages] = useState([])
  const [isUploading, setIsUploading] = useState(false)
  const [isAsking, setIsAsking] = useState(false)

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
      alert('Failed to upload PDF. Make sure the backend is running.')
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
      setMessages(prev => [...prev, { role: 'assistant', content: 'Something went wrong. Please try again.' }])
    } finally {
      setIsAsking(false)
    }
  }

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}
      className="bg-slate-950 text-white">
      
      <div className="px-6 py-5 border-b border-slate-800">
        <h1 className="text-xl font-bold text-white">Study Assistant</h1>
        <p className="text-slate-400 text-sm mt-0.5">Upload a PDF and ask questions about it</p>
      </div>

      <div style={{ flex: 1, overflow: 'hidden', display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px', padding: '24px' }}>
        <UploadZone
          onUpload={handleUpload}
          isUploading={isUploading}
          sessionId={sessionId}
          fileName={fileName}
        />
        <ChatWindow
          onAsk={handleAsk}
          isAsking={isAsking}
          messages={messages}
          sessionId={sessionId}
        />
      </div>
    </div>
  )
}