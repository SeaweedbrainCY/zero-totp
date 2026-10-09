import { Component, OnInit, signal, ChangeDetectionStrategy } from '@angular/core';
import { faEnvelope, faLock, faCheck, faXmark, faFlagCheckered, faCloudArrowUp, faBriefcaseMedical, faEye, faEyeSlash, faKey, faCircleNotch, faCircleQuestion, faPen, faShieldHalved, faGlobe, faLink, faCircleInfo, faArrowRight, faFingerprint } from '@fortawesome/free-solid-svg-icons';
import { HttpClient } from '@angular/common/http';
import { environment } from 'src/environments/environment';
import { Router, ActivatedRoute } from '@angular/router';
import { UserService } from '../../../shared/Services/User/user.service';
import { Crypto } from '../../../shared/Crypto/crypto';
import { AuthServiceService, AuthToken } from '../services/AuthService/auth-service.service';
import { LocalVaultV1Service, UploadVaultStatus } from '../../../shared/Services/upload-vault/LocalVaultv1Service.service';
import { isDeviceMobile } from '../../../shared/Utils/utils';
import { VaultService } from '../../../shared/Services/VaultService/vault.service';
import { ApiService } from '../services/API/api.service';
import { ToastService } from '../../../shared/Services/Toast/toast.service';
import { TranslateService, TranslatePipe } from '@ngx-translate/core';
import { CapacitorPersistentStorageService } from '../services/Capacitor/persistentStorage/capacitor-persistent-storage.service';
import { ProtectedKeychainStorageService } from '../services/Capacitor/ProtectedKeychainStorage/protected-keychain-storage.service';
import { DisplayPreferencesService } from '../services/DisplayPreferences/display-preferences.service';
import { FormsModule } from '@angular/forms';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';
import { NgClass } from '@angular/common';
@Component({
    selector: 'app-login',
    templateUrl: './login.component.html',
    styleUrls: ['./login.component.css'],
    changeDetection: ChangeDetectionStrategy.OnPush,
    imports: [
        FormsModule,
        FaIconComponent,
        NgClass,
        TranslatePipe,
    ],
})
export class LoginComponent implements OnInit {
  faEnvelope = faEnvelope;
  faLock = faLock;
  faArrowRight = faArrowRight;
  faFingerprint = faFingerprint;
  faCheck = faCheck;
  faCircleInfo = faCircleInfo;
  faLink = faLink;
  faShieldHalved = faShieldHalved;
  faGlobe = faGlobe;
  faCircleQuestion = faCircleQuestion;
  faXmark = faXmark;
  faCircleNotch = faCircleNotch;
  faKey = faKey;
  faFlagCheckered = faFlagCheckered;
  faCloudArrowUp = faCloudArrowUp;
  faEye = faEye;
  faEyeSlash = faEyeSlash;
  faBriefcaseMedical = faBriefcaseMedical;
  faPen = faPen;
  environment = environment

  // Read in template — signals
  email = signal("");
  password = signal("");
  isLoading = signal(false);
  warning_message = signal("");
  warning_message_color = signal("is-warning");
  isPassphraseModalActive = signal(false);
  is_oauth_flow = signal(false);
  login_button = signal("login.open_button");
  isPassphraseVisible = signal(false);
  remember = signal(false);
  current_domain = signal("");
  instance_dropdown_active = signal(false);
  instance_modal_active = signal(false)
  instance_modal_error = signal("")
  instance_modal_loading = signal(false)
  instance_modal_apiBaseURL_input = signal(this.apiService.baseURL)
  biometric_protection_preference_modal_is_active = signal(false)
  biometric_protection_preference_modal_buttons_are_active = signal(true)

  // Not read in template — plain properties
  hashedPassword: string = "";
  error_param: string | null = null;

  // Pass to html template
  protected isDeviceMobile = isDeviceMobile

