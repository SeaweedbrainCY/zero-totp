import { ApplicationConfig, isDevMode, provideAppInitializer, provideCheckNoChangesConfig, provideZonelessChangeDetection } from '@angular/core';
import { HttpClient, provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { provideRouter, withInMemoryScrolling, withViewTransitions } from '@angular/router';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideServiceWorker } from '@angular/service-worker';
import { MissingTranslationHandler, TranslateLoader, provideTranslateService } from '@ngx-translate/core';
import { provideMarkdown } from 'ngx-markdown';
import { provideToastr } from 'ngx-toastr';
import { provideNgIdle } from '@ng-idle/core';

import { routes } from './app.routes';
import { HttpLoaderFactory, MissingTranslationHelper, initTranslations } from './i18n';
import { httpInterceptorProviders } from './helpers/auth.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZonelessChangeDetection(),
    provideCheckNoChangesConfig({ exhaustive: true, interval: 1000 }),
    provideRouter(
      routes,
      withViewTransitions(),
      withInMemoryScrolling({ scrollPositionRestoration: 'enabled' }),
    ),
    provideHttpClient(withInterceptorsFromDi()),
    httpInterceptorProviders,
    provideAnimations(), // required by ngx-toastr
    provideToastr(),
    provideNgIdle(),
    provideMarkdown({ loader: HttpClient }),
    provideTranslateService({
      loader: {
        provide: TranslateLoader,
        useFactory: HttpLoaderFactory,
        deps: [HttpClient],
      },
      missingTranslationHandler: {
        provide: MissingTranslationHandler,
        useClass: MissingTranslationHelper,
      },
    }),
    provideAppInitializer(initTranslations),
    provideServiceWorker('ngsw-worker.js', {
      enabled: !isDevMode(),
      // Register the ServiceWorker as soon as the application is stable
      // or after 30 seconds (whichever comes first).
      registrationStrategy: 'registerWhenStable:30000',
    }),
  ],
};
