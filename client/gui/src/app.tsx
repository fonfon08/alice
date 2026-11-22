import CanvaPage from '@/pages/canva'
import { TooltipProvider } from '@/components/ui/tooltip'
import { Toaster } from '@/components/ui/sonner'
import StartupNotice from '@/components/canva/startup_notice'

export default function App() {
  return (
    <TooltipProvider>
      <Toaster />
      <StartupNotice />
      <CanvaPage />
    </TooltipProvider>
  )
}
