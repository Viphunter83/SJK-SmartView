"use client"

import * as React from "react"
import { Upload, X, Check, Loader2, Sparkles, Image as ImageIcon } from "lucide-react"
import { 
  Dialog, 
  DialogContent, 
  DialogHeader, 
  DialogTitle, 
  DialogDescription,
  DialogFooter
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Location } from "@/lib/mock-data"

interface MockupCreatorProps {
  location: Location | null;
  isOpen: boolean;
  onClose: () => void;
}

export function MockupCreator({ location, isOpen, onClose }: MockupCreatorProps) {
  const [file, setFile] = React.useState<File | null>(null)
  const [isProcessing, setIsProcessing] = React.useState(false)
  const [result, setResult] = React.useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleGenerate = async () => {
    if (!file || !location) return
    setIsProcessing(true)
    
    try {
      // 1. Подготовка данных (Multipart)
      const formData = new FormData()
      formData.append("background", new File([], "bg.jpg")) // В будущем: передаем фото локации или текущий канвас
      formData.append("creative", file)
      formData.append("location_id", location.id)

      // 2. Запрос к API
      const response = await fetch("http://localhost:8000/v1/mockup/generate", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) throw new Error("Ошибка сервера при генерации")

      const data = await response.json()
      
      if (data.status === "completed" && data.mockup_url) {
        setResult(data.mockup_url)
      } else {
        throw new Error(data.error || "Неизвестная ошибка")
      }
    } catch (error) {
      console.error("Generation failed:", error)
      alert("Не удалось сгенерировать мокап. Проверьте запущен ли бэкенд.")
    } finally {
      setIsProcessing(false)
    }
  }

  const reset = () => {
    setFile(null)
    setResult(null)
    setIsProcessing(false)
  }

  return (
    <Dialog open={isOpen} onOpenChange={(open) => { if (!open) { reset(); onClose(); } }}>
      <DialogContent className="sm:max-w-[600px] border-border/40 bg-background/90 backdrop-blur-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-2xl">
            <Sparkles className="h-5 w-5 text-primary" />
            Создание мокапа
          </DialogTitle>
          <DialogDescription>
            Экран: <span className="font-semibold text-foreground">{location?.name}</span>
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col items-center justify-center py-8">
          {!file && !result ? (
            <label className="flex w-full cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-border/60 bg-muted/30 py-12 transition-colors hover:bg-muted/50">
              <Upload className="mb-4 h-12 w-12 text-muted-foreground" />
              <p className="mb-2 text-sm font-semibold">Нажмите для загрузки креатива</p>
              <p className="text-xs text-muted-foreground">PNG, JPG или SVG (макс. 5Мб)</p>
              <input type="file" className="hidden" onChange={handleFileChange} accept="image/*" />
            </label>
          ) : isProcessing ? (
            <div className="flex flex-col items-center gap-4 py-12">
              <Loader2 className="h-12 w-12 animate-spin text-primary" />
              <div className="text-center">
                <p className="font-semibold">Магия AI в процессе...</p>
                <p className="text-sm text-muted-foreground">Находим углы и накладываем маски перекрытий</p>
              </div>
            </div>
          ) : result ? (
            <div className="relative aspect-video w-full overflow-hidden rounded-xl border border-border/40 shadow-2xl">
              <img src={result} alt="Result" className="h-full w-full object-cover" />
              <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/60 p-4">
                <p className="flex items-center gap-2 text-sm font-medium text-white">
                  <Check className="h-4 w-4 text-green-400" />
                  Мокап успешно создан
                </p>
              </div>
            </div>
          ) : (
            <div className="flex w-full items-center justify-between rounded-lg border border-border/40 bg-muted/40 p-4">
              <div className="flex items-center gap-3">
                <ImageIcon className="h-8 w-8 text-primary" />
                <div>
                  <p className="text-sm font-semibold">{file?.name}</p>
                  <p className="text-xs text-muted-foreground">{(file!.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              </div>
              <Button variant="ghost" size="icon" onClick={() => setFile(null)}>
                <X className="h-4 w-4" />
              </Button>
            </div>
          )}
        </div>

        <DialogFooter className="gap-2 sm:justify-between">
          <Button variant="ghost" onClick={onClose}>Отмена</Button>
          {!result ? (
            <Button 
              disabled={!file || isProcessing} 
              onClick={handleGenerate}
              className="gap-2 bg-gradient-to-r from-primary to-purple-600 px-8"
            >
              {isProcessing && <Loader2 className="h-4 w-4 animate-spin" />}
              Сгенерировать
            </Button>
          ) : (
            <div className="flex gap-2">
              <Button variant="outline" onClick={reset}>Заново</Button>
              <Button className="bg-green-600 hover:bg-green-700">Скачать JPEG</Button>
            </div>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
