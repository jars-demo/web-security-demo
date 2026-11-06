import Link from 'next/link'

import { BackToTop } from '@/components/BackToTop'
import { REPO_URL, SERIES, STAGE, TITLE } from '@/lib/site'

function Mark() {
  return (
    <svg viewBox="0 0 24 24" className="size-6 shrink-0" aria-hidden="true">
      <rect x="2" y="2" width="20" height="20" rx="5" fill="#4f46e5" />
      <path
        d="M12 6l5 2v3.2c0 3-2.1 5.1-5 6.2-2.9-1.1-5-3.2-5-6.2V8l5-2z"
        fill="none"
        stroke="#ffffff"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
    </svg>
  )
}

export function Shell({ children }: { children: React.ReactNode }) {
  return (
    <>
      <header className="on-slate sticky top-0 z-40 bg-slate text-on-slate">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between gap-4 px-4">
          <Link href="/" className="flex min-w-0 items-center gap-2.5">
            <Mark />
            <span className="truncate text-[15px] font-semibold">{TITLE}</span>
            <span className="hidden font-mono text-[12px] text-on-slate-muted sm:inline">
              {SERIES}, stage {STAGE}
            </span>
          </Link>
          <nav aria-label="Main" className="flex shrink-0 items-center gap-1 text-[14.5px]">
            <Link
              href="/workshop"
              className="inline-flex h-10 items-center rounded-md px-3 text-on-slate-muted hover:bg-slate-2 hover:text-on-slate"
            >
              Chapters
            </Link>
            <a
              href={REPO_URL}
              className="inline-flex h-10 items-center rounded-md px-3 text-on-slate-muted hover:bg-slate-2 hover:text-on-slate"
            >
              GitHub
            </a>
          </nav>
        </div>
      </header>
      <main id="main" className="flex-1">
        {children}
      </main>
      <footer className="border-t border-rule pb-20">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 px-4 py-8 text-[14px] text-muted sm:flex-row sm:justify-between">
          <p>
            {TITLE}. {SERIES}, stage {STAGE}. Every lab runs on your own machine, on 127.0.0.1.
          </p>
          <p>MIT licensed.</p>
        </div>
      </footer>
      <div className="fixed right-[max(1rem,env(safe-area-inset-right))] bottom-[max(1rem,env(safe-area-inset-bottom))] z-30">
        <BackToTop />
      </div>
    </>
  )
}
