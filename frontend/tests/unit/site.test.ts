import fs from 'node:fs'
import path from 'node:path'

import { describe, expect, it } from 'vitest'

import { CASES, MEASURED } from '@/lib/site'
import { CHAPTERS } from '@/lib/workshop'

const ROOT = path.join(process.cwd(), '..')
const lab = fs.readFileSync(path.join(ROOT, 'lab/trust/__main__.py'), 'utf8')
const read = (name: string) =>
  fs.readFileSync(path.join(process.cwd(), 'src/lib/experiments', name), 'utf8')

describe('the site matches the lab', () => {
  it.each(CASES.map((item) => [item.number, item.title] as const))(
    'case %s is titled as the lab titles it',
    (number, title) => {
      expect(lab).toContain(`${Number(number)}: ("case${number}_`)
      expect(lab).toContain(JSON.stringify(title))
    },
  )

  it('lists the ten cases in order', () => {
    expect(CASES.map((item) => Number(item.number))).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
  })

  it('groups every case under a known level', () => {
    const levels = new Set(['Foundations', 'Access and identity', 'Server-side and redirects'])
    for (const item of CASES) expect(levels.has(item.level)).toBe(true)
  })

  // Each measured figure must appear in the real output of the experiment it came from.
  const proofs: [string, string, string][] = [
    ['Tokens dumped through the login', 'exfiltrate.txt', '3 tokens in 3 requests, 581 bytes'],
    ['Rows a string-built query leaks', 'inject.txt', 'OR always true      3 rows'],
    ['Collisions in 200,000 weak tokens', 'tokens.txt', '142,144'],
    ['Internal URLs a blocklist lets through', 'ssrf.txt', 'the blocklist lets 3 through'],
  ]

  it.each(proofs)('%s is backed by %s', (label, file, proof) => {
    expect(MEASURED.some((row) => row.label === label)).toBe(true)
    expect(read(file)).toContain(proof)
  })
})

describe('chapters that exist', () => {
  it('match a case number and quote its commands, with no em dashes', () => {
    for (const chapter of CHAPTERS) {
      const number = Number(chapter.number)
      expect(number, chapter.slug).toBeGreaterThanOrEqual(1)
      expect(number, chapter.slug).toBeLessThanOrEqual(CASES.length)
      expect(chapter.body, chapter.slug).toContain(`trust run ${number}`)
      expect(chapter.body, chapter.slug).toContain(`trust check ${number}`)
      expect(chapter.body, chapter.slug).not.toMatch(/[–—]/)
    }
  })
})
