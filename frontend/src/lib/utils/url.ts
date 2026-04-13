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
 */
export function downloadFile(url: string, filename: string): void {
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.target = "_blank";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}
