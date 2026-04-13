import { NextRequest, NextResponse } from "next/server";

/**
 * Proxy endpoint для загрузки внешних изображений в Canvas.
 * Решает CORS-проблему: браузер не может загружать cross-origin img в canvas,
 * но Next.js server-side может — и отдаёт как локальный ресурс.
 *
 * Usage: /api/image-proxy?url=https://example.com/photo.jpg
 */
export async function GET(request: NextRequest) {
  const url = request.nextUrl.searchParams.get("url");

  if (!url) {
    return NextResponse.json({ error: "Missing url parameter" }, { status: 400 });
  }

  // Базовая валидация — разрешаем только http/https
  let parsedUrl: URL;
  try {
    parsedUrl = new URL(url);
    if (!["http:", "https:"].includes(parsedUrl.protocol)) {
      return NextResponse.json({ error: "Invalid URL protocol" }, { status: 400 });
    }
  } catch {
    return NextResponse.json({ error: "Invalid URL" }, { status: 400 });
  }

  try {
    const response = await fetch(parsedUrl.toString(), {
      headers: {
        // Представляемся как браузер, чтобы не получить 403
        "User-Agent":
          "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        Accept: "image/webp,image/apng,image/*,*/*;q=0.8",
      },
      // Таймаут 10 секунд
      signal: AbortSignal.timeout(10_000),
    });

    if (!response.ok) {
      return NextResponse.json(
        { error: `Upstream returned ${response.status}` },
        { status: response.status }
      );
    }

    const contentType = response.headers.get("content-type") || "image/jpeg";
    const buffer = await response.arrayBuffer();

    return new NextResponse(buffer, {
      status: 200,
      headers: {
        "Content-Type": contentType,
        // Кэшируем на 1 час в браузере
        "Cache-Control": "public, max-age=3600, s-maxage=3600",
        // Разрешаем Canvas использование
        "Access-Control-Allow-Origin": "*",
        "Cross-Origin-Resource-Policy": "cross-origin",
      },
    });
  } catch (error) {
    const msg = error instanceof Error ? error.message : "Fetch failed";
    console.error("[image-proxy] error:", msg, "url:", url);
    return NextResponse.json({ error: msg }, { status: 502 });
  }
}
