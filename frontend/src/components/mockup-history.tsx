'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Download, ExternalLink, Calendar, Clock } from 'lucide-react';
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
          <div key={i} className="h-48 rounded-xl bg-zinc-900/50 animate-pulse border border-zinc-800" />
        ))}
      </div>
    );
  }

  if (history.length === 0) {
    return (
      <div className="py-20 text-center border-2 border-dashed border-zinc-800 rounded-2xl">
        <p className="text-zinc-500 italic">История генераций пока пуста. Создайте свой первый мокап!</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {history.map((item) => (
        <Card key={item.id} className="bg-zinc-900/40 border-zinc-800 overflow-hidden group">
          <div className="aspect-video relative bg-zinc-800">
            {item.result_url && (
              <img 
                src={item.result_url} 
                alt={item.location_name}
                className="object-cover w-full h-full"
              />
            )}
            <div className="absolute top-2 right-2 flex gap-2">
              <Badge className={item.status === 'completed' ? 'bg-green-600' : 'bg-red-600'}>
                {item.status}
              </Badge>
            </div>
          </div>
          <CardHeader className="p-4">
            <div className="flex justify-between items-start">
              <div>
                <CardTitle className="text-base text-white truncate max-w-[150px]">
                  {item.location_name}
                </CardTitle>
                <div className="flex items-center text-xs text-zinc-500 mt-1 gap-3">
                  <span className="flex items-center gap-1">
                    <Calendar size={12} /> {new Date(item.created_at).toLocaleDateString()}
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock size={12} /> {item.processing_time}s
                  </span>
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant="ghost" size="icon" className="h-8 w-8 text-zinc-400 hover:text-white" asChild>
                  <a href={item.result_url} download={`mockup-${item.id}.jpg`}>
                    <Download size={16} />
                  </a>
                </Button>
              </div>
            </div>
          </CardHeader>
        </Card>
      ))}
    </div>
  );
}
