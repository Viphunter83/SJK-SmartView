export interface Location {
  id: string;
  name: string;
  category: 'Outdoor LED' | '3D LED' | 'Billboard' | 'Indoor LCD';
  address: string;
  image: string;
  isOnline: boolean;
}

export const mockLocations: Location[] = [
  {
    id: '1',
    name: 'Terra Royal LED',
    category: 'Outdoor LED',
    address: 'Quận 3, TP.HCM',
    image: 'https://images.unsplash.com/photo-1542310503-9935137000c0?auto=format&fit=crop&q=80&w=800',
    isOnline: true,
  },
  {
    id: '2',
    name: 'Nguyen Hue 3D LED',
    category: '3D LED',
    address: 'Phố đi bộ Nguyễn Huệ, Quận 1',
    image: 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&q=80&w=800',
    isOnline: true,
  },
  {
    id: '3',
    name: 'Lotte Center Billboard',
    category: 'Billboard',
    address: '54 Liễu Giai, Ba Đình, Hà Nội',
    image: 'https://images.unsplash.com/photo-1563911302283-d2bc129e7570?auto=format&fit=crop&q=80&w=800',
    isOnline: false,
  },
  {
    id: '4',
    name: 'Vincom Dong Khoi LCD',
    category: 'Indoor LCD',
    address: '72 Lê Thánh Tôn, Quận 1',
    image: 'https://images.unsplash.com/photo-1555529669-e69e7aa0ba9a?auto=format&fit=crop&q=80&w=800',
    isOnline: true,
  },
];
