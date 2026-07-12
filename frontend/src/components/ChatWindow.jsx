import { useState, useRef, useEffect } from 'react'

export default function ChatWindow({ onAsk, isAsking, messages, sessionId }) {
  const [input, setInput] = useState('')
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = () => {
    if (!input.trim() || !sessionId || isAsking) return
    onAsk(input.trim())
    setInput('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', overflow: 'hidden' }}
      className="bg-slate-900 rounded-xl border border-slate-800">

      <div className="p-5 border-b border-slate-800 shrink-0">
        <h2 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Chat</h2>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '20px' }} className="space-y-4">
        {messages.length === 0 ? (
          <div className="text-center text-slate-600 mt-20">
            <div className="text-3xl mb-3">🧠</div>
            <p className="text-sm">Upload a PDF and ask anything about it</p>
          </div>
        ) : (
          messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[80%] rounded-xl px-4 py-3 text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-indigo-600 text-white'
                  : 'bg-slate-800 text-slate-200'
              }`}>
                {msg.content}
              </div>
            </div>
          ))
        )}

        {isAsking && (
          <div className="flex justify-start">
            <div className="bg-slate-800 rounded-xl px-4 py-3 text-sm text-slate-400">
              Thinking...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="p-4 border-t border-slate-800 shrink-0">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={sessionId ? 'Ask a question about your PDF...' : 'Upload a PDF first'}
            disabled={!sessionId || isAsking}
            className="flex-1 bg-slate-800 text-slate-200 placeholder-slate-600 rounded-lg px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
          />
          <button
            onClick={handleSubmit}
            disabled={!sessionId || isAsking || !input.trim()}
            className="bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg px-4 py-2.5 text-sm font-medium transition-colors"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}