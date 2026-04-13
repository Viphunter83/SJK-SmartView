/**
 * Canvas-based perspective renderer для AI мокапов.
 * Работает полностью в браузере без GPU/Modal.
 * Поддерживает автоматический CORS-прокси для внешних изображений.
 */

export interface Point {
  x: number;
  y: number;
}

export interface RenderOptions {
  opacity?: number;       // 0–1, прозрачность наложения
  blendMode?: string;     // CSS blend mode
  quality?: number;       // JPEG quality 0–1
}

// ─────────────────────────────────────────────────────────────
// CORS Image Proxy
// ─────────────────────────────────────────────────────────────

/**
 * Проксируем внешние URL через Next.js API /api/image-proxy.
 * Локальные URL (blob:, data:, /) — напрямую.
 */
function toProxiedUrl(src: string): string {
  if (
    src.startsWith("blob:") ||
    src.startsWith("data:") ||
    src.startsWith("/") ||
    src.startsWith("http://localhost") ||
    src.startsWith("http://127.0.0.1")
  ) {
    return src;
  }
  return `/api/image-proxy?url=${encodeURIComponent(src)}`;
}

/**
 * Загружает изображение с автоматическим fallback на CORS-прокси.
 * При любой ошибке выдаёт понятное сообщение вместо "[object Event]".
 */
function loadImage(src: string): Promise<HTMLImageElement> {
  const proxiedSrc = toProxiedUrl(src);
  const needsProxy = proxiedSrc !== src;

  return new Promise((resolve, reject) => {
    const attempt = (url: string, isFallback: boolean) => {
      const img = new Image();
      // crossOrigin нужен только когда грузим напрямую (не через прокси),
      // иначе браузер добавляет CORS preflight к уже проксированному запросу
      if (!isFallback && !needsProxy) {
        img.crossOrigin = "anonymous";
      }
      img.onload = () => resolve(img);
      img.onerror = () => {
        if (!isFallback) {
          // Первая попытка провалилась → пробуем через прокси
          attempt(`/api/image-proxy?url=${encodeURIComponent(src)}`, true);
        } else {
          reject(
            new Error(
              `Не удалось загрузить изображение (CORS или недоступен сервер):\n${src.substring(0, 100)}`
            )
          );
        }
      };
      img.src = url;
    };

    // Сразу идём через прокси если URL внешний
    attempt(needsProxy ? proxiedSrc : src, needsProxy);
  });
}

// ─────────────────────────────────────────────────────────────
// Perspective Math
// ─────────────────────────────────────────────────────────────

/**
 * Вычисляет матрицу гомографии (perspective transform) из 4 точек.
 */
function getPerspectiveTransform(
  src: [number, number][],
  dst: [number, number][]
): number[] {
  const A: number[][] = [];
  for (let i = 0; i < 4; i++) {
    const [sx, sy] = src[i];
    const [dx, dy] = dst[i];
    A.push([-sx, -sy, -1, 0, 0, 0, dx * sx, dx * sy, dx]);
    A.push([0, 0, 0, -sx, -sy, -1, dy * sx, dy * sy, dy]);
  }

  const n = 8;
  const aug = A.map((row) => [...row]);

  for (let col = 0; col < n; col++) {
    let maxRow = col;
    for (let row = col + 1; row < 2 * n; row++) {
      if (Math.abs(aug[row][col]) > Math.abs(aug[maxRow][col])) {
        maxRow = row;
      }
    }
    [aug[col], aug[maxRow]] = [aug[maxRow], aug[col]];
    for (let row = col + 1; row < 2 * n; row++) {
      const factor = aug[row][col] / aug[col][col];
      for (let k = col; k <= n; k++) {
        aug[row][k] -= factor * aug[col][k];
      }
    }
  }

  const h = new Array(n).fill(0);
  for (let i = n - 1; i >= 0; i--) {
    h[i] = aug[i][n] / aug[i][i];
    for (let j = i - 1; j >= 0; j--) {
      aug[j][n] -= aug[j][i] * h[i];
    }
  }

  return [...h, 1];
}

// ─────────────────────────────────────────────────────────────
// Canvas Drawing
// ─────────────────────────────────────────────────────────────

/**
 * Применяет perspective warp к image и рисует на canvas через mesh triangulation.
 */
async function warpImage(
  sourceImg: HTMLImageElement,
  canvas: HTMLCanvasElement,
  corners: Point[],
  options: RenderOptions = {}
): Promise<void> {
  const { opacity = 1.0 } = options;

  if (corners.length !== 4) {
    throw new Error("warpImage requires exactly 4 corner points");
  }

  const ctx = canvas.getContext("2d");
  if (!ctx) throw new Error("Canvas 2D context unavailable");

  drawPerspectiveWarp(ctx, sourceImg, corners, opacity);
}

/**
 * Рисует перспективно трансформированное изображение через mesh triangulation (20×20).
 */
