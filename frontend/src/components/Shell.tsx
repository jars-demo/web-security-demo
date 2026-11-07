import Link from 'next/link'

import { BackToTop } from '@/components/BackToTop'
import { PREV_REPO_URL, REPO_URL, SERIES, STAGE, TITLE } from '@/lib/site'

function Mark() {
  return (
    <svg viewBox="0 0 64 64" className="size-7 shrink-0" aria-hidden="true">
      <rect
        x="1"
        y="1"
        width="62"
        height="62"
        rx="14"
        fill="#1a2233"
        stroke="#344054"
        strokeWidth="2"
      />
      <path
        d="M18 20 30 32 18 44"
        fill="none"
        stroke="#f2f4f7"
        strokeWidth="6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path d="M43 16v32" fill="none" stroke="#a5b4fc" strokeWidth="6" strokeLinecap="round" />
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
            {TITLE}. {SERIES}, stage {STAGE}, after{' '}
            <a href={PREV_REPO_URL} className="underline underline-offset-2 hover:text-ink">
              How systems talk
            </a>
            . Every lab runs on your own machine, on 127.0.0.1.
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
