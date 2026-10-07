import { ApplicationConfig, provideAppInitializer, provideCheckNoChangesConfig, provideZonelessChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideAnimations } from '@angular/platform-browser/animations';
import { MissingTranslationHandler, provideTranslateService } from '@ngx-translate/core';
import { provideToastr } from 'ngx-toastr';

import { routes } from './app.routes';
import { MissingTranslationHelper, initTranslations } from '../../shared/i18n';

// Rescue must work while Zero-TOTP is down: no HttpClient, no auth interceptor, no API.
// Any code path that tries to inject HttpClient will fail loudly with a NullInjectorError.
export const appConfig: ApplicationConfig = {
  providers: [
    provideZonelessChangeDetection(),
    // Surfaces UI updates missed under zoneless (useful while porting legacy components)
    provideCheckNoChangesConfig({ exhaustive: true, interval: 1000 }),
    provideRouter(routes),
    provideAnimations(), // required by ngx-toastr
    provideToastr({
      positionClass: 'toast-bottom-full-width',
      closeButton: true,
      progressBar: true,
      progressAnimation: 'decreasing',
      tapToDismiss: true,
    }),
    // No loader: translations are bundled and registered by initTranslations
    provideTranslateService({
      missingTranslationHandler: {
        provide: MissingTranslationHandler,
        useClass: MissingTranslationHelper,
      },
    }),
    provideAppInitializer(initTranslations),
  ],
};
