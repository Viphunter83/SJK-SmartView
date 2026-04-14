"use client"

import * as React from "react"
import {
  Upload, X, Check, Loader2, Sparkles,
  Image as ImageIcon, Camera, RefreshCw, Download, AlertCircle
} from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { API_ENDPOINTS } from "@/lib/config"
import { getFullImageUrl, downloadFile } from "@/lib/utils/url"
import { useLanguage } from "@/lib/i18n"

interface Point {
  x: number;
  y: number;
}

interface Location {
  id: string;
  name: string;
  category: string;
  primary_photo_url?: string;
  screen_geometry?: Point[];
  aspect_ratio?: number;
}

interface MockupCreatorProps {
  location: Location | null;
  onClose: () => void;
}

type ProcessingStage = 'idle' | 'uploading' | 'rendering' | 'saving' | 'completed' | 'failed';

// STAGE_MESSAGES will be defined inside component to use t()

const STAGE_PROGRESS: Record<ProcessingStage, number> = {
  idle: 0,
  uploading: 1,
  rendering: 2,
  saving: 3,
  completed: 4,
  failed: 0,
};

const DEFAULT_CORNERS: Point[] = [
  { x: 120, y: 120 },
  { x: 680, y: 120 },
  { x: 680, y: 460 },
  { x: 120, y: 460 },
];