  constructor(
    private http: HttpClient,
    private router: Router,
    private route: ActivatedRoute,
    private userService: UserService,
    private crypto: Crypto,
    private translate: TranslateService,
    private toast: ToastService,
    private vaultService: VaultService,
    private apiService: ApiService,
    private persistentStorage: CapacitorPersistentStorageService,
    private authService: AuthServiceService,
    private secureProtectedStorage: ProtectedKeychainStorageService,
    public displayPreferences: DisplayPreferencesService
  ) {
  }


  ngOnInit() {
    if (this.userService.isUserLoggedIn()) {
      // If logged in redirect to /vault
      this.router.navigate(["/vault"], { relativeTo: this.route.root });
    }
    this.error_param = this.route.snapshot.paramMap.get('error_param')
    switch (this.error_param) {
      case null: {
        break;
      }
      case 'sessionKilled': {
        this.warning_message.set('login.errors.session_killed');
        this.email.set(this.userService.email() || "");
        this.userService.clear();
        break;
      }
      case 'sessionTimeout': {
        this.warning_message.set('login.errors.session_timeout');
        this.email.set(this.userService.email() || "");
        this.userService.clear();
        break;
      }

      case 'sessionEnd': {
        this.warning_message.set('login.errors.session_end');
        this.email.set(this.userService.email() || "");
        break;
      }
      case 'oauth': {
        this.warning_message.set('login.errors.oauth');
        this.email.set(this.userService.email() || "");
        this.warning_message_color.set("is-success");
        this.userService.clear();
        this.is_oauth_flow.set(true);
        this.login_button.set("login.authorize");
        this.get_user_email_oauth_flow();
        break;
      }
      case 'confirmPassphrase': {
        this.warning_message.set('login.errors.confirm_passphrase');
        this.email.set(this.userService.email() || "");
        this.warning_message_color.set("is-success");
        this.userService.clear();
        this.is_oauth_flow.set(true);
        break;
      }
    }
    if (localStorage.getItem("r_email") != null) {
      this.email.set(localStorage.getItem("r_email")!);
      this.remember.set(true);
    }
    if (environment.isMobileApp) {
      // Mobile app, current domain is the one of the API
      const baseURL = new URL(this.apiService.baseURL)
      this.current_domain.set(baseURL.host)
    } else {
      // webapp we use the current location
      this.current_domain.set(window.location.host);
    }
  }


  checkEmail(): boolean {
    const emailRegex = /\S+@\S+\.\S+/;
    if (!emailRegex.test(this.email())) {
      this.translate.get("login.errors.email").subscribe((translation) => {
        this.toast.error(translation);
      });
      return false;
    } else {
      return true;
    }
  }

  get_user_email_oauth_flow() {
    this.http.get(this.apiService.baseURL + "/api/v1/whoami", { withCredentials: true, observe: 'response' }).subscribe({
      next: (response) => {
        const data = JSON.parse(JSON.stringify(response.body))
        this.email.set(data.email);
      },
      error: (error) => {
        this.translate.get("login.errors.no_session").subscribe((translation) => {
          this.toast.error(translation);
          this.router.navigate(["/login/sessionEnd"], { relativeTo: this.route.root });
        });
      }
    });
  }


  login() {
    if (this.email() == "" || this.password() == "") {
      this.translate.get("login.errors.empty").subscribe((translation) => {
        this.toast.error(translation);
      });
      return;
    }
    if (!this.checkEmail()) {
      return;
    }
    this.isLoading.set(true);
    this.hashPassword()

  }



