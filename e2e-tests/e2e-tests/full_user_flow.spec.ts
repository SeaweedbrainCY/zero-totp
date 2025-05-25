import { test, expect } from '@playwright/test';

test.use({
  ignoreHTTPSErrors: true
});

let username = 'Test';
let email = 'test@test.test';
let passphrase = 'fake-$tvIpw5VKH97f0CxEF6C';

test('Signup flow', async ({ page }) => {
  await page.goto('https://zero-totp.lan/signup');
  await page.getByRole('textbox', { name: 'Username' }).click();
  await page.getByRole('textbox', { name: 'Username' }).fill(username);
  await page.getByRole('textbox', { name: 'Email' }).click();
  await page.getByRole('textbox', { name: 'Email' }).fill(email);
  await page.getByRole('textbox', { name: 'Passphrase', exact: true }).click();
  await page.getByRole('textbox', { name: 'Passphrase', exact: true }).fill(passphrase);
  await page.getByRole('textbox', { name: 'Confirm passphrase' }).click();
  await page.getByRole('textbox', { name: 'Confirm passphrase' }).fill(passphrase);
  await page.getByRole('checkbox', { name: 'I agree to the Privacy Policy' }).check();
  await page.getByRole('button', { name: 'Start my zero-trip' }).click();
  await page.getByRole('textbox', { name: 'My passphrase is strong and I' }).click();
  await page.getByRole('textbox', { name: 'My passphrase is strong and I' }).fill('My passphrase is strong and I won\'t forget i');
  await page.getByRole('textbox', { name: 'My passphrase is strong and I' }).pressSequentially('t')
  await page.getByRole('button', { name: 'Create my vault' }).click();
  await page.waitForURL('**/login/**');
  await page.getByLabel('Account created successfully').click();
  await expect(page.getByText('It\'s time to open your vault !')).toBeVisible();
});


test('Add TOTP code', async ({ page }) => {
  await page.goto('https://zero-totp.lan/login');
  await page.getByRole('textbox', { name: 'Email' }).click();
  await page.getByRole('textbox', { name: 'Email' }).fill(email);
  await page.getByRole('textbox', { name: 'Passphrase' }).click();
  await page.getByRole('textbox', { name: 'Passphrase' }).fill(passphrase);
  await page.getByRole('checkbox', { name: 'Remember my email address' }).check();
  await page.getByRole('button', { name: 'Open my vault' }).click();
  await page.waitForURL('**/vault');
  await expect(page.getByLabel('Vault decrypted ✅')).toContainText('Vault decrypted ✅');
  await page.locator('a').filter({ hasText: 'Add a new TOTP code' }).click();
  await page.getByRole('button', { name: 'Enter it manually' }).click();
  await page.getByRole('textbox', { name: 'GitHub', exact: true }).click();
  await page.getByRole('textbox', { name: 'GitHub', exact: true }).fill('Github');
  await page.getByRole('textbox', { name: 'https://github.com' }).click();
  await page.getByRole('textbox', { name: 'https://github.com' }).fill('github.com');
  await expect(page.getByRole('textbox', { name: 'https://github.com' })).toBeVisible();
  await page.getByRole('textbox', { name: 'XXXXXXXXXXXXXXXX' }).click();
  await page.getByRole('textbox', { name: 'XXXXXXXXXXXXXXXX' }).fill('AA');
  await page.getByRole('checkbox', { name: 'Display the website logo' }).check();
  await expect(page.getByRole('img', { name: 'favicon' })).toBeVisible();
  await page.locator('.tag > .ng-fa-icon > .svg-inline--fa').click();
  await page.getByRole('textbox', { name: 'Tag\'s name' }).click();
  await page.getByRole('textbox', { name: 'Tag\'s name' }).fill('test');
  await page.locator('section').filter({ hasText: 'Add a tag' }).getByRole('button').click();
  await expect(page.getByText('test')).toBeVisible();
  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page.getByLabel('New TOTP code added !')).toContainText('New TOTP code added !');
  await expect(page.locator('app-vault')).toMatchAriaSnapshot(`
    - paragraph: Github
    - button "edit"
    - button "copy"
    - paragraph:
      - text: /\\d+/
      - progressbar: /\\d+\\.\\d+%/
    `);
});


test('Edit TOTP code', async ({ page }) => {
  await page.goto('https://zero-totp.lan/login');
  await page.getByRole('textbox', { name: 'Email' }).click();
  await page.getByRole('textbox', { name: 'Email' }).fill(email);
  await page.getByRole('textbox', { name: 'Passphrase' }).click();
  await page.getByRole('textbox', { name: 'Passphrase' }).fill(passphrase);
  await page.getByRole('checkbox', { name: 'Remember my email address' }).check();
  await page.getByRole('button', { name: 'Open my vault' }).click();
  await page.waitForURL('**/vault');
  await expect(page.getByLabel('Vault decrypted ✅')).toContainText('Vault decrypted ✅');
  await page.getByRole('button', { name: 'edit' }).click();
  await page.getByRole('textbox', { name: 'XXXXXXXXXXXXXXXX' }).dblclick();
  await page.getByRole('textbox', { name: 'XXXXXXXXXXXXXXXX' }).fill('BB');
  await page.getByRole('combobox').selectOption('Red');
  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page.getByLabel('TOTP code updated !')).toContainText('TOTP code updated !');
  await expect(page.locator('app-vault')).toContainText('Github');
  await expect(page.locator('app-vault')).toMatchAriaSnapshot(`
    - paragraph: Github
    - button "edit"
    - button "copy"
    - paragraph:
      - text: /\\d+/
      - progressbar: /\\d+\\.\\d+%/
    `);
});