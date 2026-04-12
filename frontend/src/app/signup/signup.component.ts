import { Component, OnInit, signal, ChangeDetectionStrategy } from '@angular/core';
import { faEnvelope, faKey, faCheck, faUser, faXmark, faFlagCheckered, faEye, faEyeSlash, faFlask, faCircleQuestion, faArrowUpRightFromSquare, faDoorClosed } from '@fortawesome/free-solid-svg-icons';
import { faDiscord } from '@fortawesome/free-brands-svg-icons';
import { HttpClient } from '@angular/common/http';

import { Utils } from '../common/Utils/utils';
import { Crypto } from '../common/Crypto/crypto';
import { ActivatedRoute, Router } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';
import { ToastrService } from 'ngx-toastr';
import { UserService } from '../services/User/user.service';


@Component({
    selector: 'app-signup',
    templateUrl: './signup.component.html',
    styleUrls: ['./signup.component.css'],
    standalone: false,
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class SignupComponent implements OnInit {
  // Icons (static, no need for signals)
  faEnvelope = faEnvelope;
  faKey = faKey;
  faDoorClosed = faDoorClosed;
  faCheck = faCheck;
  faUser = faUser;
  faArrowUpRightFromSquare = faArrowUpRightFromSquare;
  faDiscord = faDiscord;
  faCircleQuestion = faCircleQuestion;
  faXmark = faXmark;
  faFlagCheckered = faFlagCheckered;
  faEye = faEye;
  faEyeSlash = faEyeSlash;
  faFlask = faFlask;

  username = signal('');
  email = signal('');
  password = signal('');
  confirmPassword = signal('');
  hashed_password = signal('');
  terms = signal(false);
  isLoading = signal(false);
  emailErrorMessage = signal('');
  usernameErrorMessage = signal('');
  passwordErrorMessage = signal<string[]>(['']);
  isModalActive = signal(false);
  input = signal('');
  encryptedZKEkey = signal('');
  derivedKeySalt = signal('');
  passphraseSalt = signal('');
  beta = signal(true);
  isPasswordVisible = signal(false);
  isConfirmPasswordVisible = signal(false);
  current_domain = signal('');
  instance_dropdown_active = signal(false);
  signup_enabled = signal(true);

  constructor(
    private http: HttpClient,
    public utils: Utils,
    private crypto: Crypto,
    private router: Router,
    private route: ActivatedRoute,
    private translate: TranslateService,
    private toastr: ToastrService,
    private userService: UserService,
  ) {}

  ngOnInit(): void {
    this.current_domain.set(window.location.host);
    this.get_api_configuration();
  }

  checkPassword() {
    this.passwordErrorMessage.set(['']);
    const special = /[!@#$%^&*()_+\-=[\]{};:\\|,./?~]/;
    const upper = /[A-Z]/;
    const number = /[0-9]/;
    const pwd = this.password();
    const errors: string[] = [''];
    if (pwd.length < 12) {
      errors.push(this.translate.instant('signup.passphrase.error.char'));
    }
    if (!special.test(pwd)) {
      errors.push(this.translate.instant('signup.passphrase.error.special_char'));
    }
    if (!upper.test(pwd)) {
      errors.push(this.translate.instant('signup.passphrase.error.upper'));
    }
    if (!number.test(pwd)) {
      errors.push(this.translate.instant('signup.passphrase.error.number'));
    }
    if (pwd !== this.confirmPassword()) {
      errors.push(this.translate.instant('signup.passphrase.error.match'));
    }
    this.passwordErrorMessage.set(errors);
  }

  checkEmail() {
    const forbidden = /["'<>]/;
    this.emailErrorMessage.set('');
    if (this.email() === '') {
      this.emailErrorMessage.set(' ');
      return;
    }
    const emailRegex = /\S+@\S+\.\S+/;
    if (!emailRegex.test(this.email())) {
      this.emailErrorMessage.set(this.translate.instant('signup.email.error.invalid'));
      return;
    }
    if (forbidden.test(this.email())) {
      this.emailErrorMessage.set(this.translate.instant('signup.email.error.forbidden'));
      return;
    }
  }

  get_api_configuration() {
    this.http.get('/api/v1/configuration', { withCredentials: true }).subscribe({
      next: (response) => {
        const response_data = response as { signup_enabled: boolean };
        this.signup_enabled.set(response_data.signup_enabled);
        console.log('Signup enabled: ', this.signup_enabled());
      },
    });
  }

  checkUsername() {
    const forbidden = /["'<>]/;
    this.usernameErrorMessage.set('');
    if (this.username() === '') {
      this.usernameErrorMessage.set(' ');
      return;
    }
    if (forbidden.test(this.username())) {
      this.usernameErrorMessage.set(this.translate.instant('signup.username.error.forbidden'));
      return;
    }
  }

  signup() {
    this.closeModal();
    this.emailErrorMessage.set('');
    this.usernameErrorMessage.set('');
    this.passwordErrorMessage.set(['']);
    if (!this.terms()) {
      this.utils.toastError(this.toastr, this.translate.instant('signup.errors.terms'), '');
      return;
    }
    if (!this.beta()) {
      this.utils.toastError(this.toastr, this.translate.instant('signup.errors.beta'), '');
      return;
    }
    if (this.username() === '' || this.email() === '' || this.password() === '') {
      this.utils.toastError(this.toastr, this.translate.instant('signup.errors.missing_fields'), '');
      return;
    }
    this.checkPassword();
    this.checkEmail();
    this.checkUsername();
    if (this.emailErrorMessage() !== '' || this.passwordErrorMessage().length > 1 || this.usernameErrorMessage() !== '') {
      return;
    }
    this.isLoading.set(true);
    const ZKEkey = this.crypto.generateZKEKey();
    const randomSalt = this.crypto.generateRandomSalt();
    this.crypto.deriveKey(randomSalt, this.password()).then((key) => {
      this.crypto.encrypt(ZKEkey, key).then((encryptedZKEkey) => {
        this.encryptedZKEkey.set(encryptedZKEkey);
        this.derivedKeySalt.set(randomSalt);
        this.hashPassword();
      });
    });
  }

  hashPassword() {
    const passphraseSalt = this.crypto.generateRandomSalt();
    this.passphraseSalt.set(passphraseSalt);
    this.crypto.hashPassphrase(this.password(), passphraseSalt).then((hashed) => {
      if (hashed != null) {
        this.hashed_password.set(hashed);
        this.signupRequest();
      } else {
        this.utils.toastError(this.toastr, this.translate.instant('signup.errors.hashing'), '');
      }
    });
  }

  signupRequest() {
    const data = {
      username: this.username(),
      email: this.email(),
      password: this.hashed_password(),
      ZKE_key: this.encryptedZKEkey(),
      derivedKeySalt: this.derivedKeySalt(),
      passphraseSalt: this.passphraseSalt(),
    };

    this.http.post('/api/v1/signup', data, { withCredentials: true, observe: 'response' }).subscribe({
      next: (response) => {
        this.isLoading.set(false);
        this.utils.toastSuccess(this.toastr, this.translate.instant('signup.success'), '');
        this.userService.email.set(this.email());
        const response_data = response.body as { message: string; email_verification_required: boolean };
        if (response_data.email_verification_required) {
          this.router.navigate(['/emailVerification'], { relativeTo: this.route.root });
        } else {
          this.router.navigate(['/vault'], { relativeTo: this.route.root });
        }
      },
      error: (error) => {
        console.log(error);
        this.isLoading.set(false);
        if (error.status === 409) {
          this.utils.toastError(this.toastr, this.translate.instant('signup.errors.already_exist'), '');
        } else if (error.status === 403 && error.error != null && error.error.code != null && error.error.code === 'signup_disabled') {
          this.utils.toastError(this.toastr, this.translate.instant('signup.errors.disabled'), '');
        } else {
          let error_message = this.translate.instant('signup.errors.unknown');
          if (error.error != null && error.error.message != null) {
            error_message = error.error.message;
          }
          this.utils.toastError(this.toastr, 'Error : ' + error_message, '');
        }
      },
    });
  }

  openModal() {
    this.isModalActive.set(true);
  }

  closeModal() {
    this.isModalActive.set(false);
  }

  zero_totp_instance_button_click() {
    if (this.utils.isDeviceMobile()) {
      this.instance_dropdown_active.update(v => !v);
    }
  }
}