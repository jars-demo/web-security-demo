// Colour pairs the site puts text on. Each value mirrors a variable in globals.css, and a unit
// test checks both that they match and that every pair meets WCAG AA (4.5:1).

export const TOKENS = {
  canvas: '#f6f7f9',
  surface: '#ffffff',
  surface2: '#eceff3',
  ink: '#0d1321',
  ink2: '#344054',
  muted: '#5b6474',
  slate: '#0d1321',
  slate2: '#1a2233',
  onSlate: '#f2f4f7',
  onSlateMuted: '#aab4c4',
  accent: '#4f46e5',
  accentText: '#4338ca',
  accentWash: '#e8e7fc',
  onAccent: '#ffffff',
  accentGlow: '#a5b4fc',
  pass: '#157347',
  passWash: '#e6f4ec',
  fail: '#b42318',
  failWash: '#fdecea',
  codeBg: '#0d1321',
  codeHead: '#1a2233',
  codeInk: '#e6eaf0',
  codeMuted: '#a3adbd',
} as const

export type Token = keyof typeof TOKENS

export const TEXT_PAIRS: readonly [Token, Token][] = [
  ['ink', 'canvas'],
  ['ink2', 'canvas'],
  ['muted', 'canvas'],
  ['ink', 'surface'],
  ['ink2', 'surface'],
  ['muted', 'surface'],
  ['ink2', 'surface2'],
  ['muted', 'surface2'],
  ['accentText', 'canvas'],
  ['accentText', 'surface'],
  ['accentText', 'surface2'],
  ['accentText', 'accentWash'],
  ['onAccent', 'accent'],
  ['onSlate', 'slate'],
  ['onSlateMuted', 'slate'],
  ['onSlate', 'slate2'],
  ['onSlateMuted', 'slate2'],
  ['accentGlow', 'slate'],
  ['accentGlow', 'slate2'],
  ['pass', 'passWash'],
  ['fail', 'failWash'],
  ['codeInk', 'codeBg'],
  ['codeMuted', 'codeBg'],
  ['codeMuted', 'codeHead'],
]

function channel(hex: string, offset: number): number {
  const value = parseInt(hex.slice(offset, offset + 2), 16) / 255
  return value <= 0.03928 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4
}

function luminance(hex: string): number {
  return 0.2126 * channel(hex, 1) + 0.7152 * channel(hex, 3) + 0.0722 * channel(hex, 5)
}

export function contrast(a: string, b: string): number {
  const [la, lb] = [luminance(a), luminance(b)]
  return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05)
}
