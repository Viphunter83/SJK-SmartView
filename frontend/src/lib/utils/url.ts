import { API_BASE_URL, API_ENDPOINTS } from "@/lib/config";

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
 * Скачать или поделиться файлом.
 * Использует fetch+Blob для скачивания или Web Share API для мобильных устройств.
 */
export async function downloadFile(url: string, filename: string): Promise<void> {
  // 1. Попытка использовать Share API (лучший опыт для мобильных)
  if (typeof navigator !== 'undefined' && navigator.share && navigator.canShare) {
    try {
      const response = await fetch(url);
      const blob = await response.blob();
      const file = new File([blob], filename, { type: blob.type });
      
      if (navigator.canShare({ files: [file] })) {
        await navigator.share({
          files: [file],
          title: filename,
        });
        return; // Успешно поделились
      }
    } catch (e) {
      console.warn("Share API failed, falling back to download:", e);
    }
  }

  // 2. Стандартный метод через Blob (для десктопа)
  try {
    let objectUrl: string;
    
    if (url.startsWith("data:")) {
      objectUrl = url;
    } else {
      const response = await fetch(url);
      if (!response.ok) throw new Error("Network response was not ok");
      const blob = await response.blob();
      objectUrl = window.URL.createObjectURL(blob);
    }
    
    const a = document.createElement("a");
    a.href = objectUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    if (!url.startsWith("data:")) {
      window.URL.revokeObjectURL(objectUrl);
    }
  } catch (error) {
    console.error("Download failed, using PROXY fallback:", error);
    
    // 3. Последний надежный способ: прокси через наш бэкенд
    // Это гарантирует принудительную загрузку даже на iOS/Android Chrome
    if (url.startsWith("http")) {
      const proxyUrl = API_ENDPOINTS.DOWNLOAD_PROXY(url);
      const a = document.createElement("a");
      a.href = proxyUrl;
      // Мы не ставим target="_blank" здесь, чтобы не открывать пустую вкладку, 
      // так как сервер вернет Content-Disposition: attachment
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    } else {
      // Совсем крайний случай (почти невозможен для http)
      const a = document.createElement("a");
      a.href = url;
      a.target = "_blank";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    }
  }
}

