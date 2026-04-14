export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";
export const SJK_API_KEY = process.env.NEXT_PUBLIC_SJK_KEY || "e30575eb-cf4e-4304-a008-a9f3cc91cab2";

export const API_ENDPOINTS = {
  HEALTH: `${API_BASE_URL}/api/v1/health`,
  LOCATIONS: `${API_BASE_URL}/api/v1/locations`,
  HISTORY: `${API_BASE_URL}/api/v1/history`,
  // Исправлено: было /api/v1/mockup/generate — теперь совпадает с backend роутом
  GENERATE_MOCKUP: `${API_BASE_URL}/api/v1/mockup/generate`,
  DETECT_CORNERS: `${API_BASE_URL}/api/v1/mockup/detect-corners`,
  DELETE_MOCKUP: (id: string) => `${API_BASE_URL}/api/v1/history/${id}`,
};

