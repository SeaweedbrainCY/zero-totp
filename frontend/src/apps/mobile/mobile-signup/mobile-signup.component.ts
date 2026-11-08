import { Component, signal } from '@angular/core';
import { SignupSharedComponent } from 'src/shared/Component/signup/signup.component';
import { MobileZeroTotpTenantSelectorComponent } from '../mobile-zero-totp-tenant-selector/mobile-zero-totp-tenant-selector.component';

@Component({
  selector: 'app-mobile-signup',
  imports: [SignupSharedComponent, MobileZeroTotpTenantSelectorComponent],
  templateUrl: './mobile-signup.component.html',
  styleUrl: './mobile-signup.component.css',
})
export class MobileSignupComponent {



}
