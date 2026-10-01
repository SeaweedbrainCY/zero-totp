import { inject } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { MissingTranslationHandler, MissingTranslationHandlerParams, TranslateService } from "@ngx-translate/core";
import { TranslateHttpLoader } from "@ngx-translate/http-loader";
import defaultLanguage from "../../assets/i18n/en-uk.json";
import FrenchLanguage from "../../assets/i18n/fr-fr.json";

export function HttpLoaderFactory(http: HttpClient) {
  return new TranslateHttpLoader(http);
}

export class MissingTranslationHelper implements MissingTranslationHandler {
  handle(params: MissingTranslationHandlerParams) {
    return params.key;
  }
}

// Registered via provideAppInitializer (replaces the former AppModule constructor).
// Translations are bundled so the UI is translated on first render without an HTTP round-trip.
export function initTranslations(): void {
  const translate = inject(TranslateService);
  translate.addLangs(["fr-fr"]);
  translate.setTranslation("fr-fr", FrenchLanguage);
  translate.setTranslation("en-uk", defaultLanguage);
  translate.setDefaultLang("en-uk");
  if (localStorage.getItem("language") == null) {
    const browserLang = translate.getBrowserLang();
    if (browserLang == undefined) {
      localStorage.setItem("language", "en-uk");
      translate.use("en-uk");
    } else if (browserLang.match(/fr/)) {
      localStorage.setItem("language", "fr-fr");
      translate.use("fr-fr");
    } else {
      // default + en
      localStorage.setItem("language", "en-uk");
      translate.use("en-uk");
    }
  } else {
    if (localStorage.getItem("language") == "fr-fr") {
      translate.use("fr-fr");
    } else {
      // default + en
      translate.use("en-uk");
    }
  }
}
