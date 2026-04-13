"use client"

import * as React from "react"
import { 
  Monitor, 
  Map, 
  History, 
  Settings, 
  Plus, 
  Box,
  Image as ImageIcon,
  LogOut
} from "lucide-react"
import { useRouter } from "next/navigation"

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"

interface AppSidebarProps {
  currentTab: 'catalog' | 'history' | 'map';
  onTabChange: (tab: 'catalog' | 'history' | 'map') => void;
  onOpenCreator: () => void;
}

export function AppSidebar({ currentTab, onTabChange, onOpenCreator }: AppSidebarProps) {
  const router = useRouter()
  
  const handleLogout = () => {
    // В MVP просто редирект на логин
    router.push('/login')
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
              tooltip="История"
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
            <SidebarMenuButton tooltip="Выйти" onClick={handleLogout} className="text-red-400 hover:text-red-300 hover:bg-red-500/10">
              <LogOut className="h-5 w-5" />
              <span>Выйти</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </Sidebar>
  )
}