  // DEPRECATED.
  // userService pre-hashed
  hashPassword() {
    this.http.get(this.apiService.baseURL + "/api/v1/login/specs?username=" + encodeURIComponent(this.email()), { withCredentials: true, observe: 'response' }).subscribe({
      next: (response) => {

        try {
          const data = JSON.parse(JSON.stringify(response.body))
          const salt = data.passphrase_salt
          this.crypto.hashPassphrase(this.password(), salt).then(hashed => {
            if (hashed != null) {
              this.hashedPassword = hashed;
              this.userService.passphraseSalt.set(salt);
              this.postLoginRequest();
            } else {
              this.translate.get("login.errors.hashing").subscribe((translation) => {
                this.toast.error(translation)
              });
              this.isLoading.set(false);
            }
          });
        } catch {
          this.translate.get("login.errors.hashing").subscribe((translation) => {
            this.toast.error(translation)
          });
          this.isLoading.set(false);
        }
      }, error: error => {
        if (error.status == 429) {
          const ban_time = error.error.ban_time || "few";
          this.translate.get("login.errors.rate_limited", { time: String(ban_time) }).subscribe((translation) => {
            this.toast.error(translation)
          });
        } else {
          this.translate.get("login.errors.no_connection").subscribe((translation) => {
            this.toast.error(translation)
          });
        }
        this.isLoading.set(false);
      }
    });
  }



  postLoginRequest() {
    const data = {
      email: this.email(),
      password: this.hashedPassword
    }
    this.http.post<{ id: number | undefined, isVerified: boolean, username: string | undefined, derivedKeySalt: string | undefined, role: string | undefined, isGoogleDriveSync: boolean | undefined, session_token: string | undefined, refresh_token: string | undefined }>(this.apiService.baseURL + "/api/v1/login", data, { withCredentials: true, observe: 'response' }).subscribe({
      next: (response) => {
        try {
          this.userService.id.set(response.body!.id!);
          this.userService.email.set(this.email());
          if (!response.body!.isVerified) {
            this.router.navigate(["/emailVerification"], { relativeTo: this.route.root });
            return;
          }


          this.userService.derivedKeySalt.set(response.body!.derivedKeySalt!);
          if (environment.isMobileApp && response.body!.session_token != undefined && response.body!.refresh_token != undefined) {
            const domain = new URL(this.apiService.baseURL).host
            if (domain == undefined) {
              console.log(this.apiService.baseURL + " gives an undefined host")
            } else {

              const authToken: AuthToken = {
                domain,
                session_token: response.body!.session_token,
                refresh_token: response.body!.refresh_token,
              }
              this.authService.setToken(authToken).catch((error) => {
                console.log("Failed to save auth token:", error)
              });
            }
          }
          this.userService.googleDriveSync.set(response.body!.isGoogleDriveSync!);
          this.final_zke_flow();
        } catch (e) {
          this.isLoading.set(false);
          console.log(e);
          this.translate.get("login.errors.server_error").subscribe((translation) => {
            this.toast.error(translation)
          });
        }

      },
      error: (error) => {
        console.log(error);
        console.log(error.error.message)
        this.isLoading.set(false);
        if (error.status == 429) {
          const ban_time = error.error.ban_time || "few";
          this.translate.get("login.errors.rate_limited", { time: String(ban_time) }).subscribe((translation) => {
            this.toast.error(translation)
          });
        } else if (error.error.message == "blocked") {
          this.translate.get("login.errors.account_blocked").subscribe((translation) => {
            this.toast.error(translation)
          });
        } else if (error.error.message == "generic_errors.invalid_creds") {
          this.translate.get(error.error.message).subscribe((translation) => {
            this.toast.error(translation)
          });
        } else {
          this.translate.get("generic_errors.error").subscribe((translation) => {
            let message = translation + " : " + error.status + " " + error.statusText + ". " + (error.error.message);
            this.toast.error(message)
          });
        }

      }
    });
  }

