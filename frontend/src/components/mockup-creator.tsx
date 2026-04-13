"use client"

import * as React from "react"
import { Upload, X, Check, Loader2, Sparkles, Image as ImageIcon, Camera, RefreshCw } from "lucide-react"
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogDescription,
  DialogFooter
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
interface Location {
  id: string;
  name: string;
  category: string;
  primary_photo_url?: string;
}

interface MockupCreatorProps {
  location: Location | null;
  onClose: () => void;
}

type ProcessingStage = 'idle' | 'uploading' | 'detecting' | 'segmenting' | 'rendering' | 'completed' | 'failed';

const STAGE_MESSAGES: Record<ProcessingStage, string> = {
  idle: "",
  uploading: "Загрузка файлов на сервер...",
  detecting: "Поиск рекламного носителя (YOLO OBB)...",
  segmenting: "Вырезание препятствий (SAM 2)...",
  rendering: "Финальное наложение и цветокоррекция...",
  completed: "Готово!",
  failed: "Ошибка при обработке"
};

export function MockupCreator({ location, onClose }: MockupCreatorProps) {
  const [creativeFile, setCreativeFile] = React.useState<File | null>(null)
  const [backgroundFile, setBackgroundFile] = React.useState<File | null>(null)
  const [stage, setStage] = React.useState<ProcessingStage>('idle')
  const [result, setResult] = React.useState<string | null>(null)

  const handleCreativeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setCreativeFile(e.target.files[0])
    }
  }

  const handleBackgroundChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setBackgroundFile(e.target.files[0])
    }
  }

  const handleGenerate = async () => {
    if (!creativeFile) return
    if (!location && !backgroundFile) return

    setStage('uploading')
    
    try {
      // Имитация этапов для UX
      setTimeout(() => setStage('detecting'), 1000)
      setTimeout(() => setStage('segmenting'), 2500)
      setTimeout(() => setStage('rendering'), 4500)

      const formData = new FormData()
      formData.append("creative", creativeFile)
      
      if (backgroundFile) {
        formData.append("background", backgroundFile)
      }
      
      formData.append("location_id", location?.id || "custom")

      const response = await fetch("http://localhost:8000/v1/mockup/generate", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) throw new Error("Ошибка сервера при генерации")

      const data = await response.json()
      
      if (data.status === "completed" && data.mockup_url) {
        setResult(data.mockup_url)
        setStage('completed')
      } else {
        throw new Error(data.error || "Неизвестная ошибка")
      }
    } catch (error) {
      console.error("Generation failed:", error)
      setStage('failed')
    }
  }

  const reset = () => {
    setCreativeFile(null)
    setBackgroundFile(null)
    setResult(null)
    setStage('idle')
  }

  const isProcessing = stage !== 'idle' && stage !== 'completed' && stage !== 'failed';

  return (
    <Dialog open={isOpen} onOpenChange={(open) => { if (!open) { reset(); onClose(); } }}>
      <DialogContent className="sm:max-w-[600px] border-border/40 bg-background/95 backdrop-blur-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-2xl font-bold tracking-tight">
            <Sparkles className="h-6 w-6 text-primary animate-pulse" />
            AI Mockup Creator
          </DialogTitle>
          <DialogDescription>
            {location ? (
              <>Используется база: <span className="font-semibold text-foreground">{location.name}</span></>
            ) : (
              "Режим «Street Upload»: загрузите фото с улицы"
            )}
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-6 py-6 font-sans">
          {!result && !isProcessing && (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              {/* Выбор креатива (Обязательно) */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground uppercase tracking-wider">1. Креатив клиента</label>
                <label className={cn(
                  "flex flex-col items-center justify-center aspect-square rounded-2xl border-2 border-dashed transition-all cursor-pointer",
                  creativeFile ? "border-primary bg-primary/5" : "border-border/60 hover:border-primary/50 hover:bg-muted/30"
                )}>
                  {creativeFile ? (
                    <div className="flex flex-col items-center p-4 text-center">
                      <Check className="h-8 w-8 text-primary mb-2" />
                      <p className="text-xs font-medium truncate max-w-[150px]">{creativeFile.name}</p>
                    </div>
                  ) : (
                    <>
                      <Upload className="h-10 w-10 text-muted-foreground mb-2" />
                      <p className="text-xs font-medium text-center px-4">Загрузить баннер</p>
                    </>
                  )}
                  <input type="file" className="hidden" onChange={handleCreativeChange} accept="image/*" />
                </label>
              </div>

              {/* Выбор фона (Если Street Mode) */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground uppercase tracking-wider">2. Фото объекта</label>
                {!location || backgroundFile ? (
                  <label className={cn(
                    "flex flex-col items-center justify-center aspect-square rounded-2xl border-2 border-dashed transition-all cursor-pointer",
                    backgroundFile ? "border-green-500 bg-green-500/5" : "border-border/60 hover:border-green-500/50 hover:bg-muted/30"
                  )}>
                    {backgroundFile ? (
                      <div className="flex flex-col items-center p-4 text-center">
                        <Camera className="h-8 w-8 text-green-500 mb-2" />
                        <p className="text-xs font-medium truncate max-w-[150px]">{backgroundFile.name}</p>
                      </div>
                    ) : (
                      <>
                        <Camera className="h-10 w-10 text-muted-foreground mb-2" />
                        <p className="text-xs font-medium text-center px-4">Снять или выбрать фото</p>
                      </>
                    )}
                    <input 
                      type="file" 
                      className="hidden" 
                      onChange={handleBackgroundChange} 
                      accept="image/*" 
                      capture="environment" 
                    />
                  </label>
                ) : (
                  <div className="relative aspect-square rounded-2xl overflow-hidden border border-border/40 group">
                    <img 
                      src={location.primary_photo_url || "/placeholder-location.jpg"} 
                      alt="Target" 
                      className="h-full w-full object-cover grayscale-[0.5] group-hover:grayscale-0 transition-all" 
                    />
                    <div className="absolute inset-0 bg-black/20 flex items-end p-3">
                      <p className="text-[10px] text-white font-medium bg-black/40 px-2 py-1 rounded-full backdrop-blur-md">Базовое фото</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {isProcessing && (
            <div className="flex flex-col items-center justify-center gap-6 py-12">
              <div className="relative">
                <Loader2 className="h-16 w-16 animate-spin text-primary opacity-20" />
                <RefreshCw className="h-8 w-8 animate-spin-slow text-primary absolute top-1/2 left-1/2 -ml-4 -mt-4" />
              </div>
              <div className="text-center space-y-2">
                <p className="text-lg font-bold bg-gradient-to-r from-primary to-purple-600 bg-clip-text text-transparent">
                  {STAGE_MESSAGES[stage]}
                </p>
                <div className="flex gap-1 justify-center">
                  {[1, 2, 3, 4].map((i) => (
                    <div key={i} className={cn(
                      "h-1 w-8 rounded-full transition-colors duration-500",
                      (stage === 'uploading' && i === 1) || 
                      (stage === 'detecting' && i <= 2) || 
                      (stage === 'segmenting' && i <= 3) || 
                      (stage === 'rendering' && i <= 4) ? "bg-primary" : "bg-muted"
                    )} />
                  ))}
                </div>
              </div>
            </div>
          )}

          {result && !isProcessing && (
            <div className="relative group overflow-hidden rounded-2xl border border-border/40 shadow-2xl animate-in zoom-in-95 duration-500">
              <img src={result} alt="Result" className="w-full h-auto object-contain" />
              <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/80 to-transparent p-6 translate-y-2 group-hover:translate-y-0 transition-transform">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-white">
                    <div className="h-8 w-8 rounded-full bg-green-500 flex items-center justify-center">
                      <Check className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="font-bold">Мокап готов</p>
                      <p className="text-xs text-gray-300">Сохранено в историю</p>
                    </div>
                  </div>
                  <Button size="sm" className="bg-white text-black hover:bg-white/90 font-bold rounded-full">
                    SHARE
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>

        <DialogFooter className="gap-3 sm:justify-between border-t border-border/40 pt-6">
          <Button variant="ghost" onClick={onClose} className="rounded-full">Отмена</Button>
          {!result && !isProcessing ? (
            <Button 
              disabled={!creativeFile || (!location && !backgroundFile)} 
              onClick={handleGenerate}
              className="gap-2 bg-primary hover:bg-primary/90 text-primary-foreground font-bold px-10 rounded-full shadow-lg shadow-primary/20"
            >
              СГЕНЕРИРОВАТЬ
            </Button>
          ) : result ? (
            <div className="flex gap-2">
              <Button variant="secondary" onClick={reset} className="rounded-full">ЗАНОГО</Button>
              <Button className="bg-primary hover:bg-primary/90 font-bold rounded-full px-8">СКАЧАТЬ</Button>
            </div>
          ) : null}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
