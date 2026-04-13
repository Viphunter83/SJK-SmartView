'use client';

import React, { useState } from 'react';
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar"
import { AppSidebar } from "@/components/app-sidebar"
import { LocationCatalog } from "@/components/location-catalog"
import { MockupHistory } from "@/components/mockup-history"
import { MockupCreator } from "@/components/mockup-creator"
import { Button } from "@/components/ui/button"
import { History, LayoutGrid, Map as MapIcon } from "lucide-react"
import dynamic from 'next/dynamic'
import { useAuth } from "@/lib/auth-context"

// Leaflet работает только в браузере — динамический импорт без SSR
const LocationMap = dynamic(() => import('@/components/location-map'), {
  ssr: false,
  loading: () => <div className="h-[calc(100vh-12rem)] w-full bg-zinc-900/50 animate-pulse rounded-3xl" />
})

interface Location {
  id: string;
  name: string;
  category: string;
  address?: string;
  primary_photo_url?: string;
  screen_geometry?: { x: number; y: number }[];
  aspect_ratio?: number;
}

export default function Home() {
  const [activeTab, setActiveTab] = useState<'catalog' | 'history' | 'map'>('catalog');
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [isCreatorOpen, setIsCreatorOpen] = useState(false);
  const { user } = useAuth()

  const handleOpenCreator = (location: Location | null = null) => {
    setSelectedLocation(location);
    setIsCreatorOpen(true);
  };

  const handleLocationSelectFromMap = (location: Location) => {
    // При выборе с карты — сразу открываем MockupCreator
    handleOpenCreator(location);
    setActiveTab('catalog'); // Переключаемся на каталог для визуального обзора
  };

  return (
    <SidebarProvider>
      <div className="flex min-h-screen w-full bg-black text-white selection:bg-primary/30">
        <AppSidebar
          currentTab={activeTab}
          onTabChange={setActiveTab}
          onOpenCreator={() => handleOpenCreator(null)}
        />
        <main className="flex-1 overflow-auto bg-gradient-to-br from-black via-[#0a0a0a] to-[#0f0f0f]">
          <header className="flex h-16 shrink-0 items-center justify-between border-b border-white/5 px-6 backdrop-blur-md sticky top-0 z-50 bg-black/40">
            <div className="flex items-center gap-4">
              <SidebarTrigger />
              <div className="flex bg-zinc-900/50 backdrop-blur-md border border-white/5 rounded-xl p-1 shadow-inner">
                <Button
                  variant={activeTab === 'catalog' ? 'secondary' : 'ghost'}
                  size="sm"
                  onClick={() => setActiveTab('catalog')}
                  className="gap-2 transition-all duration-300"
                >
                  <LayoutGrid size={16} /> Каталог
                </Button>
                <Button
                  variant={activeTab === 'history' ? 'secondary' : 'ghost'}
                  size="sm"
                  onClick={() => setActiveTab('history')}
                  className="gap-2 transition-all duration-300"
                >
                  <History size={16} /> История
                </Button>
                <Button
                  variant={activeTab === 'map' ? 'secondary' : 'ghost'}
                  size="sm"
                  onClick={() => setActiveTab('map')}
                  className="gap-2 transition-all duration-300"
                >
                  <MapIcon size={16} /> Карта
                </Button>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-sm font-medium text-zinc-400">
                Менеджер: <span className="text-white hover:text-primary transition-colors cursor-default">{user?.email?.split('@')[0] || "Shojiki Staff"}</span>
              </div>
              <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-primary to-purple-600 shadow-[0_0_15px_rgba(var(--primary),0.3)] ring-1 ring-white/10" />
            </div>
          </header>

          <div className="p-6 max-w-[1600px] mx-auto min-h-[calc(100vh-4rem)]">
            <div className="animate-in fade-in slide-in-from-bottom-2 duration-500">
              {activeTab === 'catalog' && (
                <LocationCatalog onSelect={handleOpenCreator} />
              )}
              {activeTab === 'history' && (
                <MockupHistory />
              )}
              {activeTab === 'map' && (
                <LocationMap onSelect={handleLocationSelectFromMap} />
              )}
            </div>
          </div>

          {isCreatorOpen && (
            <MockupCreator
              location={selectedLocation}
              onClose={() => {
                setIsCreatorOpen(false)
                setSelectedLocation(null)
              }}
            />
          )}
        </main>
      </div>
    </SidebarProvider>
  );
}
