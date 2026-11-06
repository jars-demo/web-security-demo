import type { Metadata } from 'next'
import Link from 'next/link'
import { notFound } from 'next/navigation'

import { CopyButton } from '@/components/CopyButton'
import { Inline } from '@/components/Inline'
import { headingsOf, Markdown } from '@/components/Markdown'
import { Quiz } from '@/components/Quiz'
import { QUIZ } from '@/lib/quiz'
import { CHAPTERS, findChapter } from '@/lib/workshop'

// Chapters are prerendered. Until the first one is written, one placeholder path keeps the route
// valid and renders a 404.
const PLACEHOLDER = '00-none'

export function generateStaticParams() {
  return CHAPTERS.length
    ? CHAPTERS.map((chapter) => ({ slug: chapter.slug }))
    : [{ slug: PLACEHOLDER }]
}

export async function generateMetadata(props: PageProps<'/workshop/[slug]'>): Promise<Metadata> {
  const { slug } = await props.params
  const chapter = findChapter(slug)
  return { title: chapter ? `${chapter.number}. ${chapter.title}` : 'Chapter' }
}

function Command({ text }: { text: string }) {
  return (
    <div className="terminal flex items-center justify-between gap-2 py-1 pr-1 pl-3.5 text-[13.5px]">
      <code className="min-w-0 overflow-x-auto py-1.5 whitespace-nowrap">
        <span className="text-accent-glow">$ </span>
        {text}
      </code>
      <CopyButton text={text} label={`Copy ${text}`} />
    </div>
  )
}

export default async function ChapterPage(props: PageProps<'/workshop/[slug]'>) {
  const { slug } = await props.params
  const chapter = findChapter(slug)
  if (!chapter) notFound()
  const index = CHAPTERS.indexOf(chapter)
  const previous = CHAPTERS[index - 1]
  const next = CHAPTERS[index + 1]
  const number = Number(chapter.number)
  const quiz = QUIZ[chapter.number]

  return (
    <div className="mx-auto grid max-w-6xl gap-10 px-4 pt-10 pb-24 lg:grid-cols-[220px_minmax(0,1fr)] xl:grid-cols-[240px_minmax(0,1fr)_220px]">
      <aside className="hidden lg:block">
        <nav aria-label="Chapters" className="sticky top-20 flex flex-col gap-1 text-[14px]">
          <span className="mb-1 font-mono text-[11px] tracking-[0.08em] text-muted uppercase">
            Chapters
          </span>
          {CHAPTERS.map((c) => (
            <Link
              key={c.slug}
              href={`/workshop/${c.slug}`}
              aria-current={c.slug === chapter.slug ? 'page' : undefined}
              className={`rounded-md px-2 py-1.5 ${
                c.slug === chapter.slug
                  ? 'bg-accent-wash font-semibold text-accent-text'
                  : 'text-ink-2 hover:bg-surface-2'
              }`}
            >
              <span className="font-mono text-[12px] text-muted">{c.number}</span> {c.title}
            </Link>
          ))}
        </nav>
      </aside>

      <article className="flex min-w-0 flex-col gap-8">
        <header className="flex flex-col gap-4 border-b border-rule pb-8">
          <span className="eyebrow">
            Chapter {chapter.number}
            {chapter.minutes ? ` · ${chapter.minutes} minutes` : ''}
          </span>
          <h1 className="text-[34px] leading-[1.1] font-bold tracking-[-0.025em] sm:text-[42px]">
            {chapter.title}
          </h1>
          {chapter.summary ? (
            <p className="text-[19px] leading-relaxed text-ink-2">
              <Inline text={chapter.summary} />
            </p>
          ) : null}
          <div className="flex flex-col gap-2 rounded-lg border border-rule bg-surface p-4">
            <span className="text-[14px] text-ink-2">From the lab folder:</span>
            <Command text={`uv run python -m trust run ${number}`} />
            <Command text={`uv run python -m trust check ${number}`} />
          </div>
        </header>

        <div className="prose-doc">
          <Markdown>{chapter.body}</Markdown>
        </div>

        {quiz ? <Quiz questions={quiz} /> : null}

        <nav aria-label="Chapter navigation" className="grid gap-3 sm:grid-cols-2">
          {previous ? (
            <Link
              href={`/workshop/${previous.slug}`}
              className="card flex flex-col gap-1 p-4 hover:border-accent"
            >
              <span className="text-[13px] text-muted">Previous</span>
              <span className="font-semibold">
                {previous.number}. {previous.title}
              </span>
            </Link>
          ) : (
            <span />
          )}
          {next ? (
            <Link
              href={`/workshop/${next.slug}`}
              className="card flex flex-col gap-1 p-4 text-right hover:border-accent"
            >
              <span className="text-[13px] text-muted">Next</span>
              <span className="font-semibold">
                {next.number}. {next.title}
              </span>
            </Link>
          ) : null}
        </nav>
      </article>

      <aside className="hidden xl:block">
        <div className="sticky top-20 flex flex-col gap-3">
          <span className="font-mono text-[11px] tracking-[0.08em] text-muted uppercase">
            On this page
          </span>
          <ul className="flex flex-col gap-1.5 text-[14px]">
            {headingsOf(chapter.body).map((heading) => (
              <li key={heading.id}>
                <a href={`#${heading.id}`} className="text-ink-2 hover:text-accent-text">
                  {heading.text}
                </a>
              </li>
            ))}
          </ul>
        </div>
      </aside>
    </div>
  )
}
