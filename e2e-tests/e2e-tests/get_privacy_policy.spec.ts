import { test, expect } from '@playwright/test';

test.use({
  ignoreHTTPSErrors: true
});

test('Test get privacy policy in both lang', async ({ page }) => {
  await page.goto('https://zero-totp.lan/privacy');
  await page.getByRole('heading', { name: 'Zero-TOTP Privacy Policy' }).click();
  await page.locator('.navbar-link').click();
  await page.locator('a').filter({ hasText: 'Français' }).click();
  await page.getByRole('heading', { name: 'Politique de confidentialité' }).click();
});