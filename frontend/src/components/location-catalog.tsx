"use client"

import * as React from "react"
import { Search, MapPin, Monitor, Layers, Image as ImageIcon } from "lucide-react"

import { Input } from "@/components/ui/input"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { mockLocations, Location } from "@/lib/mock-data"
import { MockupCreator } from "@/components/mockup-creator"

export function LocationCatalog() {
  const [searchQuery, setSearchQuery] = React.useState("")
  const [selectedLocation, setSelectedLocation] = React.useState<Location | null>(null)
  const [isModalOpen, setIsModalOpen] = React.useState(false)
  
  const filteredLocations = mockLocations.filter(loc => 
    loc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    loc.address.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleCreateMockup = (location: Location) => {
    setSelectedLocation(location)
    setIsModalOpen(true)
  }

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex items-center justify-between gap-4">
        <h1 className="text-3xl font-bold tracking-tight">Каталог экранов</h1>
        <div className="relative w-full max-w-sm">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            type="search"
            placeholder="Поиск по названию или адресу..."
            className="pl-8"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {filteredLocations.map((location) => (
          <Card key={location.id} className="overflow-hidden border-border/40 bg-card/50 backdrop-blur-sm transition-all hover:border-primary/50">
            <div className="relative aspect-video">
              <img
                src={location.image}
                alt={location.name}
                className="h-full w-full object-cover transition-transform duration-300 hover:scale-105"
              />
              <Badge 
                variant={location.isOnline ? "default" : "secondary"}
                className="absolute right-2 top-2 gap-1 bg-background/80 backdrop-blur-md"
              >
                <div className={`h-2 w-2 rounded-full ${location.isOnline ? 'bg-green-500' : 'bg-red-500'}`} />
                {location.isOnline ? "Active" : "Offline"}
              </Badge>
            </div>
            <CardHeader className="p-4">
              <div className="flex items-center justify-between">
                <Badge variant="outline" className="text-[10px] uppercase tracking-wider">
                  {location.category}
                </Badge>
              </div>
              <CardTitle className="line-clamp-1 text-lg">{location.name}</CardTitle>
            </CardHeader>
            <CardContent className="px-4 pb-4 pt-0 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <MapPin className="h-3 w-3" />
                <span className="line-clamp-1">{location.address}</span>
              </div>
            </CardContent>
            <CardFooter className="p-4 pt-0">
              <Button 
                onClick={() => handleCreateMockup(location)}
                className="w-full gap-2 font-semibold shadow-lg shadow-primary/20"
              >
                <ImageIcon className="h-4 w-4" />
                Создать мокап
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>

      <MockupCreator 
        location={selectedLocation} 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
      />
    </div>
  )
}
