import { ApplicationConfig, isDevMode, provideAppInitializer, provideCheckNoChangesConfig, provideZonelessChangeDetection } from '@angular/core';
import { HttpClient, provideHttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { provideRouter, withInMemoryScrolling, withViewTransitions } from '@angular/router';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideServiceWorker } from '@angular/service-worker';
import { MissingTranslationHandler, TranslateLoader, provideTranslateService } from '@ngx-translate/core';
import { provideMarkdown } from 'ngx-markdown';
import { provideToastr } from 'ngx-toastr';
import { provideNgIdle } from '@ng-idle/core';
import {provideTranslateHttpLoader} from '@ngx-translate/http-loader';
import { routes } from './app.routes';
import { MissingTranslationHelper, initTranslations } from '../../shared/i18n';
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
    provideToastr({
      positionClass: 'toast-bottom-full-width',
      closeButton: true,
      progressBar: true,
      progressAnimation: 'decreasing',
      tapToDismiss: true,
    }),
    provideNgIdle(),
    provideMarkdown({ loader: HttpClient }),
    provideTranslateService({
      loader: provideTranslateHttpLoader({prefix:"../assets/i18n/", suffix:".json"}),
      missingTranslationHandler: {
        provide: MissingTranslationHandler,
        useClass: MissingTranslationHelper,
      },
      fallbackLang: "en-uk"
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