export function MockupCreator({ location, onClose }: MockupCreatorProps) {
  const [isMounted, setIsMounted] = React.useState(false)
  const [creativeFile, setCreativeFile] = React.useState<File | null>(null)
  const [creativePreview, setCreativePreview] = React.useState<string | null>(null)
  const [backgroundFile, setBackgroundFile] = React.useState<File | null>(null)
  const [stage, setStage] = React.useState<ProcessingStage>('idle')
  const [result, setResult] = React.useState<string | null>(null)
  const [errorMessage, setErrorMessage] = React.useState<string | null>(null)
  const [resultIsPremium, setResultIsPremium] = React.useState(false)
  const [isDetecting, setIsDetecting] = React.useState(false)
  const [usePremium, setUsePremium] = React.useState(false)
  const [points, setPoints] = React.useState<Point[]>(
    location?.screen_geometry?.length === 4
      ? location.screen_geometry
      : DEFAULT_CORNERS
  )
  const { t } = useLanguage()

  const STAGE_MESSAGES: Record<ProcessingStage, string> = {
    idle: "",
    uploading: t("stage_uploading"),
    rendering: t("stage_rendering"),
    saving: t("stage_saving"),
    completed: t("stage_completed"),
    failed: t("stage_failed"),
  }

  React.useEffect(() => {
    setIsMounted(true)
    return () => {
      // Cleanup object URLs
      if (creativePreview) URL.revokeObjectURL(creativePreview)
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const handleCreativeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setCreativeFile(file)
    if (creativePreview) URL.revokeObjectURL(creativePreview)
    setCreativePreview(URL.createObjectURL(file))
  }

  const handleBackgroundChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) setBackgroundFile(file)
  }

  const handleAutoDetect = async () => {
    if (!backgroundFile) return
    setIsDetecting(true)
    try {
      const formData = new FormData()
      formData.append("image", backgroundFile)
      const response = await fetch(API_ENDPOINTS.DETECT_CORNERS, {
        method: "POST",
        body: formData,
      })
      if (response.ok) {
        const data = await response.json()
        if (data.corners?.length === 4) {
          setPoints(data.corners)
        }
      }
    } catch (error) {
      console.error("Auto-detect failed:", error)
    } finally {
      setIsDetecting(false)
    }
  }

  const handleGenerate = async () => {
    if (!creativeFile) return
    if (!location && !backgroundFile) return

    setErrorMessage(null)
    setStage('uploading')

    try {
      // ── Определяем источник фона ──────────────────────────────
      let backgroundSrc: string | null = null
      if (backgroundFile) {
        backgroundSrc = URL.createObjectURL(backgroundFile)
      } else if (location?.primary_photo_url) {
        backgroundSrc = getFullImageUrl(location.primary_photo_url)
      }
      if (!backgroundSrc) throw new Error(t("no_bg_image"))
      if (!creativePreview) throw new Error(t("no_creative"))

      const renderCorners = location?.screen_geometry?.length === 4
        ? location.screen_geometry
        : points

      // ── Step 1: Attempt via Backend → Gemini Native AI (primary) ────
      setStage('rendering')

      // Для бэкенда нам нужен файл фона (не URL)
      // Если фон из каталога — скачиваем через прокси в Blob
      let bgFile = backgroundFile
      if (!bgFile && backgroundSrc) {
        try {
          const proxyUrl = backgroundSrc.startsWith("http")
            ? `/api/image-proxy?url=${encodeURIComponent(backgroundSrc)}`
            : backgroundSrc
          const resp = await fetch(proxyUrl)
          if (resp.ok) {
            const blob = await resp.blob()
            bgFile = new File([blob], "background.jpg", { type: blob.type || "image/jpeg" })
          }
        } catch (e) {
          console.warn("Background fetch failed, will use canvas fallback:", e)
        }
      }

      let resultUrl: string | null = null
      let isPremium = false

      if (bgFile) {
        try {
          const formData = new FormData()
          formData.append("creative", creativeFile)
          formData.append("background", bgFile)
          formData.append("location_id", location?.id || "custom")
          formData.append("use_premium", String(usePremium))
          if (renderCorners && renderCorners.length === 4) {
            formData.append("corners_json", JSON.stringify(renderCorners))
          }
          // Не передаём result_url → бэкенд запустит Modal GPU

          const controller = new AbortController()
          const timeout = setTimeout(() => controller.abort(), 120_000) // 2 мин для GPU

          const response = await fetch(API_ENDPOINTS.GENERATE_MOCKUP, {
            method: "POST",
            body: formData,
            signal: controller.signal,
          })
          clearTimeout(timeout)

          if (response.ok) {
            const data = await response.json()
            if (data.status === "completed" && data.mockup_url) {
              resultUrl = data.mockup_url
              setResultIsPremium(usePremium)
              isPremium = usePremium
            }
          }
        } catch (modalError) {
          console.warn("Backend/Gemini failed, falling back to Canvas:", modalError)
        }
      }

      // ── Step 2: Canvas fallback (если Backend не сработал) ───────
      if (!resultUrl) {
        console.log("Using Canvas renderer as fallback")
        const { renderMockup } = await import("@/lib/canvas-renderer")
        const dataUrl = await renderMockup(backgroundSrc, creativePreview, renderCorners, {
          opacity: 1.0,
          quality: 0.92,
        })

        // Пытаемся сохранить через бэкенд (для истории)
        try {
          const formData = new FormData()
          formData.append("creative", creativeFile)
          formData.append("location_id", location?.id || "custom")
          formData.append("result_url", dataUrl)

          const response = await fetch(API_ENDPOINTS.GENERATE_MOCKUP, {
            method: "POST",
            body: formData,
            signal: AbortSignal.timeout(10_000),
          })
          if (response.ok) {
            const data = await response.json()
            if (data.mockup_url) resultUrl = data.mockup_url
          }
        } catch {
          // Некритично — показываем data URL напрямую
        }

        resultUrl = resultUrl || dataUrl
      }

      // Cleanup
      if (backgroundFile) URL.revokeObjectURL(backgroundSrc)

      // ── Step 3: Completion ─────────────────────────────────────
      setStage('saving')
      await new Promise(r => setTimeout(r, 400)) // Brief UX pause

      setResult(resultUrl)
      setStage('completed')

      console.log(`Mockup generated via: ${resultUrl ? (isPremium ? "Gemini Native 🚀" : "Local Engine") : "Canvas fallback"}`)

    } catch (error) {
      const msg = error instanceof Error ? error.message : String(error)
      console.error("Generation failed:", msg)
      setErrorMessage(msg)
      setStage('failed')
    }
  }


  const handleDownload = () => {
    if (!result) return
    const filename = `sjk-mockup-${location?.name?.replace(/\s+/g, "-") || "custom"}-${Date.now()}.jpg`
    downloadFile(result, filename)
  }

  const reset = () => {
    setCreativeFile(null)
    if (creativePreview) URL.revokeObjectURL(creativePreview)
    setCreativePreview(null)
    setBackgroundFile(null)
    setResult(null)
    setStage('idle')
    setErrorMessage(null)
    setResultIsPremium(false)
  }

  const isProcessing = stage !== 'idle' && stage !== 'completed' && stage !== 'failed'
  const progress = STAGE_PROGRESS[stage]

  if (!isMounted) return null

  return (
    <Dialog open={true} onOpenChange={(open) => { if (!open) { reset(); onClose() } }}>
      <DialogContent className="sm:max-w-[620px] border-border/40 bg-background/95 backdrop-blur-2xl">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-2xl font-bold tracking-tight">
            <Sparkles className="h-6 w-6 text-primary animate-pulse" />
            AI Mockup Creator
          </DialogTitle>
          <DialogDescription>
            {location ? (
              <>{t("creator_base")} <span className="font-semibold text-foreground">{location.name}</span></>
            ) : (
              t("creator_street_mode")
            )}
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-6 py-4 font-sans">

          {/* ── Upload Zone ─────────────────────────────────── */}
          {!result && !isProcessing && (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              {/* Креатив */}
              <div className="space-y-2">
                <label className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  {t("creator_client_banner")} <span className="text-red-400">*</span>
                </label>
                <label className={cn(
                  "flex flex-col items-center justify-center aspect-square rounded-2xl border-2 border-dashed transition-all cursor-pointer group",
                  creativeFile
                    ? "border-primary bg-primary/5"
                    : "border-border/60 hover:border-primary/50 hover:bg-muted/30"
                )}>
                  {creativePreview ? (
                    <div className="relative w-full h-full rounded-2xl overflow-hidden">
                      <img src={creativePreview} alt="Creative" className="w-full h-full object-contain p-2" />
                      <div className="absolute top-2 right-2 p-1 rounded-full bg-primary">
                        <Check className="h-3 w-3 text-white" />
                      </div>
                    </div>
                  ) : (
                    <>
                      <Upload className="h-10 w-10 text-muted-foreground mb-2 group-hover:text-primary transition-colors" />
                      <p className="text-xs font-medium text-center px-4 text-muted-foreground">
                        PNG, JPG, WEBP
                      </p>
                    </>
                  )}
                  <input type="file" className="hidden" onChange={handleCreativeChange} accept="image/*" />
                </label>
              </div>

              {/* Фон */}
              <div className="space-y-2">
                <label className="text-xs font-bold text-muted-foreground uppercase tracking-wider">
                  {t("creator_object_photo")} {!location && <span className="text-red-400">*</span>}
                </label>
                {!location || backgroundFile ? (
                  <label className={cn(
                    "flex flex-col items-center justify-center aspect-square rounded-2xl border-2 border-dashed transition-all cursor-pointer group",
                    backgroundFile
                      ? "border-green-500 bg-green-500/5"
                      : "border-border/60 hover:border-green-500/50 hover:bg-muted/30"
                  )}>
                    {backgroundFile ? (
                      <div className="flex flex-col items-center p-4 text-center gap-2">
                        <div className="p-2 rounded-full bg-green-500/10">
                          <Camera className="h-6 w-6 text-green-500" />
                        </div>
                        <p className="text-xs font-medium truncate max-w-[150px]">{backgroundFile.name}</p>
                        <Button
                          type="button"
                          variant="ghost"
                          size="sm"
                          className="text-xs h-7 text-muted-foreground"
                          onClick={(e) => { e.preventDefault(); handleAutoDetect() }}
                          disabled={isDetecting}
                        >
                          {isDetecting ? <Loader2 className="h-3 w-3 animate-spin mr-1" /> : <RefreshCw className="h-3 w-3 mr-1" />}
                          {t("creator_auto_detect")}
                        </Button>
                      </div>
                    ) : (
                      <>
                        <Camera className="h-10 w-10 text-muted-foreground mb-2 group-hover:text-green-500 transition-colors" />
                        <p className="text-xs font-medium text-center px-4 text-muted-foreground">
                          {t("creator_take_photo")}
                        </p>
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
                      src={getFullImageUrl(location.primary_photo_url)}
                      alt="Базовое фото"
                      className="h-full w-full object-cover transition-all duration-500 group-hover:scale-105"
                      onError={(e) => {
                        (e.target as HTMLImageElement).src =
                          'https://images.unsplash.com/photo-1542281286-9e0a16bb7366?auto=format&fit=crop&q=80&w=600'
                      }}
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex items-end p-3">
                      <p className="text-[10px] text-white font-medium bg-black/40 px-2 py-1 rounded-full backdrop-blur-md">
                        {t("creator_catalog_photo")}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ── Processing ──────────────────────────────────── */}
          {isProcessing && (
            <div className="flex flex-col items-center justify-center gap-6 py-10">
              <div className="relative">
                <div className="h-20 w-20 rounded-full border-4 border-primary/20 animate-pulse" />
                <Loader2 className="h-10 w-10 animate-spin text-primary absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" />
              </div>
              <div className="text-center space-y-3 w-full max-w-xs">
                <p className="text-lg font-bold bg-gradient-to-r from-primary to-purple-500 bg-clip-text text-transparent">
                  {STAGE_MESSAGES[stage]}
                </p>
                {/* Progress bar */}
                <div className="flex gap-1.5">
                  {[1, 2, 3, 4].map((i) => (
                    <div
                      key={i}
                      className={cn(
                        "h-1 flex-1 rounded-full transition-all duration-700",
                        i <= progress ? "bg-primary" : "bg-muted"
                      )}
                    />
                  ))}
                </div>
                <p className="text-xs text-muted-foreground">
                  {stage === 'rendering' ? (usePremium ? 'Gemini 3 Pro • SCHEMA v4.0 • Thinking: HIGH' : 'OpenCV Local Warp') : ''}
                  {stage === 'saving' ? t("creator_saving") : ''}
                </p>
              </div>
            </div>
          )}

          {/* ── Error ───────────────────────────────────────── */}
          {stage === 'failed' && (
            <div className="flex flex-col items-center gap-4 py-8">
              <div className="p-4 rounded-full bg-red-500/10 border border-red-500/20">
                <AlertCircle className="h-10 w-10 text-red-400" />
              </div>
              <div className="text-center space-y-1">
                <p className="font-bold text-red-400">{t("creator_gen_error")}</p>
                {errorMessage && (
                  <p className="text-xs text-muted-foreground max-w-xs">{errorMessage}</p>
                )}
              </div>
              <Button variant="outline" onClick={reset} className="gap-2">
                <RefreshCw className="h-4 w-4" />
                {t("creator_try_again")}
              </Button>
            </div>
          )}

          {/* ── Result ──────────────────────────────────────── */}
          {result && stage === 'completed' && (
            <div className="relative group overflow-hidden rounded-2xl border border-border/40 shadow-2xl animate-in zoom-in-95 duration-500">
              <img src={result} alt="Mockup Result" className="w-full h-auto object-contain" />
              <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/90 to-transparent p-5 translate-y-2 group-hover:translate-y-0 transition-transform duration-300">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 text-white">
                    <div className="h-8 w-8 rounded-full bg-green-500 flex items-center justify-center shadow-lg shadow-green-500/30">
                      <Check className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="font-bold text-sm">{t("creator_ready")}</p>
                      <p className="text-[10px] text-gray-400">
                        {resultIsPremium ? "Gemini 3 Pro Native AI" : "SJK Local Engine Client"}
                      </p>
                    </div>
                  </div>
                  <Button
                    size="sm"
                    onClick={handleDownload}
                    className="bg-white text-black hover:bg-white/90 font-bold rounded-full gap-2 shadow-lg"
                  >
                    <Download className="h-3.5 w-3.5" />
                    {t("creator_download")}
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* ── Footer ──────────────────────────────────────── */}
        <DialogFooter className="gap-3 sm:justify-between border-t border-border/40 pt-5">
          <Button
            variant="ghost"
            onClick={() => { reset(); onClose() }}
            className="rounded-full text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4 mr-2" />
            {t("creator_close")}
          </Button>

          {stage === 'idle' && (
            <div className="flex flex-col sm:flex-row gap-3">
              <Button
                variant="outline"
                onClick={() => setUsePremium(!usePremium)}
                className={cn(
                  "rounded-full gap-2 transition-all",
                  usePremium ? "border-purple-500 bg-purple-500/10 text-purple-600 hover:bg-purple-500/20" : ""
                )}
              >
                <Sparkles className={cn("h-4 w-4", usePremium ? "animate-pulse" : "")} />
                {usePremium ? "Premium Gemini Native Active" : "Enable Premium Gemini"}
              </Button>
              <Button
                disabled={!creativeFile || (!location && !backgroundFile)}
                onClick={handleGenerate}
                className="gap-2 bg-primary hover:bg-primary/90 text-primary-foreground font-bold px-10 rounded-full shadow-lg shadow-primary/20"
              >
                {usePremium ? <Sparkles className="h-4 w-4" /> : <Check className="h-4 w-4" />}
                {usePremium ? "Generate Premium" : t("creator_generate")}
              </Button>
            </div>
          )}

          {stage === 'completed' && (
            <div className="flex gap-2">
              <Button variant="secondary" onClick={reset} className="rounded-full">
                {t("creator_retry")}
              </Button>
              <Button
                onClick={handleDownload}
                className="bg-primary hover:bg-primary/90 font-bold rounded-full px-8 gap-2"
              >
                <Download className="h-4 w-4" />
                {t("creator_download")}
              </Button>
            </div>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
