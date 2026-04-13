"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import { Box, Sparkles, Loader2, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"

export default function LoginPage() {
  const [isLoading, setIsLoading] = React.useState(false)
  const router = useRouter()

  async function onSubmit(event: React.SyntheticEvent) {
    event.preventDefault()
    setIsLoading(true)

    // Имитация авторизации для MVP
    setTimeout(() => {
      setIsLoading(false)
      router.push("/")
    }, 1500)
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-black p-6 font-sans">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(120,50,255,0.1),transparent_50%)]" />
      
      <Card className="relative w-full max-w-md border-white/5 bg-zinc-900/40 backdrop-blur-2xl shadow-2xl shadow-purple-500/10 transition-all duration-500 hover:border-primary/30">
        <CardHeader className="space-y-4 text-center">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-2xl shadow-primary/40 rotate-12 transition-transform hover:rotate-0">
            <Box className="h-8 w-8" />
          </div>
          <div className="space-y-2">
            <CardTitle className="text-3xl font-bold tracking-tight text-white">SJK SmartView</CardTitle>
            <CardDescription className="text-zinc-500 text-sm">
              Войдите в систему управления рекламными поверхностями
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit}>
            <div className="grid gap-6">
              <div className="grid gap-2">
                <Label htmlFor="email" className="text-zinc-400 text-xs font-bold uppercase tracking-widest pl-1">Email</Label>
                <Input
                  id="email"
                  placeholder="name@shojiki.ru"
                  type="email"
                  autoCapitalize="none"
                  autoComplete="email"
                  autoCorrect="off"
                  disabled={isLoading}
                  className="bg-zinc-900/50 border-white/5 focus-visible:ring-primary/50 h-11"
                  required
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="password" className="text-zinc-400 text-xs font-bold uppercase tracking-widest pl-1">Пароль</Label>
                <Input
                  id="password"
                  type="password"
                  disabled={isLoading}
                  className="bg-zinc-900/50 border-white/5 focus-visible:ring-primary/50 h-11"
                  required
                />
              </div>
              <Button disabled={isLoading} className="h-11 font-bold shadow-lg shadow-primary/20 transition-all active:scale-95">
                {isLoading ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <span className="flex items-center gap-2">
                    Войти в систему <ArrowRight className="h-4 w-4" />
                  </span>
                )}
              </Button>
            </div>
          </form>
        </CardContent>
        <CardFooter className="flex flex-col gap-4 text-center">
          <div className="text-xs text-zinc-600 flex items-center gap-1">
            <Sparkles className="h-3 w-3" /> Корпоративный доступ Shojiki
          </div>
        </CardFooter>
      </Card>
    </div>
  )
}
