'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Download, Calendar, Clock, Image as ImageIcon, Sparkles, Trash2, RefreshCw, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { API_ENDPOINTS } from "@/lib/config";
import { getFullImageUrl, downloadFile } from "@/lib/utils/url";

interface MockupHistoryItem {
  id: string;
  location_name: string;
  creative_url: string;
  result_url: string | null;
  status: string;
  created_at: string;
  processing_time: number;
}

const PAGE_SIZE = 12;

export function MockupHistory() {
  const [history, setHistory] = useState<MockupHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fetchHistory = useCallback(async (currentOffset = 0, append = false) => {
    setLoading(true);
    setError(null);
    try {
      const url = `${API_ENDPOINTS.HISTORY}?limit=${PAGE_SIZE}&offset=${currentOffset}`;
      const response = await fetch(url);
      if (!response.ok) throw new Error(`Server error: ${response.status}`);
      const data: MockupHistoryItem[] = await response.json();

      if (append) {
        setHistory((prev) => [...prev, ...data]);
      } else {
        setHistory(data);
      }
      setHasMore(data.length === PAGE_SIZE);
      setOffset(currentOffset + data.length);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка загрузки");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHistory(0, false);
  }, [fetchHistory]);

  const handleLoadMore = () => {
    fetchHistory(offset, true);
  };

  const handleDelete = async (id: string) => {
    setDeletingId(id);
    try {
      const response = await fetch(API_ENDPOINTS.DELETE_MOCKUP(id), { method: "DELETE" });
      if (response.ok) {
        setHistory((prev) => prev.filter((item) => item.id !== id));
      }
    } catch (err) {
      console.error("Delete failed:", err);
    } finally {
      setDeletingId(null);
    }
  };

  const handleDownload = (item: MockupHistoryItem) => {
    if (!item.result_url) return;
    const url = getFullImageUrl(item.result_url);
    const filename = `sjk-mockup-${item.location_name?.replace(/\s+/g, "-") || "unknown"}-${item.id.slice(0, 8)}.jpg`;
    downloadFile(url, filename);
  };

  // ── Error ───────────────────────────────────
  if (error && history.length === 0) {
    return (
      <div className="py-32 text-center border-2 border-dashed border-red-500/20 rounded-3xl bg-red-500/5">
        <div className="flex flex-col items-center gap-4">
          <div className="p-4 rounded-full bg-red-500/10">
            <AlertCircle className="h-8 w-8 text-red-400" />
          </div>
          <p className="font-bold text-red-400">Ошибка загрузки истории</p>
          <p className="text-xs text-zinc-500">{error}</p>
          <Button variant="outline" onClick={() => fetchHistory(0, false)} className="gap-2 border-red-500/30 text-red-400">
            <RefreshCw className="h-4 w-4" />
            Повторить
          </Button>
        </div>
      </div>
    );
  }

  // ── Loading ──────────────────────────────────
  if (loading && history.length === 0) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3].map((i) => (
          <div key={i} className="h-72 rounded-2xl bg-zinc-900/50 animate-pulse border border-white/5" />
        ))}
      </div>
    );
  }

  // ── Empty ────────────────────────────────────
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
      <div className="flex items-center justify-between">
        <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent">
          История генераций
        </h2>
        <Badge className="bg-zinc-900/60 border-white/10 text-zinc-400">
          {history.length} мокапов
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {history.map((item) => (
          <Card
            key={item.id}
            className="group bg-zinc-900/30 border-white/5 overflow-hidden backdrop-blur-md transition-all duration-500 hover:border-primary/50 hover:bg-zinc-900/50 hover:shadow-2xl hover:shadow-primary/10"
          >
            <div className="aspect-video relative bg-zinc-800 overflow-hidden">
              {item.result_url ? (
                <img
                  src={getFullImageUrl(item.result_url)}
                  alt={item.location_name}
                  className="object-cover w-full h-full transition-transform duration-700 group-hover:scale-110"
                  onError={(e) => {
                    (e.target as HTMLImageElement).style.display = 'none'
                  }}
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
                  <div className={`h-1.5 w-1.5 rounded-full mr-1.5 ${
                    item.status === 'completed' ? 'bg-green-400 shadow-[0_0_8px_rgba(74,222,128,0.5)]' : 'bg-red-400'
                  }`} />
                  {item.status.toUpperCase()}
                </Badge>
              </div>
            </div>

            <CardHeader className="p-4">
              <div className="flex justify-between items-start">
                <div className="space-y-1 flex-1 min-w-0">
                  <CardTitle className="text-base font-bold text-white group-hover:text-primary transition-colors truncate">
                    {item.location_name || "Street Upload"}
                  </CardTitle>
                  <div className="flex items-center text-[10px] text-zinc-500 font-bold uppercase tracking-widest gap-4">
                    <span className="flex items-center gap-1.5">
                      <Calendar size={10} className="text-primary/50" />
                      {new Date(item.created_at).toLocaleDateString("vi-VN")}
                    </span>
                    <span className="flex items-center gap-1.5">
                      <Clock size={10} className="text-primary/50" />
                      {item.processing_time}s
                    </span>
                  </div>
                </div>

                <div className="flex gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity duration-300 shrink-0 ml-2">
                  {item.result_url && (
                    <Button
                      variant="outline"
                      size="icon"
                      className="h-8 w-8 border-white/10 bg-black/40 backdrop-blur-md hover:bg-primary hover:text-white hover:border-primary transition-all"
                      onClick={() => handleDownload(item)}
                      title="Скачать"
                    >
                      <Download size={13} />
                    </Button>
                  )}
                  <Button
                    variant="outline"
                    size="icon"
                    className="h-8 w-8 border-red-500/20 bg-black/40 backdrop-blur-md hover:bg-red-500 hover:text-white hover:border-red-500 transition-all"
                    onClick={() => handleDelete(item.id)}
                    disabled={deletingId === item.id}
                    title="Удалить"
                  >
                    {deletingId === item.id
                      ? <RefreshCw size={13} className="animate-spin" />
                      : <Trash2 size={13} />
                    }
                  </Button>
                </div>
              </div>
            </CardHeader>
          </Card>
        ))}
      </div>

      {/* Load More */}
      {hasMore && (
        <div className="flex justify-center pt-4">
          <Button
            variant="outline"
            onClick={handleLoadMore}
            disabled={loading}
            className="gap-2 border-white/10 hover:border-primary/50"
          >
            {loading ? <RefreshCw className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
            Загрузить ещё
          </Button>
        </div>
      )}
    </div>
  );
}
