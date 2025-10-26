import { test, expect } from '@playwright/test'

test('home page has title', async ({ page }) => {
  await page.goto('/')
  await expect(page).toHaveTitle(/AreaYield OS/)
})

test('home page has main content', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('h1')).toContainText('AreaYield OS')
})

