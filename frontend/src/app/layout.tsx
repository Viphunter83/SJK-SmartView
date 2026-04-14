import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthProvider } from "@/lib/auth-context";
import { LanguageProvider } from "@/lib/i18n";

const inter = Inter({ subsets: ["latin", "cyrillic"] });

export const metadata: Metadata = {
  title: "SJK SmartView - Premium AI DOOH Mockup Studio",
  description: "AI-powered visualization tool for Shojiki Group advertising sales teams. Photorealistic digital billboard mockups in seconds.",
  manifest: "/manifest.json",
  openGraph: {
    title: "SJK SmartView | AI Mockup Studio",
    description: "Professional DOOH visualization for Shojiki Group Vietnam",
    url: "https://sjk-smart-view.vercel.app",
    siteName: "SJK SmartView",
    locale: "vi_VN",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "SJK SmartView | AI Mockup Studio",
    description: "Professional DOOH visualization for Shojiki Group Vietnam",
  },
  icons: {
    icon: "/favicon.png",
    apple: "/icon-192.png",
  },
};

export const viewport: Viewport = {
  themeColor: "#000000",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="vi" className="dark h-full antialiased">
      <body className={`${inter.className} min-h-full bg-background`}>
        <AuthProvider>
          <LanguageProvider>
            <TooltipProvider>
              {children}
            </TooltipProvider>
          </LanguageProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
