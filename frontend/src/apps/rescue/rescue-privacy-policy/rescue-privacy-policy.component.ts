import { Component, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { map } from 'rxjs';
import { RescuePrivacyPolicyEnComponent } from '../rescue-privacy-policy-en/rescue-privacy-policy-en.component';
import { RescuePrivacyPolicyFrComponent } from '../rescue-privacy-policy-fr/rescue-privacy-policy-fr.component';
import { TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-rescue-privacy-policy',
  imports: [
    RescuePrivacyPolicyEnComponent,
    RescuePrivacyPolicyFrComponent
  ],
  templateUrl: './rescue-privacy-policy.component.html',
  styleUrl: './rescue-privacy-policy.component.css',
})
export class RescuePrivacyPolicyComponent {
  // DI
  translate = inject(TranslateService);

  // Follows the language selector live
  currentLang = toSignal(
    this.translate.onLangChange.pipe(map(event => event.lang)),
    { initialValue: this.translate.getCurrentLang() || 'en-uk' }
  );
}
