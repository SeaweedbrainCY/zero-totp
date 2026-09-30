import { AppModule, HttpLoaderFactory, MissingTranslationHelper } from './app/app.module';
import { UserService } from './app/services/User/user.service';
import { DisplayPreferencesService } from './app/services/DisplayPreferences/display-preferences.service';
import { Utils } from './app/common/Utils/utils';
import { Crypto } from './app/common/Crypto/crypto';
import { QrCodeTOTP } from './app/services/qr-code-totp/qr-code-totp.service';
import { GlobalConfigurationService } from './app/services/GlobalConfiguration/global-configuration.service';
import { LocalVaultV1Service } from './app/services/upload-vault/LocalVaultv1Service.service';
import { provideMarkdown, MarkdownModule } from 'ngx-markdown';
import { provideHttpClient, HttpClient, withInterceptorsFromDi } from '@angular/common/http';
import { TranslateHttpLoader } from '@ngx-translate/http-loader';
import { httpInterceptorProviders } from './app/helpers/auth.interceptor';
import { provideZonelessChangeDetection, provideCheckNoChangesConfig, isDevMode, importProvidersFrom, provideAppInitializer } from '@angular/core';
import { BrowserModule, bootstrapApplication } from '@angular/platform-browser';
import { AppRoutingModule, routes } from './app/app-routing.module';
import { FormsModule } from '@angular/forms';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { ClipboardModule } from '@angular/cdk/clipboard';
import { withInMemoryScrolling, provideRouter } from '@angular/router';
import { ZXingScannerModule } from '@zxing/ngx-scanner';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { ToastrModule } from 'ngx-toastr';
import { NgIdleModule } from '@ng-idle/core';
import { TranslateModule, TranslateLoader, MissingTranslationHandler, MissingTranslationHandlerParams } from '@ngx-translate/core';
import { ServiceWorkerModule } from '@angular/service-worker';
import { AppComponent } from './app/app.component';
import { initTranslations } from './app/i18n';


bootstrapApplication(AppComponent, {
    providers: [
        importProvidersFrom(BrowserModule, AppRoutingModule, FormsModule, MarkdownModule.forRoot(), MarkdownModule.forChild(), FontAwesomeModule, ClipboardModule, ZXingScannerModule, BrowserAnimationsModule, ToastrModule.forRoot(), NgIdleModule.forRoot(), TranslateModule.forRoot({
            loader: {
                provide: TranslateLoader,
                useFactory: HttpLoaderFactory,
                deps: [HttpClient],
            },
            missingTranslationHandler: {
                provide: MissingTranslationHandler,
                useClass: MissingTranslationHelper,
            },
        }), ServiceWorkerModule.register("ngsw-worker.js", {
            enabled: !isDevMode(),
            // Register the ServiceWorker as soon as the application is stable
            // or after 30 seconds (whichever comes first).
            registrationStrategy: "registerWhenStable:30000",
        })),
        UserService,
        DisplayPreferencesService,
        Utils,
        Crypto,
        QrCodeTOTP,
        GlobalConfigurationService,
        LocalVaultV1Service,
        provideMarkdown(),
        provideHttpClient(),
        provideMarkdown({ loader: HttpClient }),
        httpInterceptorProviders,
        provideHttpClient(withInterceptorsFromDi()),
        provideZonelessChangeDetection(),
        provideCheckNoChangesConfig({ exhaustive: true, interval: 1000 }),
        provideRouter(routes, withInMemoryScrolling({ scrollPositionRestoration: "enabled" })),
        provideAppInitializer(initTranslations),
    ]
})
  .catch(err => console.error(err));
