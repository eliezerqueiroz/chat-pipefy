import { useEffect, useState } from 'react'
import { Activity, Wifi, WifiOff } from 'lucide-react'
import { getHealth } from '../../api/client'
import { useChatStore } from '../../store/chatStore'

export function Header() {
  const { activeSession } = useChatStore()
  const session = activeSession()
  const [health, setHealth] = useState<{ status: string; redis: string } | null>(null)

  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch(() => setHealth({ status: 'error', redis: 'disconnected' }))
  }, [])

  return (
    <header className="h-12 flex items-center justify-between px-6 border-b border-surface-600 bg-surface-800 shrink-0">
      {/* Session name */}
      <h1 className="text-sm font-semibold text-gray-200 truncate">
        {session ? session.name : 'Chat-Pipefy'}
      </h1>

      {/* Health indicator */}
      {health && (
        <div className="flex items-center gap-2 text-xs">
          {health.redis === 'connected' ? (
            <>
              <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse-soft" />
              <span className="text-emerald-400 hidden sm:block">Redis connected</span>
            </>
          ) : (
            <>
              <div className="w-1.5 h-1.5 rounded-full bg-red-400" />
              <span className="text-red-400 hidden sm:block">Redis disconnected</span>
            </>
          )}
        </div>
      )}
    </header>
  )
}
