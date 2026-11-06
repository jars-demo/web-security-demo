'use client'

import { useState } from 'react'

import { login, type Mode, PRESETS } from '@/lib/inject'

// The core idea, made interactive: the same login, built two ways. Type an email and password, or
// pick a known payload, and watch the string-built query get rewritten while the parameterized one
// does not. The logic is in lib/inject.ts and is unit-tested.

function Verdict({ email, password, mode }: { email: string; password: string; mode: Mode }) {
  const result = login(email, password, mode)
  const ok = result.signedInAs !== null
  const tone = result.bypass ? 'fail' : ok ? 'pass' : 'muted'
  const label = result.error
    ? 'SQL error'
    : result.bypass
      ? `Bypassed: signed in as ${result.signedInAs}`
      : ok
        ? `Signed in as ${result.signedInAs}`
        : 'Rejected'
  const toneClass =
    tone === 'fail'
      ? 'border-fail bg-fail-wash text-fail'
      : tone === 'pass'
        ? 'border-pass bg-pass-wash text-pass'
        : 'border-rule bg-surface-2 text-muted'

  return (
    <div className="flex flex-col gap-2">
      <div className="terminal min-w-0 overflow-x-auto p-3 text-[12.5px] leading-relaxed">
        <code className="whitespace-pre-wrap break-words">{result.query}</code>
      </div>
      <div
        className={`flex items-center gap-2 rounded-lg border px-3 py-2 text-[14px] ${toneClass}`}
      >
        <span aria-hidden="true" className="font-mono text-[13px]">
          {result.bypass ? '[!]' : ok ? '[ok]' : '[x]'}
        </span>
        <span className="font-semibold">{label}</span>
        <span className="ml-auto font-mono text-[12.5px]">
          {result.rows.length} row{result.rows.length === 1 ? '' : 's'}
        </span>
      </div>
    </div>
  )
}

export function InjectionSim() {
  const [email, setEmail] = useState(PRESETS[2]!.email)
  const [password, setPassword] = useState(PRESETS[2]!.password)

  return (
    <div className="card flex flex-col gap-5 p-5 sm:p-6">
      <div className="flex flex-wrap gap-2">
        {PRESETS.map((preset) => (
          <button
            key={preset.label}
            type="button"
            onClick={() => {
              setEmail(preset.email)
              setPassword(preset.password)
            }}
            className="inline-flex min-h-10 items-center rounded-full border border-rule bg-surface px-3 text-[13px] text-ink-2 hover:border-accent hover:text-accent-text"
          >
            {preset.label}
          </button>
        ))}
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        <label className="flex flex-col gap-1.5 text-[13px] text-muted">
          email
          <input
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            spellCheck={false}
            autoCapitalize="off"
            autoCorrect="off"
            className="min-h-11 rounded-lg border border-rule bg-surface px-3 font-mono text-[13px] text-ink"
          />
        </label>
        <label className="flex flex-col gap-1.5 text-[13px] text-muted">
          password
          <input
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            spellCheck={false}
            autoCapitalize="off"
            autoCorrect="off"
            className="min-h-11 rounded-lg border border-rule bg-surface px-3 font-mono text-[13px] text-ink"
          />
        </label>
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <div className="flex flex-col gap-2">
          <h3 className="flex items-center gap-2 text-[14px] font-semibold text-ink">
            <span className="rounded bg-fail-wash px-2 py-0.5 font-mono text-[12px] text-fail">
              built from text
            </span>
          </h3>
          <Verdict email={email} password={password} mode="concat" />
        </div>
        <div className="flex flex-col gap-2">
          <h3 className="flex items-center gap-2 text-[14px] font-semibold text-ink">
            <span className="rounded bg-pass-wash px-2 py-0.5 font-mono text-[12px] text-pass">
              bound parameters
            </span>
          </h3>
          <Verdict email={email} password={password} mode="parameterized" />
        </div>
      </div>

      <p className="text-[13.5px] leading-relaxed text-muted">
        The same input. On the left it is pasted into the query text, so a quote can end the string
        and the rest becomes query. On the right it is bound as a value, so it only ever matches a
        row or does not.
      </p>
    </div>
  )
}
