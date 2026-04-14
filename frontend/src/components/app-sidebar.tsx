"use client"

import * as React from "react"
import { Monitor, Map, History, Plus, Box, LogOut, Loader2, Smartphone } from "lucide-react"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import { useAuth } from "@/lib/auth-context"
import { useLanguage } from "@/lib/i18n"

interface AppSidebarProps {
  currentTab: 'catalog' | 'history' | 'map';
  onTabChange: (tab: 'catalog' | 'history' | 'map') => void;
  onOpenCreator: () => void;
}

export function AppSidebar({ currentTab, onTabChange, onOpenCreator }: AppSidebarProps) {
  const { logout } = useAuth()
  const { t } = useLanguage()
  const [isLoggingOut, setIsLoggingOut] = React.useState(false)

  const handleLogout = async () => {
    setIsLoggingOut(true)
    try {
      await logout() // Реальный Firebase signOut + редирект
    } finally {
      setIsLoggingOut(false)
    }
  }

  return (
    <Sidebar collapsible="icon" className="border-r border-border/40 bg-background/50 backdrop-blur-xl">
      <SidebarHeader className="p-4">
        <div className="flex items-center gap-3 px-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-zinc-900 border border-white/10 shadow-lg shadow-primary/20 overflow-hidden">
            <img src="/logo.png" className="h-7 w-7 object-contain" alt="Logo" />
          </div>
          <span className="text-xl font-bold tracking-tight text-foreground">SJK SmartView</span>
        </div>
      </SidebarHeader>

      <SidebarContent className="px-2">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              tooltip={t("screen_catalog")}
              isActive={currentTab === 'catalog'}
              onClick={() => onTabChange('catalog')}
            >
              <Monitor className="h-5 w-5" />
              <span>{t("screen_catalog")}</span>
            </SidebarMenuButton>
          </SidebarMenuItem>

          <SidebarMenuItem>
            <SidebarMenuButton
              tooltip={t("street_upload")}
              onClick={onOpenCreator}
            >
              <Plus className="h-5 w-5" />
              <span>{t("street_upload")}</span>
            </SidebarMenuButton>
          </SidebarMenuItem>

          <SidebarMenuItem>
            <SidebarMenuButton
              tooltip={t("mockup_history")}
              isActive={currentTab === 'history'}
              onClick={() => onTabChange('history')}
            >
              <History className="h-5 w-5" />
              <span>{t("mockup_history")}</span>
            </SidebarMenuButton>
          </SidebarMenuItem>

          <SidebarMenuItem>
            <SidebarMenuButton
              tooltip={t("location_map")}
              isActive={currentTab === 'map'}
              onClick={() => onTabChange('map')}
            >
              <Map className="h-5 w-5" />
              <span>{t("location_map")}</span>
            </SidebarMenuButton>
          </SidebarMenuItem>

          <SidebarMenuItem>
            <SidebarMenuButton
              tooltip={t("pwa_install")}
              asChild
            >
              <a href="https://github.com/Viphunter83/SJK-SmartView/blob/main/docs/user/PWA_INSTALLATION_GUIDE.md" target="_blank" rel="noopener noreferrer">
                <Smartphone className="h-5 w-5" />
                <span>{t("pwa_install")}</span>
              </a>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarContent>

      <SidebarFooter className="p-4">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              tooltip={t("logout")}
              onClick={handleLogout}
              disabled={isLoggingOut}
              className="text-red-400 hover:text-red-300 hover:bg-red-500/10 disabled:opacity-50"
            >
              {isLoggingOut ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <LogOut className="h-5 w-5" />
              )}
              <span>{isLoggingOut ? t("logging_out") : t("logout")}</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  )
}
