import Link from 'next/link'

import { CASES, type Level, LEVELS } from '@/lib/site'
import { chapterFor } from '@/lib/workshop'

// The ten cases, grouped by level, each showing its real symptom. A case links to its chapter once
// the chapter is written.

function Row({ number }: { number: string }) {
  const item = CASES.find((c) => c.number === number)!
  const chapter = chapterFor(number)
  const inner = (
    <>
      <div className="flex items-baseline justify-between gap-3">
        <span className="font-mono text-[13px] text-accent-text">
          {item.number} · {item.topic}
        </span>
        {chapter ? (
          <span className="shrink-0 text-[13px] text-muted">{chapter.minutes} min</span>
        ) : (
          <span className="shrink-0 rounded bg-surface-2 px-2 py-0.5 text-[12px] text-muted">
            soon
          </span>
        )}
      </div>
      <h3 className="text-[18px] leading-snug font-semibold text-ink">
        {chapter?.title ?? item.title}
      </h3>
      <p className="text-[14px] leading-relaxed text-ink-2">{item.symptom}</p>
      <p className="mt-auto pt-1 font-mono text-[12.5px] text-muted">
        uv run python -m trust run {Number(item.number)}
      </p>
    </>
  )
  return chapter ? (
    <Link
      href={`/workshop/${chapter.slug}`}
      className="card flex h-full flex-col gap-2 p-4 hover:border-accent sm:p-5"
    >
      {inner}
    </Link>
  ) : (
    <div className="card flex h-full flex-col gap-2 p-4 sm:p-5">{inner}</div>
  )
}

export function CaseList() {
  const byLevel = (level: Level) => CASES.filter((c) => c.level === level)
  return (
    <div className="flex flex-col gap-10">
      {LEVELS.map((level, index) => (
        <section
          key={level.name}
          aria-labelledby={`level-${index}`}
          className="flex flex-col gap-4"
        >
          <div className="flex flex-col gap-1">
            <div className="flex items-baseline gap-3">
              <span className="font-mono text-[12px] text-muted">
                {String(index + 1).padStart(2, '0')}
              </span>
              <h3 id={`level-${index}`} className="text-[20px] font-bold tracking-[-0.015em]">
                {level.name}
              </h3>
            </div>
            <p className="text-[15px] text-muted">{level.blurb}</p>
          </div>
          <ol className="grid gap-3 md:grid-cols-2">
            {byLevel(level.name).map((item) => (
              <li key={item.number} className="flex">
                <div className="flex-1">
                  <Row number={item.number} />
                </div>
              </li>
            ))}
          </ol>
        </section>
      ))}
    </div>
  )
}
