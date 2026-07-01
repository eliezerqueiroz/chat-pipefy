import { Sidebar } from './components/Layout/Sidebar'
import { Header } from './components/Layout/Header'
import { DocumentPanel } from './components/DocumentPanel/DocumentPanel'
import { ChatPanel } from './components/ChatPanel/ChatPanel'

export default function App() {
  return (
    <div className="flex h-screen overflow-hidden">
      {/* Session sidebar */}
      <Sidebar />

      {/* Main content: document panel + chat */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <div className="flex-1 flex overflow-hidden">
          <DocumentPanel />
          <ChatPanel />
        </div>
      </div>
    </div>
  )
}
