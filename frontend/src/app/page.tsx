'use client';

import React, { useState } from 'react';
import { AppSidebar } from "@/components/app-sidebar"
import { LocationCatalog } from "@/components/location-catalog"
import { MockupHistory } from "@/components/mockup-history"
import { MockupCreator } from "@/components/mockup-creator"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"
import { History, LayoutGrid } from "lucide-react"

export default function Home() {
  const [activeTab, setActiveTab] = useState<'catalog' | 'history'>('catalog');
  const [selectedLocation, setSelectedLocation] = useState<any>(null);
  const [isCreatorOpen, setIsCreatorOpen] = useState(false);

  const handleSelectLocation = (location: any) => {
    setSelectedLocation(location);
    setIsCreatorOpen(true);
  };

  return (
    <div className="flex min-h-screen w-full bg-black text-white">
      <AppSidebar />
      <main className="flex-1 overflow-auto">
        <header className="flex h-16 shrink-0 items-center justify-between border-b border-zinc-800 px-6 backdrop-blur-md sticky top-0 z-50 bg-black/50">
          <div className="flex items-center gap-4">
            <SidebarTrigger />
            <div className="flex bg-zinc-900 rounded-lg p-1 p-1">
              <Button 
                variant={activeTab === 'catalog' ? 'secondary' : 'ghost'} 
                size="sm"
                onClick={() => setActiveTab('catalog')}
                className="gap-2"
              >
                <LayoutGrid size={16} /> Каталог
              </Button>
              <Button 
                variant={activeTab === 'history' ? 'secondary' : 'ghost'} 
                size="sm"
                onClick={() => setActiveTab('history')}
                className="gap-2"
              >
                <History size={16} /> История
              </Button>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="text-sm font-medium text-zinc-400">
              Менеджер: <span className="text-white">Константин В.</span>
            </div>
            <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-orange-500 to-purple-500 shadow-lg shadow-orange-500/20" />
          </div>
        </header>

        <div className="p-6">
          {activeTab === 'catalog' ? (
            <LocationCatalog onSelect={handleSelectLocation} />
          ) : (
            <MockupHistory />
          )}
        </div>

        {isCreatorOpen && (
          <MockupCreator 
            location={selectedLocation} 
            onClose={() => setIsCreatorOpen(false)} 
          />
        )}
      </main>
    </div>
  );
}
