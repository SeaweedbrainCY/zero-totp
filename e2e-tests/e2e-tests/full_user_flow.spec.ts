import { test, expect } from '@playwright/test';


test.use({
  ignoreHTTPSErrors: true
});


let seed = Math.random().toString(36)
let seed2 = Math.random().toString(36).substring(2, 15);
let username = 'Test' + seed;
let username2 = 'Test' + seed2;
let email = 'test' + seed + '@test.test';
let email2 = 'test' + seed2 + '@test.test';
let passphrase = 'fake-$tvIpw5VKH97f0CxEF6C' + seed;
let passphrase2 = 'fake-$tvIpw5VKH97f0CxEF6C' + seed2;

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
  await page.getByRole('textbox', { name: 'XXXXXXXXXXXXXXXX' }).click();
  await expect(page.getByRole('textbox', { name: 'https://github.com' })).toHaveValue('https://github.com');
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


test('Add several TOTP code', async ({ page }) => {
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
  await page.getByRole('textbox', { name: 'GitHub', exact: true }).fill('Amazon');
  await page.getByRole('textbox', { name: 'https://github.com' }).click();
  await page.getByRole('textbox', { name: 'https://github.com' }).fill('amazon.com');
  await page.getByRole('textbox', { name: 'XXXXXXXXXXXXXXXX' }).click();
  await expect(page.getByRole('textbox', { name: 'https://github.com' })).toHaveValue('https://amazon.com');
  await page.getByRole('textbox', { name: 'XXXXXXXXXXXXXXXX' }).fill('AA');
  await page.getByRole('checkbox', { name: 'Display the website logo' }).check();
  await expect(page.getByRole('img', { name: 'favicon' })).toBeVisible();
  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page.getByLabel('New TOTP code added !')).toContainText('New TOTP code added !');
  await page.getByLabel('New TOTP code added !').click();
  await expect(page.locator('app-vault')).toMatchAriaSnapshot(`
    - paragraph: Amazon
    - button "edit"
    - button "copy"
    - paragraph:
      - text: /\\d+/
      - progressbar: /\\d+\\.\\d+%/
    `);
  await page.locator('a').filter({ hasText: 'Add a new TOTP code' }).click();
  await page.getByRole('button', { name: 'Enter it manually' }).click();
  await page.getByRole('textbox', { name: 'GitHub', exact: true }).click();
  await page.getByRole('textbox', { name: 'GitHub', exact: true }).fill('Apple');
  await page.getByRole('textbox', { name: 'https://github.com' }).click();
  await page.getByRole('textbox', { name: 'https://github.com' }).fill('apple.com');
  await page.getByRole('textbox', { name: 'XXXXXXXXXXXXXXXX' }).click();
  await expect(page.getByRole('textbox', { name: 'https://github.com' })).toHaveValue('https://apple.com');
  await page.getByRole('textbox', { name: 'XXXXXXXXXXXXXXXX' }).fill('AA');
  await page.getByRole('checkbox', { name: 'Display the website logo' }).check();
  await expect(page.getByRole('img', { name: 'favicon' })).toBeVisible();
  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page.getByLabel('New TOTP code added !')).toContainText('New TOTP code added !');
  await page.getByLabel('New TOTP code added !').click();
  await expect(page.locator('app-vault')).toMatchAriaSnapshot(`
    - paragraph: Apple
    - button "edit"
    - button "copy"
    - paragraph:
      - text: /\\d+/
      - progressbar: /\\d+\\.\\d+%/
    `);
  await page.locator('a').filter({ hasText: 'Add a new TOTP code' }).click();
  await page.getByRole('button', { name: 'Enter it manually' }).click();
  await page.getByRole('textbox', { name: 'GitHub', exact: true }).click();
  await page.getByRole('textbox', { name: 'GitHub', exact: true }).fill('Microsoft');
  await page.getByRole('textbox', { name: 'https://github.com' }).click();
  await page.getByRole('textbox', { name: 'https://github.com' }).fill('microsoft.com');
  await page.getByRole('textbox', { name: 'XXXXXXXXXXXXXXXX' }).click();
  await expect(page.getByRole('textbox', { name: 'https://github.com' })).toHaveValue('https://microsoft.com');
  await page.getByRole('textbox', { name: 'XXXXXXXXXXXXXXXX' }).fill('AA');
  await page.getByRole('checkbox', { name: 'Display the website logo' }).check();
  await expect(page.getByRole('img', { name: 'favicon' })).toBeVisible();
  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page.getByLabel('New TOTP code added !')).toContainText('New TOTP code added !');
  await page.getByLabel('New TOTP code added !').click();
  await expect(page.locator('app-vault')).toMatchAriaSnapshot(`
    - paragraph: Microsoft
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
  await page.locator('header').filter({ hasText: 'Github' }).getByLabel('edit').click();
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



test('Delete TOTP code', async ({ page }) => {
  await page.goto('https://zero-totp.lan/login');
  await page.getByRole('textbox', { name: 'Email' }).click();
  await page.getByRole('textbox', { name: 'Email' }).fill(email);
  await page.getByRole('textbox', { name: 'Passphrase' }).click();
  await page.getByRole('textbox', { name: 'Passphrase' }).fill(passphrase);
  await page.getByRole('checkbox', { name: 'Remember my email address' }).check();
  await page.getByRole('button', { name: 'Open my vault' }).click();
  await page.waitForURL('**/vault');
  await expect(page.getByLabel('Vault decrypted ✅')).toContainText('Vault decrypted ✅');
  await page.locator('header').filter({ hasText: 'Github' }).getByLabel('edit').click();
  await page.getByRole('button', { name: 'Delete' }).click();
  await page.getByRole('button', { name: 'Destroy this secret' }).click();
  await expect(page.getByLabel('TOTP code deleted !')).toContainText('TOTP code deleted !');
});



test('Edit preferences', async ({ page }) => {
   await page.goto('https://zero-totp.lan/login');
  await page.getByRole('textbox', { name: 'Email' }).click();
  await page.getByRole('textbox', { name: 'Email' }).fill(email);
  await page.getByRole('textbox', { name: 'Passphrase' }).click();
  await page.getByRole('textbox', { name: 'Passphrase' }).fill(passphrase);
  await page.getByRole('checkbox', { name: 'Remember my email address' }).check();
  await page.getByRole('button', { name: 'Open my vault' }).click();
  await page.waitForURL('**/vault');
  await expect(page.getByLabel('Vault decrypted ✅')).toContainText('Vault decrypted ✅');
  await page.getByText('Preferences').click();
  await page.getByRole('combobox').selectOption('hour');
  await page.locator('div').filter({ hasText: /^minutehourUpdate$/ }).getByRole('button').click();
  await expect(page.locator('app-preferences')).toContainText('Success ! This new value will be applied at your next login');
  await page.getByPlaceholder('10').click();
  await page.getByPlaceholder('10').fill('24');
  await page.locator('div').filter({ hasText: /^minutehourUpdate$/ }).getByRole('button').click();
  await expect(page.getByText('Success ! This new value will')).toBeVisible();
  await page.getByRole('button', { name: 'More info' }).click();
  await expect(page.getByRole('article').getByRole('button')).toBeVisible();
  await page.getByRole('article').getByRole('button').click();
  await page.getByRole('button', { name: 'Always' }).click();
  await expect(page.locator('app-preferences')).toMatchAriaSnapshot(`- button "Always"`);
  await page.getByRole('button', { name: 'Never' }).click();
  await expect(page.locator('app-preferences')).toMatchAriaSnapshot(`- button "Never"`);
  await page.getByPlaceholder('Default : 20').click();
  await page.getByPlaceholder('Default : 20').fill('30');
  await page.getByRole('button', { name: 'Update' }).nth(1).click();
  await expect(page.getByPlaceholder('Default : 20')).toHaveValue('30');
  await page.getByPlaceholder('Default : 30').click();
  await page.getByPlaceholder('Default : 30').fill('365');
  await page.getByRole('button', { name: 'Update' }).nth(2).click();
  await expect(page.getByPlaceholder('Default : 30')).toBeVisible();
  await page.getByRole('button', { name: 'Display advanced settings' }).click();
  await expect(page.locator('app-preferences')).toContainText('Zero-TOTP is still under development. This value will be customizable in the future.');
});



test('Edit account', async ({ page }) => {
  await page.goto('https://zero-totp.lan/login');
  await page.getByRole('textbox', { name: 'Email' }).click();
  await page.getByRole('textbox', { name: 'Email' }).fill(email);
  await page.getByRole('textbox', { name: 'Passphrase' }).click();
  await page.getByRole('textbox', { name: 'Passphrase' }).fill(passphrase);
  await page.getByRole('checkbox', { name: 'Remember my email address' }).check();
  await page.getByRole('button', { name: 'Open my vault' }).click();
  await page.waitForURL('**/vault');
  await expect(page.getByLabel('Vault decrypted ✅')).toContainText('Vault decrypted ✅');
  await page.getByText('Account').click();
  await expect(page.locator('app-account')).toContainText('Your current username is: ' + username);
  await page.getByRole('textbox', { name: 'Username' }).click();
  await page.getByRole('textbox', { name: 'Username' }).fill(username2);
  await page.getByRole('button', { name: 'Update' }).first().click();
  await expect(page.locator('app-account')).toContainText('Your current username is: ' + username2);
  await expect(page.locator('app-account')).toContainText('Your current email is : ' + email);

  await page.getByRole('textbox', { name: 'Email', exact: true }).click();
  await page.getByRole('textbox', { name: 'Email', exact: true }).fill(email2);
  await page.getByRole('textbox', { name: 'Confirm email' }).click();
  await page.getByRole('textbox', { name: 'Confirm email' }).fill(email2);
  await page.getByRole('button', { name: 'Update' }).nth(1).click();
  await expect(page.locator('app-account')).toContainText('Your current email is : ' + email2);
  await page.getByRole('textbox', { name: 'Passphrase', exact: true }).click();
  await page.getByRole('textbox', { name: 'Passphrase', exact: true }).fill(passphrase);
  await page.getByRole('textbox', { name: 'New passphrase' }).click();
  await page.getByRole('textbox', { name: 'New passphrase' }).fill(passphrase2);
  await page.getByRole('textbox', { name: 'Confirm Passphrase' }).click();
  await page.getByRole('textbox', { name: 'Confirm Passphrase' }).fill(passphrase2);
  await page.getByRole('button', { name: 'Update' }).nth(2).click();
  await expect(page.locator('app-account')).toContainText('Be careful');
  await expect(page.locator('app-account')).toMatchAriaSnapshot(`
    - heading "Be careful" [level=1]
    - strong: "Changing your passphrase will :"
    - list:
      - listitem: Re-encrypt your current vault
      - listitem: Your old backup will still be encrypted with your former passphrase
      - listitem: Your Google Drive backup will be updated. If you have old backup, they will still be encrypted with your former passphrase. If your passphrase is not safe anymore you should delete them without delay
      - listitem: If you lose this new passphrase, it is impossible to recover it
      - listitem: If you change your passphrase for security reasons, securely delete your backup as soon as possible
    `);
  await page.getByRole('button', { name: 'I\'m sure' }).click();
  await expect(page.getByLabel('Your passphrase is updated !')).toContainText('Your passphrase is updated ! You can now log in with your new passphrase 🎉');
});




test('Delete account', async ({ page }) => {
  await page.goto('https://zero-totp.lan/login');
  await page.getByRole('textbox', { name: 'Email' }).click();
  await page.getByRole('textbox', { name: 'Email' }).fill(email2);
  await page.getByRole('textbox', { name: 'Passphrase' }).click();
  await page.getByRole('textbox', { name: 'Passphrase' }).fill(passphrase2);
  await page.getByRole('checkbox', { name: 'Remember my email address' }).check();
  await page.getByRole('button', { name: 'Open my vault' }).click();
  await page.waitForURL('**/vault');
  await expect(page.getByLabel('Vault decrypted ✅')).toContainText('Vault decrypted ✅');
  await page.getByText('Account').click();
  await page.getByRole('button', { name: 'Delete your account' }).click();
  await expect(page.locator('#confirmation')).toMatchAriaSnapshot(`
    - heading "Are you sure ?" [level=1]
    - strong: You won't be able to undo this action. You will no longer access to your TOTP vault
    - text: .
    - strong: You will lose ALL your secrets
    - strong: ALL your backups on google drive will be DESTROYED
    - strong: "To delete your account, confirm your passphrase :"
    - textbox "Passphrase"
    `);
  await page.locator('#confirmation').getByRole('textbox', { name: 'Passphrase' }).click();
  await page.locator('#confirmation').getByRole('textbox', { name: 'Passphrase' }).fill(passphrase2);
  await page.getByRole('button', { name: 'Destroy my account definitely' }).click();
  await expect(page.getByLabel('Thanks for having used Zero-')).toContainText('Thanks for having used Zero-TOTP. Your account has been deleted. Good bye. 👋');
  await page.getByRole('textbox', { name: 'Email' }).click();
  await page.getByRole('textbox', { name: 'Email' }).fill(email2);
  await page.getByRole('textbox', { name: 'Passphrase' }).click();
  await page.getByRole('textbox', { name: 'Passphrase' }).fill(passphrase2);
  await page.getByRole('button', { name: 'Open my vault' }).click();
  await expect(page.getByLabel('Invalid credentials')).toContainText('Invalid credentials');
});