function drawPerspectiveWarp(
  ctx: CanvasRenderingContext2D,
  img: HTMLImageElement,
  corners: Point[],
  opacity: number
): void {
  const DIVISIONS = 20;
  const sw = img.naturalWidth;
  const sh = img.naturalHeight;

  ctx.globalAlpha = opacity;
  ctx.imageSmoothingEnabled = true;
  ctx.imageSmoothingQuality = "high";

  const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

  const getPoint = (u: number, v: number): Point => {
    const x = lerp(
      lerp(corners[0].x, corners[1].x, u),
      lerp(corners[3].x, corners[2].x, u),
      v
    );
    const y = lerp(
      lerp(corners[0].y, corners[1].y, u),
      lerp(corners[3].y, corners[2].y, u),
      v
    );
    return { x, y };
  };

  for (let row = 0; row < DIVISIONS; row++) {
    for (let col = 0; col < DIVISIONS; col++) {
      const u0 = col / DIVISIONS;
      const u1 = (col + 1) / DIVISIONS;
      const v0 = row / DIVISIONS;
      const v1 = (row + 1) / DIVISIONS;

      const p00 = getPoint(u0, v0);
      const p10 = getPoint(u1, v0);
      const p01 = getPoint(u0, v1);
      const p11 = getPoint(u1, v1);

      const sx0 = u0 * sw;
      const sx1 = u1 * sw;
      const sy0 = v0 * sh;
      const sy1 = v1 * sh;

      drawTriangle(ctx, img,
        p00, p10, p01,
        { x: sx0, y: sy0 }, { x: sx1, y: sy0 }, { x: sx0, y: sy1 }
      );
      drawTriangle(ctx, img,
        p10, p11, p01,
        { x: sx1, y: sy0 }, { x: sx1, y: sy1 }, { x: sx0, y: sy1 }
      );
    }
  }

  ctx.globalAlpha = 1.0;
}

/**
 * Рисует один текстурированный треугольник.
 */
function drawTriangle(
  ctx: CanvasRenderingContext2D,
  img: HTMLImageElement,
  p0: Point, p1: Point, p2: Point,
  t0: Point, t1: Point, t2: Point
): void {
  ctx.save();
  ctx.beginPath();
  ctx.moveTo(p0.x, p0.y);
  ctx.lineTo(p1.x, p1.y);
  ctx.lineTo(p2.x, p2.y);
  ctx.closePath();
  ctx.clip();

  const det = (t1.x - t0.x) * (t2.y - t0.y) - (t2.x - t0.x) * (t1.y - t0.y);
  if (Math.abs(det) < 1e-10) {
    ctx.restore();
    return;
  }

  const a = ((p1.x - p0.x) * (t2.y - t0.y) - (p2.x - p0.x) * (t1.y - t0.y)) / det;
  const b = ((p2.x - p0.x) * (t1.x - t0.x) - (p1.x - p0.x) * (t2.x - t0.x)) / det;
  const c = p0.x - a * t0.x - b * t0.y;
  const d = ((p1.y - p0.y) * (t2.y - t0.y) - (p2.y - p0.y) * (t1.y - t0.y)) / det;
  const e = ((p2.y - p0.y) * (t1.x - t0.x) - (p1.y - p0.y) * (t2.x - t0.x)) / det;
  const f = p0.y - d * t0.x - e * t0.y;

  ctx.transform(a, d, b, e, c, f);
  ctx.drawImage(img, 0, 0);
  ctx.restore();
}

// ─────────────────────────────────────────────────────────────
// Public API
// ─────────────────────────────────────────────────────────────

/**
 * Основная функция: генерирует мокап и возвращает Data URL.
 *
 * @param backgroundSrc - URL фонового изображения (поддерживает внешние URL — автопрокси)
 * @param creativeSrc - URL или blob-URL креатива (баннер)
 * @param corners - 4 угла экрана на фоне
 * @param options - настройки рендеринга
 * @returns Promise<string> - data:image/jpeg;base64,...
 */
export async function renderMockup(
  backgroundSrc: string,
  creativeSrc: string,
  corners: Point[],
  options: RenderOptions = {}
): Promise<string> {
  const { quality = 0.92 } = options;

  const [bgImg, crImg] = await Promise.all([
    loadImage(backgroundSrc),
    loadImage(creativeSrc),
  ]);

  const canvas = document.createElement("canvas");
  canvas.width = bgImg.naturalWidth;
  canvas.height = bgImg.naturalHeight;
  const ctx = canvas.getContext("2d")!;

  // 1. Рисуем фон
  ctx.drawImage(bgImg, 0, 0);

  // 2. Накладываем креатив с perspective warp
  await warpImage(crImg, canvas, corners, options);

  // 3. Лёгкая виньетка для реализма
  const gradient = ctx.createRadialGradient(
    canvas.width / 2, canvas.height / 2, canvas.width * 0.3,
    canvas.width / 2, canvas.height / 2, canvas.width * 0.7
  );
  gradient.addColorStop(0, "rgba(0,0,0,0)");
  gradient.addColorStop(1, "rgba(0,0,0,0.15)");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  return canvas.toDataURL("image/jpeg", quality);
}

/**
 * Создаёт Blob из Data URL для загрузки в Firebase Storage.
 */
export function dataUrlToBlob(dataUrl: string): Blob {
  const [header, data] = dataUrl.split(",");
  const mime = header.match(/:(.*?);/)![1];
  const binary = atob(data);
  const arr = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    arr[i] = binary.charCodeAt(i);
  }
  return new Blob([arr], { type: mime });
}
