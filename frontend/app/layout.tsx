import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AreaYield OS - 民泊投資判定プラットフォーム',
  description: '短期賃貸（民泊）投資の可否判定を、収益性・許認可実現性・規制リスクの3軸で評価',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body className={inter.className}>
        <div className="min-h-screen bg-background">
          <header className="border-b">
            <div className="container mx-auto px-4 py-4">
              <h1 className="text-2xl font-bold">AreaYield OS</h1>
            </div>
          </header>
          <main className="container mx-auto px-4 py-8">
            {children}
          </main>
          <footer className="border-t mt-auto">
            <div className="container mx-auto px-4 py-6">
              <p className="text-center text-sm text-muted-foreground">
                © 2025 AreaYield. All rights reserved.
              </p>
            </div>
          </footer>
        </div>
      </body>
    </html>
  )
}

