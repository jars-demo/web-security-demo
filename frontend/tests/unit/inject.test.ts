import { describe, expect, it } from 'vitest'

import { login, PRESETS } from '@/lib/inject'

describe('the injection simulator', () => {
  it('signs in a real credential in both modes', () => {
    for (const mode of ['concat', 'parameterized'] as const) {
      const out = login('u_1041@acme.test', 'hunter2-correct', mode)
      expect(out.signedInAs).toBe('u_1041')
      expect(out.bypass).toBe(false)
      expect(out.rows).toEqual(['u_1041'])
    }
  })

  it('rejects a wrong password in both modes', () => {
    for (const mode of ['concat', 'parameterized'] as const) {
      const out = login('u_1041@acme.test', 'guessing', mode)
      expect(out.signedInAs).toBeNull()
      expect(out.bypass).toBe(false)
    }
  })

  it('an OR-always-true email bypasses the string-built query', () => {
    const out = login("x' OR '1'='1' -- ", 'anything', 'concat')
    expect(out.bypass).toBe(true)
    expect(out.rows).toHaveLength(3) // every user comes back, matching `try inject`
  })

  it('a comment payload signs in as the named admin, string-built', () => {
    const out = login("u_1099@acme.test' -- ", 'anything', 'concat')
    expect(out.bypass).toBe(true)
    expect(out.signedInAs).toBe('u_1099')
    expect(out.rows).toEqual(['u_1099'])
  })

  it('bound parameters refuse both injection payloads', () => {
    for (const email of ["x' OR '1'='1' -- ", "u_1099@acme.test' -- "]) {
      const out = login(email, 'anything', 'parameterized')
      expect(out.rows).toHaveLength(0)
      expect(out.signedInAs).toBeNull()
      expect(out.bypass).toBe(false)
    }
  })

  it('every preset is one of the four attacks offered', () => {
    expect(PRESETS).toHaveLength(4)
    for (const preset of PRESETS) {
      expect(preset.email.length).toBeGreaterThan(0)
    }
  })
})
