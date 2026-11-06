import type { Metadata } from 'next'

import { CaseList } from '@/components/CaseList'
import { SERIES, STAGE } from '@/lib/site'

export const metadata: Metadata = { title: 'Chapters' }

export default function Workshop() {
  return (
    <div className="mx-auto flex max-w-6xl flex-col gap-10 px-4 pt-12 pb-20">
      <header className="flex max-w-3xl flex-col gap-3">
        <span className="eyebrow">
          {SERIES} · stage {STAGE}
        </span>
        <h1 className="text-[40px] leading-tight font-bold tracking-[-0.025em]">The chapters</h1>
        <p className="text-[18px] leading-relaxed text-ink-2">
          One chapter per lab case, in order. Run each case with{' '}
          <code className="font-mono text-[15px]">uv run python -m trust run N</code> and check your
          fix with <code className="font-mono text-[15px]">check N</code>.
        </p>
      </header>
      <CaseList />
    </div>
  )
}
