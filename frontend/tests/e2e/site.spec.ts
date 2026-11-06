import { expect, test } from '@playwright/test'

test('home lists the ten cases and the two stages', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Trust no request')
  await expect(page.locator('section:has(#cases) ol > li')).toHaveCount(10)
  await expect(page.locator('section:has(#series) ol > li')).toHaveCount(2)
})

test('the injection simulator reacts to the input', async ({ page }) => {
  await page.goto('/')
  const sim = page.locator('section:has(h1)')
  // It loads on the OR-always-true payload, which the string-built query lets through.
  await expect(sim.getByText(/Bypassed: signed in as/).first()).toBeVisible()
  // Switch to a real sign-in and the verdict changes.
  await page.getByRole('button', { name: 'A real sign-in' }).click()
  await expect(page.getByText('Signed in as u_1041').first()).toBeVisible()
})

test('the chapters page lists every case', async ({ page }) => {
  await page.goto('/workshop')
  await expect(page.locator('main ol > li')).toHaveCount(10)
  await expect(page.locator('main')).toContainText('The fetch that reached the metadata service')
})

test('a chapter renders and the quiz answers', async ({ page }) => {
  await page.goto('/workshop/01-sql-injection')
  await expect(page.getByRole('heading', { level: 1 })).toContainText('rewrote the query')
  const quiz = page.getByRole('region', { name: /Two questions/ })
  await quiz.getByRole('button', { name: /bound as data/ }).click()
  await expect(quiz.getByRole('status').first()).toContainText('Right.')
})

test('previous and next links move between chapters', async ({ page }) => {
  await page.goto('/workshop/01-sql-injection')
  await page.getByRole('link', { name: /Next/ }).click()
  await expect(page).toHaveURL(/\/workshop\/02-/)
})

test('back to top appears after scrolling and returns to the top', async ({ page }) => {
  await page.goto('/workshop')
  await page.setViewportSize({ width: 390, height: 500 })
  const button = page.getByRole('button', { name: 'Back to top' })
  await page.evaluate(() => window.scrollTo(0, 2000))
  await expect(button).toBeVisible()
  await button.click()
  await expect.poll(() => page.evaluate(() => window.scrollY)).toBeLessThan(50)
})

test('nothing overflows the page sideways', async ({ page }) => {
  for (const url of [
    '/',
    '/workshop',
    '/workshop/01-sql-injection',
    '/workshop/08-ssrf',
    '/workshop/10-open-redirect',
  ]) {
    await page.goto(url)
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    )
    expect(overflow, url).toBeLessThanOrEqual(0)
  }
})
