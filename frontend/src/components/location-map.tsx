"use client"

import React, { useEffect, useState, useCallback } from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { API_ENDPOINTS } from "@/lib/config"
import { getFullImageUrl } from "@/lib/utils/url"
import { MapPin, Navigation, Eye, Loader2, AlertCircle, RefreshCw } from "lucide-react"
import { Button } from '@/components/ui/button'

// Fix for default Leaflet marker icons in Next.js
const DefaultIcon = L.icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
})
L.Marker.prototype.options.icon = DefaultIcon

interface Location {
  id: string;
  name: string;
  category: string;
  address: string;
  coords_lat: number;
  coords_lng: number;
  primary_photo_url: string;
  is_active?: boolean;
}

interface LocationMapProps {
  onSelect?: (location: Location) => void;
}

export default function LocationMap({ onSelect }: LocationMapProps) {
  const [locations, setLocations] = useState<Location[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const center: [number, number] = [10.77, 106.7] // Ho Chi Minh City center

  const fetchLocations = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(API_ENDPOINTS.LOCATIONS)
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const data = await res.json()
      // Фильтруем только локации с координатами
      setLocations(data.filter((loc: Location) => loc.coords_lat && loc.coords_lng))
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка загрузки карты")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchLocations()
  }, [fetchLocations])

  if (loading) {
    return (
      <div className="h-[calc(100vh-12rem)] w-full rounded-3xl border border-white/5 bg-zinc-950 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4 text-zinc-500">
          <Loader2 className="h-10 w-10 animate-spin text-primary" />
          <p className="font-medium">Загрузка карты...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-[calc(100vh-12rem)] w-full rounded-3xl border border-red-500/20 bg-red-500/5 flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <AlertCircle className="h-10 w-10 text-red-400" />
          <p className="font-bold text-red-400">Карта недоступна</p>
          <p className="text-xs text-zinc-500">{error}</p>
          <Button variant="outline" onClick={fetchLocations} className="gap-2 border-red-500/30 text-red-400">
            <RefreshCw className="h-4 w-4" />
            Повторить
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="h-[calc(100vh-12rem)] w-full rounded-3xl overflow-hidden border border-white/5 relative bg-zinc-950">
      <MapContainer
        center={center}
        zoom={11}
        className="h-full w-full"
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {locations.map((loc) => (
          <Marker key={loc.id} position={[loc.coords_lat, loc.coords_lng]}>
            <Popup className="custom-popup">
              <Card className="border-0 bg-zinc-900 text-white w-64 overflow-hidden">
                <div className="h-32 w-full relative">
                  <img
                    src={getFullImageUrl(loc.primary_photo_url)}
                    alt={loc.name}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src =
                        'https://images.unsplash.com/photo-1542281286-9e0a16bb7366?auto=format&fit=crop&q=80&w=400'
                    }}
                  />
                  <Badge className="absolute top-2 left-2 bg-black/60 backdrop-blur-md border-white/10">
                    {loc.category}
                  </Badge>
                  <div className={`absolute top-2 right-2 h-2 w-2 rounded-full ${
                    loc.is_active !== false ? 'bg-green-500 shadow-[0_0_8px_#22c55e]' : 'bg-red-500'
                  }`} />
                </div>
                <CardContent className="p-3">
                  <h3 className="font-bold text-base mb-1">{loc.name}</h3>
                  <div className="flex items-center gap-2 text-xs text-zinc-400 mb-3">
                    <MapPin className="w-3 h-3 shrink-0" />
                    <span className="truncate">{loc.address}</span>
                  </div>
                  <div className="flex gap-2">
                    {onSelect && (
                      <button
                        className="flex-1 py-2 bg-white text-black text-xs font-bold rounded-lg flex items-center justify-center gap-1 hover:bg-white/90 transition-colors"
                        onClick={() => onSelect(loc)}
                      >
                        <Eye className="w-3 h-3" />
                        Создать мокап
                      </button>
                    )}
                    <a
                      href={`https://www.google.com/maps/search/?api=1&query=${loc.coords_lat},${loc.coords_lng}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="w-10 h-8 bg-zinc-800 rounded-lg flex items-center justify-center hover:bg-zinc-700 transition-colors"
                      title="Открыть в Google Maps"
                    >
                      <Navigation className="w-3 h-3" />
                    </a>
                  </div>
                </CardContent>
              </Card>
            </Popup>
          </Marker>
        ))}
      </MapContainer>

      {/* Map Overlay Info */}
      <div className="absolute top-4 right-4 z-[1000] flex flex-col gap-2">
        <Badge className="bg-zinc-900/80 backdrop-blur-xl border-white/10 px-4 py-2 text-sm shadow-2xl">
          {locations.length} объектов SJK по Вьетнаму
        </Badge>
      </div>
    </div>
  )
}
