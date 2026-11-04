// @ts-check
import { readdirSync } from 'node:fs';
import tseslint from 'typescript-eslint';
import { importX } from 'eslint-plugin-import-x';
import { createTypeScriptImportResolver } from 'eslint-import-resolver-typescript';

// Every folder in src/apps is an app; new apps are picked up automatically.
const apps = readdirSync(new URL('./src/apps', import.meta.url), { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => entry.name);

export default [
  { ignores: ['dist/**', '.angular/**', 'node_modules/**'] },
  {
    files: ['src/**/*.ts'],
    languageOptions: { parser: tseslint.parser },
    plugins: { 'import-x': importX },
    settings: {
      'import-x/resolver-next': [createTypeScriptImportResolver({ project: './tsconfig.json' })],
    },
    rules: {
      'import-x/no-restricted-paths': ['error', {
        basePath: import.meta.dirname,
        zones: [
          // An app may only import itself (plus shared code).
          ...apps.map((app) => ({
            target: `./src/apps/${app}`,
            from: './src/apps',
            except: [`./${app}`],
            message: `"${app}" must not import another app. Move the code to src/shared or use DI.`,
          })),
          // Shared code must never depend on an app.
          {
            target: ['./src/shared', './src/capacitor', './src/environments'],
            from: './src/apps',
            message: 'Shared code must not import from an app. Use an abstraction + DI instead.',
          },
        ],
      }],
    },
  },
];
