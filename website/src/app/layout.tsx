// SPDX-License-Identifier: Apache-2.0
import type { Metadata, Viewport } from "next";
import { Inter, Newsreader } from "next/font/google";
import { SiteHeader } from "@/components/site-header";
import { SiteFooter } from "@/components/site-footer";
import { MotionProvider } from "@/components/motion-provider";
import { site } from "@/content/site";
import "./globals.css";

const newsreader = Newsreader({
  variable: "--font-newsreader",
  subsets: ["latin"],
  axes: ["opsz"],
  style: ["normal", "italic"],
  display: "swap",
});

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  metadataBase: new URL(site.url),
  title: {
    default: `${site.name}: ${site.belief}`,
    template: `%s · ${site.name}`,
  },
  description: site.description,
  openGraph: {
    type: "website",
    siteName: site.name,
    title: `${site.name}: ${site.belief}`,
    description: site.description,
    images: [{ url: "/design/renders/10_on_open_hardcover.jpg", width: 1800, height: 1200, alt: "SenseBook clipped to an open hardcover book." }],
  },
};

export const viewport: Viewport = {
  themeColor: "#131a1b",
  colorScheme: "dark light",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${newsreader.variable} ${inter.variable} antialiased`}>
      <body className="flex min-h-dvh flex-col">
        <a
          href="#main"
          className="sr-only z-50 rounded-sm bg-marigold px-4 py-2 font-medium text-night focus:not-sr-only focus:fixed focus:top-4 focus:left-4"
        >
          Skip to content
        </a>
        <MotionProvider>
          <SiteHeader />
          <main id="main" className="flex-1">
            {children}
          </main>
          <SiteFooter />
        </MotionProvider>
      </body>
    </html>
  );
}
