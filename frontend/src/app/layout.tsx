import type { Metadata, Viewport } from 'next'
import { JetBrains_Mono, Public_Sans } from 'next/font/google'

import { Shell } from '@/components/Shell'
import { SITE_URL, TAGLINE, TITLE } from '@/lib/site'

import './globals.css'

const sans = Public_Sans({ variable: '--font-public-sans', subsets: ['latin'] })
const mono = JetBrains_Mono({ variable: '--font-jetbrains-mono', subsets: ['latin'] })

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: TITLE, template: `%s · ${TITLE}` },
  description: TAGLINE,
  openGraph: { title: TITLE, description: TAGLINE, url: SITE_URL, type: 'website' },
  twitter: { card: 'summary_large_image', title: TITLE, description: TAGLINE },
}

export const viewport: Viewport = {
  themeColor: '#0d1321',
  width: 'device-width',
  initialScale: 1,
  viewportFit: 'cover',
}

export default function RootLayout({ children }: LayoutProps<'/'>) {
  return (
    <html lang="en" className={`${sans.variable} ${mono.variable} h-full antialiased`}>
      <body className="flex min-h-full flex-col">
        <a
          href="#main"
          className="sr-only rounded bg-slate px-4 py-2 text-on-slate focus:not-sr-only focus:fixed focus:top-3 focus:left-3 focus:z-50"
        >
          Skip to content
        </a>
        <Shell>{children}</Shell>
      </body>
    </html>
  )
}
