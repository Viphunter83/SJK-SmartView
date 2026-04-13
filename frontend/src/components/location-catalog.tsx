"use client"

import * as React from "react"
import { Search, MapPin, ImageIcon, Camera } from "lucide-react"

import { Input } from "@/components/ui/input"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

interface Location {
  id: string;
  name: string;
  category: string;
  address: string;
  primary_photo_url?: string;
  isOnline?: boolean;
}

interface LocationCatalogProps {
  onSelect: (location: Location | null) => void;
}

export function LocationCatalog({ onSelect }: LocationCatalogProps) {
  const [searchQuery, setSearchQuery] = React.useState("")
  const [locations, setLocations] = React.useState<Location[]>([])
  const [loading, setLoading] = React.useState(true)

  React.useEffect(() => {
    const fetchLocations = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/v1/locations")
        if (response.ok) {
          const data = await response.json()
          setLocations(data)
        }
      } catch (error) {
        console.error("Failed to fetch locations:", error)
      } finally {
        setLoading(false)
      }
    }
    fetchLocations()
  }, [])
  
  const getFullUrl = (url: string) => {
    if (!url) return '';
    if (url.startsWith('http') || url.startsWith('data:')) return url;
    return `http://localhost:8000${url}`;
  };

  const filteredLocations = locations.filter(loc => 
    loc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    loc.address.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent">
          Экраны в сети
        </h2>
        <div className="flex items-center gap-3">
          <Button 
            variant="outline" 
            className="gap-2 border-primary/50 text-primary hover:bg-primary/5 shadow-[0_0_15px_rgba(var(--primary),0.1)]"
            onClick={() => onSelect(null)}
          >
            <Camera className="h-4 w-4" />
            Street Upload
          </Button>
          <div className="relative w-full max-w-sm">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Поиск по названию или адресу..."
              className="pl-8 bg-zinc-900/50 border-white/5 focus-visible:ring-primary/50"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-72 rounded-2xl bg-zinc-900/50 animate-pulse border border-white/5" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filteredLocations.map((location) => (
            <Card key={location.id} className="group overflow-hidden border-white/5 bg-zinc-900/30 backdrop-blur-md transition-all duration-500 hover:border-primary/50 hover:bg-zinc-900/50 hover:shadow-2xl hover:shadow-primary/10">
              <div className="relative aspect-[16/10] bg-zinc-800">
                {location.primary_photo_url ? (
                  <img
                    src={location.primary_photo_url}
                    alt={location.name}
                    className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-110"
                  />
                ) : (
                  <div className="flex h-full w-full items-center justify-center text-zinc-700">
                    <ImageIcon className="h-12 w-12" />
                  </div>
                )}
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-60 transition-opacity group-hover:opacity-40" />
                <Badge 
                  variant={location.isOnline !== false ? "default" : "secondary"}
                  className="absolute right-3 top-3 gap-1 bg-black/60 backdrop-blur-xl border border-white/10"
                >
                  <div className={`h-1.5 w-1.5 rounded-full ${location.isOnline !== false ? 'bg-green-500 shadow-[0_0_8px_#22c55e]' : 'bg-red-500'}`} />
                  {location.isOnline !== false ? "Active" : "Offline"}
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
                  <MapPin className="h-3.5 w-3.5" />
                  <span className="line-clamp-1 font-medium italic">{location.address || "Адрес не указан"}</span>
                </div>
              </CardContent>
              <CardFooter className="p-4 pt-0">
                <Button 
                  onClick={() => onSelect(location)}
                  className="w-full gap-2 font-bold bg-white text-black hover:bg-primary hover:text-white transition-all duration-300 shadow-lg"
                >
                  <ImageIcon className="h-4 w-4" />
                  Создать мокап
                </Button>
              </CardFooter>
            </Card>
          ))}

          {filteredLocations.length === 0 && (
            <div className="col-span-full py-32 text-center border-2 border-dashed border-white/5 rounded-3xl bg-zinc-900/20">
              <div className="flex flex-col items-center gap-3">
                <div className="p-4 rounded-full bg-zinc-900/50 border border-white/5">
                  <ImageIcon className="h-8 w-8 text-zinc-700" />
                </div>
                <p className="text-zinc-500 font-medium">Локации не найдены. Попробуйте изменить запрос.</p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
