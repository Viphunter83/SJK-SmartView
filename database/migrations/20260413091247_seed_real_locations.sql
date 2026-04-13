-- Seed real Shojiki locations in Vietnam
-- Data based on public inventory from shojiki.vn

INSERT INTO locations (id, name, category, description, address, coords_lat, coords_lng, aspect_ratio, screen_geometry)
VALUES 
(
    '00000000-0000-0000-0000-000000000001',
    'Terra Royal LED Screen',
    'Outdoor LED',
    'High-traffic intersection of Nam Ky Khoi Nghia and Ly Chinh Thang.',
    '278 Nam Ky Khoi Nghia, District 3, HCMC',
    10.7877, 106.6853,
    1.77,
    '{"corners": [[465, 175], [895, 315], [895, 625], [465, 545]]}'
),
(
    '00000000-0000-0000-0000-000000000002',
    'AB Tower LED',
    'Outdoor LED',
    'Prime location near New World Hotel and Le Lai park.',
    '76 Le Lai, District 1, HCMC',
    10.7712, 106.6948,
    1.77,
    '{"corners": [[200, 100], [800, 100], [800, 400], [200, 400]]}'
),
(
    '00000000-0000-0000-0000-000000000003',
    'Nguyen Hue 3D LED (Lucky Plaza)',
    '3D LED',
    'The iconic 3D L-shaped screen on the pedestrian street.',
    '38 Nguyen Hue, District 1, HCMC',
    10.7745, 106.7032,
    2.56,
    '{"corners": [[100, 50], [900, 50], [900, 450], [100, 450]]}'
),
(
    '00000000-0000-0000-0000-000000000004',
    'Vincom Center Dong Khoi',
    'Indoor LCD',
    'Digital standee network inside the mall.',
    '72 Le Thanh Ton, District 1, HCMC',
    10.7781, 106.7018,
    0.56,
    '{"corners": [[300, 50], [700, 50], [700, 950], [300, 950]]}'
),
(
    '00000000-0000-0000-0000-000000000005',
    'Diamond Island Entrance',
    'Billboard',
    'Static billboard near the bridge to Diamond Island.',
    'Quan 2, Thu Duc City, HCMC',
    10.7628, 106.7554,
    1.77,
    '{"corners": [[0, 0], [1000, 0], [1000, 500], [0, 500]]}'
)
ON CONFLICT (id) DO NOTHING;