  final_zke_flow() {
    this.userService.derivePassphrase(this.userService.derivedKeySalt()!, this.password()).then((derivedKey) => {
      this.getZKEKey().then((zke_key_encrypted) => {
        this.userService.decryptZKEKey(zke_key_encrypted, derivedKey, this.userService.isVaultLocal()!).then((zke_key) => {
          this.userService.zke_key.set(zke_key!);
          if (this.is_oauth_flow()) {
            this.router.navigate(["/oauth/synchronize"], { relativeTo: this.route.root });
          } else {
            if (this.remember()) {
              localStorage.setItem("r_email", this.email());
            } else {
              localStorage.removeItem("r_email");
            }
            this.toast.clear();
            if (this.environment.isMobileApp) {
              this.persistentStorage.isBiometricsProtectionEnabled(this.userService.id()!).then((isBiometricsProtectionEnabled) => {
                switch (isBiometricsProtectionEnabled) {
                  case null:
                    this.biometric_protection_preference_modal_is_active.set(true)
                    break
                  case true:
                    this.secureProtectedStorage.storeZKEKey(zke_key!)
                    this.toast.success(this.translate.instant("login.success"))
                    this.router.navigate(["/vault"], { relativeTo: this.route.root });
                    break;
                  default:
                    this.toast.success(this.translate.instant("login.success"))
                    this.router.navigate(["/vault"], { relativeTo: this.route.root });
                    break;
                }
              })
            } else {
              // not a mobile app
              this.toast.success(this.translate.instant("login.success"))
              this.router.navigate(["/vault"], { relativeTo: this.route.root });
            }

          }
        }, (error) => {
          this.toast.error(error)
          this.isLoading.set(false);
        });
      }, (error) => {
        this.toast.error(error)
        this.isLoading.set(false);
      });
    }, (error) => {
      this.toast.error(error)
      this.isLoading.set(false);
    });
  }


  getZKEKey(): Promise<string> {
    return new Promise((resolve, reject) => {
      this.http.get(this.apiService.baseURL + "/api/v1/zke_encrypted_key", { withCredentials: true, observe: 'response' }).subscribe((response) => {
        const data = JSON.parse(JSON.stringify(response.body))
        const zke_key_encrypted = data.zke_encrypted_key
        resolve(zke_key_encrypted);
      }, (error) => {
        reject("Impossible to retrieve your encryption key. Please try again later. " + error.error.error);
      });
    });

  }

  zero_totp_instance_button_click() {
    if (environment.isMobileApp) {
      this.instance_modal_active.update(v => !v);
    } else {
      // Webapp consulted on a mobile
      if (isDeviceMobile()) {
        // On nonMobileDevice, it's just hoverable
        this.instance_dropdown_active.update(v => !v);
      }
    }
  }

  validateNewAPIBaseURL() {
    this.instance_modal_error.set("")
    this.instance_modal_loading.set(true)
    console.log(this.instance_modal_apiBaseURL_input())
    this.persistentStorage.setAPIBaseURL(this.instance_modal_apiBaseURL_input()).then(_ => {
      this.apiService.updateBaseURL().then(success => {
        this.instance_modal_loading.set(false)
        if (success) {
          this.instance_modal_active.set(false)
          const baseURL = new URL(this.apiService.baseURL)
          this.current_domain.set(baseURL.host)
        } else {
          this.translate.get("general_error").subscribe(t => {
            this.instance_modal_error.set(t)
          })
        }
      })
    }).catch(error => {
      console.log(error)
      this.translate.get("invalid_url").subscribe(t => {
        this.instance_modal_error.set(t)
      })
    })
  }

  mobileUseBiometrics() {
    this.biometric_protection_preference_modal_buttons_are_active.set(false)
    this.persistentStorage.setBriometricProtection(this.userService.id()!, true).then(() => {
      this.secureProtectedStorage.storeZKEKey(this.userService.zke_key()!).then(() => {
        this.biometric_protection_preference_modal_buttons_are_active.set(true)
        this.biometric_protection_preference_modal_is_active.set(false)
        this.toast.success(this.translate.instant("login.success"))
        this.router.navigate(["/vault"], { relativeTo: this.route.root });
      })
    })
  }

  mobileDontUseBiometrics() {
    this.biometric_protection_preference_modal_buttons_are_active.set(false)
    this.persistentStorage.setBriometricProtection(this.userService.id()!, false).then(() => {
      this.biometric_protection_preference_modal_buttons_are_active.set(true)
      this.biometric_protection_preference_modal_is_active.set(false)
      this.toast.success(this.translate.instant("login.success"))
      this.router.navigate(["/vault"], { relativeTo: this.route.root });
    })
  }
}
