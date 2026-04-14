/**
 * Унифицированная утилита для работы с URL изображений.
 * Исключает дублирование getFullImageUrl в 3 компонентах.
 */
import { API_BASE_URL } from "@/lib/config";

/**
 * Преобразует относительный URL в абсолютный.
 * Если URL уже абсолютный (http/https/data) — возвращает как есть.
 */
export function getFullImageUrl(url: string | null | undefined): string {
  if (!url) return "";
  if (url.startsWith("http") || url.startsWith("data:") || url.startsWith("blob:")) {
    return url;
  }
  // Относительный путь — добавляем базовый URL backend
  return `${API_BASE_URL}${url.startsWith("/") ? "" : "/"}${url}`;
}

/**
 * Скачать файл по URL с заданным именем.
 * Использует fetch и Blob для преодоления проблемы кросс-доменного (CORS) открытия в новой вкладке.
 */
export async function downloadFile(url: string, filename: string): Promise<void> {
  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error("Network response was not ok");
    const blob = await response.blob();
    const objectUrl = window.URL.createObjectURL(blob);
    
    const a = document.createElement("a");
    a.href = objectUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(objectUrl);
  } catch (error) {
    console.error("Download failed, using fallback:", error);
    // Фолбэк, если CORS заблокировал fetch
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.target = "_blank";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }
}
