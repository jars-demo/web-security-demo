import Link from 'next/link'

import { CaseList } from '@/components/CaseList'
import { CopyButton } from '@/components/CopyButton'
import { InjectionSim } from '@/components/InjectionSim'
import {
  MEASURED,
  PREV_REPO_URL,
  QUICKSTART,
  REPO_URL,
  SERIES,
  STAGE,
  STAGES,
  TAGLINE,
  TITLE,
} from '@/lib/site'
import { CHAPTERS } from '@/lib/workshop'

export default function Home() {
  const minutes = CHAPTERS.reduce((sum, chapter) => sum + chapter.minutes, 0)
  return (
    <>
      <section className="on-slate overflow-hidden bg-slate text-on-slate">
        <div className="mx-auto flex max-w-6xl flex-col gap-10 px-4 pt-12 pb-14 sm:pt-16">
          <div className="flex min-w-0 flex-col gap-5">
            <span className="eyebrow">
              {SERIES} · stage {STAGE} of 2
              {minutes ? ` · ${CHAPTERS.length} chapters · ${minutes} minutes` : ''}
            </span>
            <h1 className="max-w-3xl text-[44px] leading-[1.02] font-extrabold tracking-[-0.035em] sm:text-[64px]">
              {TITLE}
            </h1>
            <p className="max-w-2xl text-[18px] leading-relaxed text-on-slate-muted">{TAGLINE}</p>
            <div className="flex flex-wrap gap-3">
              <Link
                href={CHAPTERS[0] ? `/workshop/${CHAPTERS[0].slug}` : '/workshop'}
                className="inline-flex h-12 items-center rounded-md bg-accent px-5 text-[16px] font-semibold text-on-accent hover:opacity-90"
              >
                Start chapter 01
              </Link>
              <a
                href={REPO_URL}
                className="inline-flex h-12 items-center rounded-md border border-on-slate-muted/40 px-5 text-[16px] font-semibold text-on-slate hover:bg-slate-2"
              >
                Get the lab on GitHub
              </a>
            </div>
            <p className="text-[14px] text-on-slate-muted">
              New here? Stage 1,{' '}
              <a href={PREV_REPO_URL} className="text-accent-glow underline underline-offset-2">
                How systems talk
              </a>
              , covers DNS, TLS, cookies and sessions. This stage is the application on top.
            </p>
          </div>

          <div className="rounded-2xl border border-[#2b3650] bg-[#111a2b] p-3 sm:p-5">
            <div className="mb-2 flex flex-wrap items-baseline justify-between gap-2 px-1">
              <span className="font-mono text-[12px] tracking-[0.08em] text-accent-glow uppercase">
                POST /login
              </span>
              <span className="text-[13px] text-on-slate-muted">
                one input, two readings: data or code
              </span>
            </div>
            <InjectionSim />
          </div>
        </div>
      </section>

      <section aria-labelledby="cases" className="mx-auto max-w-6xl px-4 py-14">
        <div className="mb-8 flex max-w-3xl flex-col gap-3">
          <span className="eyebrow">The lab</span>
          <h2 id="cases" className="text-[32px] leading-tight font-bold tracking-[-0.02em]">
            Ten cases, one per chapter
          </h2>
          <p className="text-[17px] leading-relaxed text-ink-2">
            Each case is one small service with one deliberate weakness, an attack that runs only on
            127.0.0.1, a fix you write, and a check that rejects the lazy non-fix. Grouped from the
            foundations to what senior engineers still get wrong.
          </p>
        </div>
        <CaseList />
      </section>

      <section aria-labelledby="measured" className="border-y border-rule bg-surface">
        <div className="mx-auto flex max-w-6xl flex-col gap-8 px-4 py-14">
          <div className="flex max-w-3xl flex-col gap-3">
            <span className="eyebrow">Measured by the lab</span>
            <h2 id="measured" className="text-[32px] leading-tight font-bold tracking-[-0.02em]">
              Numbers from real runs
            </h2>
            <p className="text-[17px] leading-relaxed text-ink-2">
              The four <code className="font-mono text-[15px]">try</code> experiments measure the
              attacks and the defences on your own machine. These figures come from the runs the
              workshop was written from.
            </p>
          </div>
          <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
            {MEASURED.map((row) => (
              <div key={row.label} className="card flex flex-col gap-2 p-5">
                <dd className="font-mono text-[34px] leading-none font-bold tracking-[-0.02em] text-accent-text">
                  {row.value}
                </dd>
                <dt className="text-[15px] font-semibold text-ink">{row.label}</dt>
                <p className="text-[13.5px] leading-relaxed text-muted">{row.detail}</p>
              </div>
            ))}
          </dl>
        </div>
      </section>

      <section
        aria-labelledby="start"
        className="mx-auto grid max-w-6xl gap-8 px-4 py-14 lg:grid-cols-2 lg:items-center"
      >
        <div className="flex flex-col gap-3">
          <span className="eyebrow">Quick start</span>
          <h2 id="start" className="text-[32px] leading-tight font-bold tracking-[-0.02em]">
            You need uv and git
          </h2>
          <p className="text-[17px] leading-relaxed text-ink-2">
            uv installs Python for you, and the lab uses only Python&apos;s standard library. Every
            service binds to 127.0.0.1 and nothing leaves your machine.
          </p>
        </div>
        <div className="terminal min-w-0 overflow-hidden">
          <div className="flex items-center justify-between bg-code-head py-1 pr-1 pl-4 font-mono text-[12px] tracking-[0.06em] text-code-muted uppercase">
            <span>shell</span>
            <CopyButton text={QUICKSTART} label="Copy the quick start" />
          </div>
          <pre className="overflow-x-auto p-4 text-[14px] leading-relaxed">{QUICKSTART}</pre>
        </div>
      </section>

      <section aria-labelledby="series" className="mx-auto max-w-6xl px-4 pb-16">
        <h2 id="series" className="mb-6 text-[24px] font-bold tracking-[-0.015em]">
          The series
        </h2>
        <ol className="grid gap-3 sm:grid-cols-2">
          {STAGES.map((stage) => (
            <li
              key={stage.number}
              aria-current={stage.current ? 'step' : undefined}
              className={`rounded-lg border p-4 ${
                stage.current ? 'border-accent bg-accent-wash' : 'border-rule bg-surface'
              }`}
            >
              <span className="font-mono text-[12px] text-accent-text">Stage {stage.number}</span>
              <p className="mt-1 font-semibold text-ink">{stage.name}</p>
              <p className="mt-1 text-[13px] text-muted">
                {stage.current ? 'You are here' : 'Stage 1'}
              </p>
            </li>
          ))}
        </ol>
      </section>
    </>
  )
}
