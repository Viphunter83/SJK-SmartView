export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

export const API_ENDPOINTS = {
  HEALTH: `${API_BASE_URL}/api/v1/health`,
  LOCATIONS: `${API_BASE_URL}/api/v1/locations`,
  HISTORY: `${API_BASE_URL}/api/v1/history`,
  // Исправлено: было /api/v1/mockup/generate — теперь совпадает с backend роутом
  GENERATE_MOCKUP: `${API_BASE_URL}/api/v1/mockup/generate`,
  DETECT_CORNERS: `${API_BASE_URL}/api/v1/mockup/detect-corners`,
  DELETE_MOCKUP: (id: string) => `${API_BASE_URL}/api/v1/history/${id}`,
};
