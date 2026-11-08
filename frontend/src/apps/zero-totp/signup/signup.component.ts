import { Component, signal } from '@angular/core';
import { SignupSharedComponent } from 'src/shared/Component/signup/signup.component';
import { isDeviceMobile } from 'src/shared/Utils/utils';
import { ZeroTotpInstanceSelectorComponent } from '../zero-totp-instance-selector/zero-totp-instance-selector.component';

@Component({
  selector: 'app-signup',
  imports: [SignupSharedComponent, ZeroTotpInstanceSelectorComponent],
  templateUrl: './signup.component.html',
  styleUrl: './signup.component.css',
})
export class SignupComponent {

}
