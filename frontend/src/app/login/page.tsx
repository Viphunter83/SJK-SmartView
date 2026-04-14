"use client"

import * as React from "react"
import { useRouter } from "next/navigation"
import { Box, Sparkles, Loader2, ArrowRight, AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { auth } from "@/lib/firebase"
import { signInWithEmailAndPassword } from "firebase/auth"
import { useLanguage } from "@/lib/i18n"

export default function LoginPage() {
  const [isLoading, setIsLoading] = React.useState(false)
  const [email, setEmail] = React.useState("")
  const [password, setPassword] = React.useState("")
  const [error, setError] = React.useState<string | null>(null)
  const router = useRouter()
  const { t } = useLanguage()

  async function onSubmit(event: React.SyntheticEvent) {
    event.preventDefault()
    setIsLoading(true)
    setError(null)

    try {
      await signInWithEmailAndPassword(auth, email, password)
      router.push("/")
    } catch (err: unknown) {
      console.error("Login error:", err)
      // Переводим Firebase коды ошибок в понятные сообщения
      const code = (err as { code?: string }).code || ""
      if (code === "auth/user-not-found" || code === "auth/wrong-password" || code === "auth/invalid-credential") {
        setError(t("err_invalid_cred"))
      } else if (code === "auth/too-many-requests") {
        setError(t("err_too_many_req"))
      } else {
        setError(t("err_network"))
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-black p-6 font-sans">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(120,50,255,0.1),transparent_50%)]" />
      
      <Card className="relative w-full max-w-md border-white/5 bg-zinc-900/40 backdrop-blur-2xl shadow-2xl shadow-purple-500/10 transition-all duration-500 hover:border-primary/30">
        <CardHeader className="space-y-4 text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-zinc-900 border border-white/10 shadow-2xl shadow-primary/20 rotate-12 transition-transform hover:rotate-0 overflow-hidden">
            <img src="/logo.png" className="h-12 w-12 object-contain" alt="SJK SmartView Logo" />
          </div>
          <div className="space-y-2">
            <CardTitle className="text-3xl font-bold tracking-tight text-white">{t("login_title")}</CardTitle>
            <CardDescription className="text-zinc-500 text-sm">
              {t("login_subtitle")}
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit}>
            <div className="grid gap-6">
              <div className="grid gap-2">
                <Label htmlFor="email" className="text-zinc-400 text-xs font-bold uppercase tracking-widest pl-1">{t("email_label")}</Label>
                <Input
                  id="email"
                  placeholder={t("email_placeholder")}
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  autoCapitalize="none"
                  autoComplete="email"
                  autoCorrect="off"
                  disabled={isLoading}
                  className="bg-zinc-900/50 border-white/5 focus-visible:ring-primary/50 h-11"
                  required
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="password" className="text-zinc-400 text-xs font-bold uppercase tracking-widest pl-1">{t("password_label")}</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={isLoading}
                  className="bg-zinc-900/50 border-white/5 focus-visible:ring-primary/50 h-11"
                  required
                />
              </div>
              {error && (
                <div className="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  {error}
                </div>
              )}
              <Button disabled={isLoading} className="h-11 font-bold shadow-lg shadow-primary/20 transition-all active:scale-95">
                {isLoading ? (
                  <span className="flex items-center"><Loader2 className="mr-2 h-4 w-4 animate-spin" /> {t("login_loading")}</span>
                ) : (
                  <span className="flex items-center gap-2">
                    {t("login_button")} <ArrowRight className="h-4 w-4" />
                  </span>
                )}
              </Button>
            </div>
          </form>
        </CardContent>

        <CardFooter className="flex flex-col gap-4 text-center">
          <div className="text-xs text-zinc-600 flex items-center gap-1">
            <Sparkles className="h-3 w-3" /> {t("login_corp_access")}
          </div>
        </CardFooter>
      </Card>
    </div>
  )
}
