"use client"

import * as React from "react"
import { Search, MapPin, ImageIcon, Camera, AlertCircle, RefreshCw, SlidersHorizontal } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { API_ENDPOINTS } from "@/lib/config"
import { getFullImageUrl } from "@/lib/utils/url"
import { useLanguage } from "@/lib/i18n"

interface Location {
  id: string;
  name: string;
  category: string;
  address: string;
  primary_photo_url?: string;
  is_active?: boolean;
}

type CategoryFilter = 'all' | string;

const CATEGORY_COLORS: Record<string, string> = {
  "Outdoor Digital": "from-blue-500 to-cyan-500",
  "3D Digital": "from-purple-500 to-pink-500",
  "Billboard": "from-orange-500 to-yellow-500",
  "Indoor LCD": "from-green-500 to-emerald-500",
};

interface LocationCatalogProps {
  onSelect: (location: Location | null) => void;
}

export function LocationCatalog({ onSelect }: LocationCatalogProps) {
  const [searchQuery, setSearchQuery] = React.useState("")
  const [locations, setLocations] = React.useState<Location[]>([])
  const [loading, setLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)
  const [activeCategory, setActiveCategory] = React.useState<CategoryFilter>('all')
  const { t } = useLanguage()

  const fetchLocations = React.useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(API_ENDPOINTS.LOCATIONS)
      if (!response.ok) throw new Error(`Server error: ${response.status}`)
      const data = await response.json()
      setLocations(data)
    } catch (err) {
      const msg = err instanceof Error ? err.message : t("err_network")
      setError(msg)
      console.error("Failed to fetch locations:", err)
    } finally {
      setLoading(false)
    }
  }, [])

  React.useEffect(() => {
    fetchLocations()
  }, [fetchLocations])

  // Уникальные категории из данных
  const categories = React.useMemo(() => {
    const cats = [...new Set(locations.map((l) => l.category).filter(Boolean))]
    return cats.sort()
  }, [locations])

  const filteredLocations = React.useMemo(() =>
    locations.filter((loc) => {
      const matchSearch =
        loc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (loc.address || "").toLowerCase().includes(searchQuery.toLowerCase())
      const matchCategory = activeCategory === 'all' || loc.category === activeCategory
      return matchSearch && matchCategory
    }),
    [locations, searchQuery, activeCategory]
  )

  return (
    <div className="flex flex-col gap-6">
      {/* ── Header ───────────────────────────────── */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent">
          {t("screens_network")}
        </h2>
        <div className="flex items-center gap-3 flex-1 max-w-sm">
          <Button
            variant="outline"
            className="gap-2 border-primary/50 text-primary hover:bg-primary/5 shadow-[0_0_15px_rgba(var(--primary),0.1)] shrink-0"
            onClick={() => onSelect(null)}
          >
            <Camera className="h-4 w-4" />
            Street Upload
          </Button>
          <div className="relative w-full">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder={t("search_placeholder")}
              className="pl-8 bg-zinc-900/50 border-white/5 focus-visible:ring-primary/50"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* ── Category Chips ───────────────────────── */}
      {categories.length > 0 && (
        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setActiveCategory('all')}
            className={`px-3 py-1 rounded-full text-xs font-bold transition-all ${
              activeCategory === 'all'
                ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/20'
                : 'bg-zinc-900/50 text-zinc-400 hover:text-white border border-white/5'
            }`}
          >
            {t("all")}
          </button>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`px-3 py-1 rounded-full text-xs font-bold transition-all ${
                activeCategory === cat
                  ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/20'
                  : 'bg-zinc-900/50 text-zinc-400 hover:text-white border border-white/5'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      )}

      {/* ── Error State ──────────────────────────── */}
      {error && (
        <div className="flex flex-col items-center gap-4 py-16 border-2 border-dashed border-red-500/20 rounded-3xl bg-red-500/5">
          <div className="p-4 rounded-full bg-red-500/10">
            <AlertCircle className="h-8 w-8 text-red-400" />
          </div>
          <div className="text-center space-y-1">
            <p className="font-bold text-red-400">{t("err_catalog_load")}</p>
            <p className="text-xs text-zinc-500">{error}</p>
          </div>
          <Button variant="outline" onClick={fetchLocations} className="gap-2 border-red-500/30 text-red-400 hover:bg-red-500/10">
            <RefreshCw className="h-4 w-4" />
            {t("retry")}
          </Button>
        </div>
      )}

      {/* ── Loading Skeleton ─────────────────────── */}
      {loading && !error && (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-80 rounded-2xl bg-zinc-900/50 animate-pulse border border-white/5" />
          ))}
        </div>
      )}

      {/* ── Grid ─────────────────────────────────── */}
      {!loading && !error && (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filteredLocations.map((location) => (
            <Card
              key={location.id}
              className="group overflow-hidden border-white/5 bg-zinc-900/30 backdrop-blur-md transition-all duration-500 hover:border-primary/50 hover:bg-zinc-900/60 hover:shadow-2xl hover:shadow-primary/10"
            >
              <div className="relative aspect-[16/10] bg-zinc-800 overflow-hidden">
                {location.primary_photo_url ? (
                  <img
                    src={getFullImageUrl(location.primary_photo_url)}
                    alt={location.name}
                    className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src =
                        'https://images.unsplash.com/photo-1542281286-9e0a16bb7366?auto=format&fit=crop&q=80&w=600'
                    }}
                  />
                ) : (
                  <div className="flex h-full w-full items-center justify-center text-zinc-700">
                    <ImageIcon className="h-12 w-12" />
                  </div>
                )}
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-60 transition-opacity group-hover:opacity-30" />

                {/* Online/Offline badge */}
                <Badge
                  className="absolute right-3 top-3 gap-1 bg-black/60 backdrop-blur-xl border border-white/10"
                >
                  <div className={`h-1.5 w-1.5 rounded-full ${
                    location.is_active !== false
                      ? 'bg-green-500 shadow-[0_0_8px_#22c55e]'
                      : 'bg-red-500'
                  }`} />
                  {location.is_active !== false ? t("active") : t("offline")}
                </Badge>
              </div>

              <CardHeader className="p-4 space-y-1">
                <div className="flex items-center justify-between">
                  <Badge variant="outline" className="text-[10px] uppercase font-bold tracking-widest text-primary/80 border-primary/20 bg-primary/5">
                    {location.category}
                  </Badge>
                </div>
                <CardTitle className="line-clamp-1 text-lg font-bold group-hover:text-primary transition-colors">
                  {location.name}
                </CardTitle>
              </CardHeader>

              <CardContent className="px-4 pb-4 pt-0 text-sm text-zinc-500">
                <div className="flex items-center gap-1.5">
                  <MapPin className="h-3.5 w-3.5 shrink-0" />
                  <span className="line-clamp-1 font-medium italic">{location.address || t("no_address")}</span>
                </div>
              </CardContent>

              <CardFooter className="p-4 pt-0">
                <Button
                  onClick={() => onSelect(location)}
                  className="w-full gap-2 font-bold bg-white text-black hover:bg-primary hover:text-white transition-all duration-300 shadow-lg"
                >
                  <ImageIcon className="h-4 w-4" />
                  {t("create_mockup")}
                </Button>
              </CardFooter>
            </Card>
          ))}

          {filteredLocations.length === 0 && (
            <div className="col-span-full py-32 text-center border-2 border-dashed border-white/5 rounded-3xl bg-zinc-900/20">
              <div className="flex flex-col items-center gap-3">
                <div className="p-4 rounded-full bg-zinc-900/50 border border-white/5">
                  <SlidersHorizontal className="h-8 w-8 text-zinc-700" />
                </div>
                <p className="text-zinc-500 font-medium">{t("no_results")}</p>
                <p className="text-zinc-600 text-sm">{t("try_different_search")}</p>
                <Button variant="ghost" size="sm" onClick={() => { setSearchQuery(""); setActiveCategory("all") }}>
                  {t("reset_filters")}
                </Button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
