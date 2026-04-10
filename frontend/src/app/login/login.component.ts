import { Component, OnInit, signal, ChangeDetectionStrategy } from '@angular/core';
import { faEnvelope, faLock, faCheck, faXmark, faFlagCheckered, faCloudArrowUp, faBriefcaseMedical, faEye, faEyeSlash, faKey, faCircleNotch, faCircleQuestion } from '@fortawesome/free-solid-svg-icons';
import { HttpClient } from '@angular/common/http';

import { Router, ActivatedRoute } from '@angular/router';
import { UserService } from '../services/User/user.service';
import { Crypto } from '../common/Crypto/crypto';
import { Buffer } from 'buffer';
import { LocalVaultV1Service, UploadVaultStatus } from '../services/upload-vault/LocalVaultv1Service.service';
import { Utils } from '../common/Utils/utils';
import { VaultService } from '../services/VaultService/vault.service';

import { ToastrService } from 'ngx-toastr';
import { TranslateService } from '@ngx-translate/core';
@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css'],
  standalone: false,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LoginComponent implements OnInit {
  faEnvelope = faEnvelope;
  faLock = faLock;
  faCheck = faCheck;
  faCircleQuestion = faCircleQuestion;
  faXmark = faXmark;
  faCircleNotch = faCircleNotch;
  faKey = faKey;
  faFlagCheckered = faFlagCheckered;
  faCloudArrowUp = faCloudArrowUp;
  faEye = faEye;
  faEyeSlash = faEyeSlash;
  faBriefcaseMedical = faBriefcaseMedical;

  // Read in template — signals
  email = signal("");
  password = signal("");
  isLoading = signal(false);
  warning_message = signal("");
  warning_message_color = signal("is-warning");
  isUnsecureVaultModaleActive = signal(false);
  isPassphraseModalActive = signal(false);
  is_oauth_flow = signal(false);
  login_button = signal("login.open_button");
  isPassphraseVisible = signal(false);
  isLocalVaultPassphraseVisible = signal(false);
  remember = signal(false);
  loading_file = signal(false);
  current_domain = signal("");
  instance_dropdown_active = signal(false);

  // Not read in template — plain properties
  hashedPassword: string = "";
  error_param: string | null = null;
  local_vault_service: LocalVaultV1Service | null = null;
  api_public_key: string | undefined = undefined;

  constructor(
    private http: HttpClient,
    private router: Router,
    private route: ActivatedRoute,
    private userService: UserService,
    private crypto: Crypto,
    private localVaultv1: LocalVaultV1Service,
    private translate: TranslateService,
    private toastr: ToastrService,
    public utils: Utils,
    private vaultService: VaultService
  ) {
  }


  ngOnInit() {
    this.error_param = this.route.snapshot.paramMap.get('error_param')
    switch (this.error_param) {
      case null: {
        break;
      }
      case 'sessionKilled': {
        this.warning_message.set('login.errors.session_killed');
        this.email.set(this.userService.getEmail() || "");
        this.userService.clear();
        break;
      }
      case 'sessionTimeout': {
        this.warning_message.set('login.errors.session_timeout');
        this.email.set(this.userService.getEmail() || "");
        this.userService.clear();
        break;
      }

      case 'sessionEnd': {
        this.warning_message.set('login.errors.session_end');
        this.email.set(this.userService.getEmail() || "");
        break;
      }
      case 'oauth': {
        this.warning_message.set('login.errors.oauth');
        this.email.set(this.userService.getEmail() || "");
        this.warning_message_color.set("is-success");
        this.userService.clear();
        this.is_oauth_flow.set(true);
        this.login_button.set("login.authorize");
        this.get_user_email_oauth_flow();
        break;
      }
      case 'confirmPassphrase': {
        this.warning_message.set('login.errors.confirm_passphrase');
        this.email.set(this.userService.getEmail() || "");
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

    this.current_domain.set(window.location.host);

  }


  checkEmail(): boolean {
    const emailRegex = /\S+@\S+\.\S+/;
    if (!emailRegex.test(this.email())) {
      this.translate.get("login.errors.email").subscribe((translation) => {
        this.utils.toastError(this.toastr, translation, "");
      });
      return false;
    } else {
      return true;
    }
  }

  get_user_email_oauth_flow() {
    this.http.get("/api/v1/whoami", { withCredentials: true, observe: 'response' }).subscribe({
      next: (response) => {
      const data = JSON.parse(JSON.stringify(response.body))
      this.email.set(data.email);
    }, 
    error: (error) => {
      this.translate.get("login.errors.no_session").subscribe((translation) => {
        this.utils.toastError(this.toastr, translation, "");
        this.router.navigate(["/login/sessionEnd"], { relativeTo: this.route.root });
      });
    }});
  }


  login() {
    if (this.email() == "" || this.password() == "") {
      this.translate.get("login.errors.empty").subscribe((translation) => {
        this.utils.toastError(this.toastr, translation, "");
      });
      return;
    }
    if (!this.checkEmail()) {
      return;
    }
    this.isLoading.set(true);
    this.hashPassword()

  }

  openVaultV1(event: any, unsecure_context: string, input: any) {
    this.local_vault_service!.parseUploadedVault(unsecure_context, this.api_public_key).then((vault_parsing_status) => {
      switch (vault_parsing_status) {
        case UploadVaultStatus.SUCCESS: {
          this.isPassphraseModalActive.set(true);
          this.loading_file.set(false);
          break
        }
        case UploadVaultStatus.INVALID_JSON: {
          this.translate.get("login.errors.import_vault.invalid_type").subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "");
          });
          this.loading_file.set(false);
          break;
        }

        case UploadVaultStatus.INVALID_VERSION: {
          this.translate.get("login.errors.import_vault.invalid_version").subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "");
          });
          this.loading_file.set(false);
          break;
        }
        case UploadVaultStatus.NO_SIGNATURE: {
          this.translate.get("login.errors.import_vault.no_signature").subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "")
          });
          this.loading_file.set(false);
          break;
        }
        case UploadVaultStatus.INVALID_SIGNATURE: {
          this.isUnsecureVaultModaleActive.set(true);
          this.loading_file.set(false);
          break;
        }
        case UploadVaultStatus.MISSING_ARGUMENT: {
          this.translate.get("login.errors.import_vault.missing_arg").subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "")
          });
          this.loading_file.set(false);
          break;
        }
        case UploadVaultStatus.INVALID_ARGUMENT: {
          this.translate.get("login.errors.import_vault.invalid_arg").subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "")
          });
          this.loading_file.set(false);
          break;
        }

        case UploadVaultStatus.UNKNOWN: {
          this.translate.get("login.errors.import_vault.error_unknown").subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "")
          });
          this.loading_file.set(false);
          break;
        }

        default: {
          this.translate.get("login.errors.import_vault.error_unknown").subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "")
          });
          this.loading_file.set(false);
          break;
        }
      }
    });
  }

  openFile(event: any): void {
    this.loading_file.set(true);
    const input = event.target;
    const reader = new FileReader();
    reader.readAsText(input.files[0], 'utf-8');
    reader.onload = (() => {
      if (reader.result) {
        try {
          const unsecure_context = reader.result.toString();
          const version = this.localVaultv1.extract_version_from_vault(unsecure_context);
          if (version == null) {
            this.translate.get("login.errors.import_vault.invalid_file").subscribe((translation) => {
              this.utils.toastError(this.toastr, translation, "");
            });
            this.loading_file.set(false);

          } else if (version == 1) {
            this.local_vault_service = this.localVaultv1
            this.http.get("/api/v1/vault/signature/public-key", { withCredentials: true, observe: 'response' }).subscribe({
              next: (response) => {
                const data = JSON.parse(JSON.stringify(response.body))
                this.api_public_key = data.public_key;
                this.openVaultV1(event, unsecure_context, input);
              },
              error: (error) => {
                console.log(error);
                this.loading_file.set(false);
                this.openVaultV1(event, unsecure_context, input);
              }
            });
          }
          else {
            this.translate.get("login.errors.import_vault.invalid_version").subscribe((translation) => {
              this.utils.toastError(this.toastr, translation, "")
            });
            this.loading_file.set(false);
          }
        } catch (e) {
          this.translate.get("login.errors.import_vault.parse_fail").subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "")
          });
          this.loading_file.set(false);
        }
      } else {
        this.translate.get("login.errors.import_vault.parse_fail").subscribe((translation) => {
          this.utils.toastError(this.toastr, translation, "")
        });
        this.loading_file.set(false);
      }
    });
    reader.onerror = (() => {
      this.loading_file.set(false);
    });
  }


  openLocalVault() {
    this.userService.clear();
    this.userService.setVaultLocal(true);
    this.userService.setLocalVaultService(this.local_vault_service!);
    this.userService.setDerivedKeySalt(this.local_vault_service!.get_derived_key_salt()!);
    this.vaultService.derivePassphrase(this.userService.getDerivedKeySalt()!, this.password()).then((derivedKey) => {
      this.vaultService.decryptZKEKey(this.local_vault_service!.get_zke_key_enc()!, derivedKey, this.userService.getIsVaultLocal()!).then((zke_key) => {
        this.userService.set_zke_key(zke_key!);
        this.router.navigate(["/vault"], { relativeTo: this.route.root });
      }, (error) => {
        this.utils.toastError(this.toastr, error, "")
        this.isLoading.set(false);
      });
    }, (error) => {
      this.utils.toastError(this.toastr, error, "")
      this.isLoading.set(false);
    });
  }

  hashPassword() {
    this.http.get("/api/v1/login/specs?username=" + encodeURIComponent(this.email()), { withCredentials: true, observe: 'response' }).subscribe({
      next: (response) => {

      try {
        const data = JSON.parse(JSON.stringify(response.body))
        const salt = data.passphrase_salt
        this.crypto.hashPassphrase(this.password(), salt).then(hashed => {
          if (hashed != null) {
            this.hashedPassword = hashed;
            this.userService.setPassphraseSalt(salt);
            this.postLoginRequest();
          } else {
            this.translate.get("login.errors.hashing").subscribe((translation) => {
              this.utils.toastError(this.toastr, translation, "")
            });
            this.isLoading.set(false);
          }
        });
      } catch {
        this.translate.get("login.errors.hashing").subscribe((translation) => {
          this.utils.toastError(this.toastr, translation, "")
        });
        this.isLoading.set(false);
      }
    }, error: error => {
      if (error.status == 429) {
        const ban_time = error.error.ban_time || "few";
        this.translate.get("login.errors.rate_limited", { time: String(ban_time) }).subscribe((translation) => {
          this.utils.toastError(this.toastr, translation, "")
        });
      } else {
        this.translate.get("login.errors.no_connection").subscribe((translation) => {
          this.utils.toastError(this.toastr, translation, "")
        });
      }
      this.isLoading.set(false);
    }});
  }


  postLoginRequest() {
    const data = {
      email: this.email(),
      password: this.hashedPassword
    }
    this.http.post("/api/v1/login", data, { withCredentials: true, observe: 'response' }).subscribe({
      next: (response) => {
      try {
        const data = JSON.parse(JSON.stringify(response.body))
        this.userService.setId(data.id);
        this.userService.setEmail(this.email());
        this.userService.setDerivedKeySalt(data.derivedKeySalt);
        if (data.isVerified == false) {
          this.router.navigate(["/emailVerification"], { relativeTo: this.route.root });
        } else {

          this.userService.setGoogleDriveSync(data.isGoogleDriveSync);
          this.final_zke_flow();
        }
      } catch (e) {
        this.isLoading.set(false);
        console.log(e);
        this.translate.get("login.errors.server_error").subscribe((translation) => {
          this.utils.toastError(this.toastr, translation, "")
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
            this.utils.toastError(this.toastr, translation, "")
          });
        } else if (error.error.message == "blocked") {
          this.translate.get("login.errors.account_blocked").subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "")
          });
        } else if (error.error.message == "generic_errors.invalid_creds") {
          this.translate.get(error.error.message).subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "")
          });
        } else {
          this.translate.get("generic_errors.error").subscribe((translation) => {
            let message = translation + " : " + error.status + " " + error.statusText + ". " + (error.error.message);
            this.utils.toastError(this.toastr, message, "")
          });
        }

      }});
  }

  final_zke_flow() {
    this.vaultService.derivePassphrase(this.userService.getDerivedKeySalt()!, this.password()).then((derivedKey) => {
      this.getZKEKey().then((zke_key_encrypted) => {
        this.vaultService.decryptZKEKey(zke_key_encrypted, derivedKey, this.userService.getIsVaultLocal()!).then((zke_key) => {
          this.userService.set_zke_key(zke_key!);
          if (this.is_oauth_flow()) {
            this.router.navigate(["/oauth/synchronize"], { relativeTo: this.route.root });
          } else {
            if (this.remember()) {
              localStorage.setItem("r_email", this.email());
            } else {
              localStorage.removeItem("r_email");
            }
            this.toastr.clear();
            this.utils.toastSuccess(this.toastr, this.translate.instant("login.success"), "")
            this.router.navigate(["/vault"], { relativeTo: this.route.root });
          }
        }, (error) => {
          this.utils.toastError(this.toastr, error, "")
          this.isLoading.set(false);
        });
      }, (error) => {
        this.utils.toastError(this.toastr, error, "")
        this.isLoading.set(false);
      });
    }, (error) => {
      this.utils.toastError(this.toastr, error, "")
      this.isLoading.set(false);
    });
  }


  getZKEKey(): Promise<string> {
    return new Promise((resolve, reject) => {
      this.http.get("/api/v1/zke_encrypted_key", { withCredentials: true, observe: 'response' }).subscribe((response) => {
        const data = JSON.parse(JSON.stringify(response.body))
        const zke_key_encrypted = data.zke_encrypted_key
        resolve(zke_key_encrypted);
      }, (error) => {
        reject("Impossible to retrieve your encryption key. Please try again later. " + error.error.error);
      });
    });

  }

  zero_totp_instance_button_click() {
    if(this.utils.isDeviceMobile()){
      this.instance_dropdown_active.update(v => !v);
    }
  }


}