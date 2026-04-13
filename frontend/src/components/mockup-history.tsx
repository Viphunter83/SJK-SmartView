'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Download, Calendar, Clock, Image as ImageIcon, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface MockupHistoryItem {
  id: string;
  location_name: string;
  creative_url: string;
  result_url: string;
  status: string;
  created_at: string;
  processing_time: number;
}

export function MockupHistory() {
  const [history, setHistory] = useState<MockupHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  const getFullUrl = (url: string) => {
    if (!url) return '';
    if (url.startsWith('http') || url.startsWith('data:')) return url;
    return `http://localhost:8000${url}`;
  };

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/history');
        if (response.ok) {
          const data = await response.json();
          setHistory(data);
        }
      } catch (error) {
        console.error('Failed to fetch history:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, []);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-64 rounded-2xl bg-zinc-900/50 animate-pulse border border-white/5" />
        ))}
      </div>
    );
  }

  if (history.length === 0) {
    return (
      <div className="py-32 text-center border-2 border-dashed border-white/5 rounded-3xl bg-zinc-900/10 backdrop-blur-sm">
        <div className="flex flex-col items-center gap-4">
          <div className="p-5 rounded-full bg-zinc-900/50 border border-white/5">
            <Sparkles className="h-10 w-10 text-zinc-700" />
          </div>
          <div className="space-y-1">
            <p className="text-xl font-bold text-zinc-400">История генераций пуста</p>
            <p className="text-zinc-600 text-sm">Создайте свой первый мокап в каталоге экранов</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent">
        Последние генерации
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {history.map((item) => (
          <Card key={item.id} className="group bg-zinc-900/30 border-white/5 overflow-hidden backdrop-blur-md transition-all duration-500 hover:border-primary/50 hover:bg-zinc-900/50 hover:shadow-2xl hover:shadow-primary/10">
            <div className="aspect-video relative bg-zinc-800 overflow-hidden">
              {item.result_url ? (
                <img 
                  src={getFullUrl(item.result_url)} 
                  alt={item.location_name}
                  className="object-cover w-full h-full transition-transform duration-700 group-hover:scale-110"
                />
              ) : (
                <div className="flex h-full w-full items-center justify-center text-zinc-700">
                  <ImageIcon className="h-12 w-12" />
                </div>
              )}
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-60" />
              <div className="absolute top-3 right-3">
                <Badge className={
                  item.status === 'completed' 
                    ? 'bg-green-500/20 text-green-400 border-green-500/30 backdrop-blur-md' 
                    : item.status === 'processing' 
                    ? 'bg-blue-500/20 text-blue-400 border-blue-500/30 backdrop-blur-md animate-pulse'
                    : 'bg-red-500/20 text-red-400 border-red-500/30 backdrop-blur-md'
                }>
                  <div className={`h-1.5 w-1.5 rounded-full mr-2 ${item.status === 'completed' ? 'bg-green-400 shadow-[0_0_8px_rgba(74,222,128,0.5)]' : 'bg-red-400'}`} />
                  {item.status.toUpperCase()}
                </Badge>
              </div>
            </div>
            <CardHeader className="p-4">
              <div className="flex justify-between items-start">
                <div className="space-y-1">
                  <CardTitle className="text-lg font-bold text-white group-hover:text-primary transition-colors">
                    {item.location_name}
                  </CardTitle>
                  <div className="flex items-center text-[10px] text-zinc-500 font-bold uppercase tracking-widest gap-4">
                    <span className="flex items-center gap-1.5">
                      <Calendar size={12} className="text-primary/50" /> {new Date(item.created_at).toLocaleDateString()}
                    </span>
                    <span className="flex items-center gap-1.5">
                      <Clock size={12} className="text-primary/50" /> {item.processing_time}s
                    </span>
                  </div>
                </div>
                <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <Button variant="outline" size="icon" className="h-9 w-9 border-white/10 bg-black/40 backdrop-blur-md hover:bg-primary hover:text-white hover:border-primary transition-all shadow-lg" asChild>
                    <a href={getFullUrl(item.result_url)} download={`mockup-${item.id}.jpg`}>
                      <Download size={16} />
                    </a>
                  </Button>
                </div>
              </div>
            </CardHeader>
          </Card>
        ))}
      </div>
    </div>
  );
}
