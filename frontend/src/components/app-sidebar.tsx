"use client"

import * as React from "react"
import { Monitor, Map, History, Plus, Box, LogOut, Loader2 } from "lucide-react"
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

interface AppSidebarProps {
  currentTab: 'catalog' | 'history' | 'map';
  onTabChange: (tab: 'catalog' | 'history' | 'map') => void;
  onOpenCreator: () => void;
}

export function AppSidebar({ currentTab, onTabChange, onOpenCreator }: AppSidebarProps) {
  const { logout } = useAuth()
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
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-lg shadow-primary/30">
            <Box className="h-5 w-5" />
          </div>
          <span className="text-xl font-bold tracking-tight text-foreground">SJK SmartView</span>
        </div>
      </SidebarHeader>

      <SidebarContent className="px-2">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              tooltip="Каталог экранов"
              isActive={currentTab === 'catalog'}
              onClick={() => onTabChange('catalog')}
            >
              <Monitor className="h-5 w-5" />
              <span>Каталог экранов</span>
            </SidebarMenuButton>
          </SidebarMenuItem>

          <SidebarMenuItem>
            <SidebarMenuButton
              tooltip="Загрузить с улицы"
              onClick={onOpenCreator}
            >
              <Plus className="h-5 w-5" />
              <span>Загрузить с улицы</span>
            </SidebarMenuButton>
          </SidebarMenuItem>

          <SidebarMenuItem>
            <SidebarMenuButton
              tooltip="История мокапов"
              isActive={currentTab === 'history'}
              onClick={() => onTabChange('history')}
            >
              <History className="h-5 w-5" />
              <span>История мокапов</span>
            </SidebarMenuButton>
          </SidebarMenuItem>

          <SidebarMenuItem>
            <SidebarMenuButton
              tooltip="Карта объектов"
              isActive={currentTab === 'map'}
              onClick={() => onTabChange('map')}
            >
              <Map className="h-5 w-5" />
              <span>Карта объектов</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarContent>

      <SidebarFooter className="p-4">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              tooltip="Выйти"
              onClick={handleLogout}
              disabled={isLoggingOut}
              className="text-red-400 hover:text-red-300 hover:bg-red-500/10 disabled:opacity-50"
            >
              {isLoggingOut ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <LogOut className="h-5 w-5" />
              )}
              <span>{isLoggingOut ? "Выход..." : "Выйти"}</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  )
}
