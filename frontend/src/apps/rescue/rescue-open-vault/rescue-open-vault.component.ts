import { NgClass } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, signal, OnInit } from '@angular/core';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import { ToastService } from 'src/shared/Services/Toast/toast.service';
import { UserService } from 'src/shared/Services/User/user.service';
import { LocalVaultV1Service, UploadVaultStatus } from 'src/shared/Services/upload-vault/LocalVaultv1Service.service';
import { Router } from '@angular/router';
import { faCheckDouble, faCircleUp, faCloudArrowUp, faExternalLinkAlt, faEye, faEyeSlash, faFire, faKey, faPersonDigging } from '@fortawesome/free-solid-svg-icons';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-rescue-open-vault',
  imports: [
    TranslatePipe,
    NgClass,
    FaIconComponent,
    FormsModule
  ],
  templateUrl: './rescue-open-vault.component.html',
  styleUrl: './rescue-open-vault.component.css',
})
export class RescueOpenVaultComponent implements OnInit {
  isPassphraseModalActive = signal(false)
  isLocalVaultPassphraseVisible = signal(false)
  loading_file = signal(false)
  local_vault_service: LocalVaultV1Service | null = null;
  zero_totp_issue = signal(false)
  zero_totp_maintenance = signal(false)
  zero_totp_back_online = signal(false)
  isUnsecureVaultModaleActive = signal(false)
  passphrase = signal("")

  // icons
  faEye = faEye
  faEyeSlash = faEyeSlash
  faKey = faKey
  faExternalLinkAlt = faExternalLinkAlt
  faCircleUp = faCircleUp
  faCloudArrowUp = faCloudArrowUp
  faCheckDouble = faCheckDouble
  faPersonDigging = faPersonDigging
  faFire = faFire


  constructor(
    private userService: UserService,
    private localVaultv1: LocalVaultV1Service,
    private translate: TranslateService,
    private http: HttpClient,
    private toast: ToastService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.get_zero_totp_uptime_status()
  }

  get_zero_totp_uptime_status(){
        this.http.get("https://status.zero-totp.com/status", {responseType: 'text', observe: 'response'}).subscribe({
          next: (response) => {
            const zero_totp_uptime_status = response.body!.trim();
            if(zero_totp_uptime_status == "issue"){
              this.zero_totp_issue.set(true);
            } else if (zero_totp_uptime_status == "maintenance"){
              this.zero_totp_maintenance.set(true);
            } else if (zero_totp_uptime_status == "backonline"){
              this.zero_totp_back_online.set(true);
            }
          },
          error: (error) => {
            console.log(error)
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
              this.toast.error(translation);
            });
            this.loading_file.set(false);

          } else if (version == 1) {
            this.local_vault_service = this.localVaultv1
            this.openVaultV1(event, unsecure_context, input);
          }
          else {
            this.translate.get("login.errors.import_vault.invalid_version").subscribe((translation) => {
              this.toast.error(translation)
            });
            this.loading_file.set(false);
          }
        } catch (e) {
          this.translate.get("login.errors.import_vault.parse_fail").subscribe((translation) => {
            this.toast.error(translation)
          });
          this.loading_file.set(false);
        }
      } else {
        this.translate.get("login.errors.import_vault.parse_fail").subscribe((translation) => {
          this.toast.error(translation)
        });
        this.loading_file.set(false);
      }
    });
    reader.onerror = (() => {
      this.loading_file.set(false);
    });
  }

  openVaultV1(event: any, unsecure_context: string, input: any) {
    this.local_vault_service!.parseUploadedVault(unsecure_context, undefined).then((vault_parsing_status) => {
      switch (vault_parsing_status) {
        case UploadVaultStatus.SUCCESS: {
          this.isPassphraseModalActive.set(true);
          this.loading_file.set(false);
          break
        }
        case UploadVaultStatus.INVALID_JSON: {
          this.translate.get("login.errors.import_vault.invalid_type").subscribe((translation) => {
            this.toast.error(translation);
          });
          this.loading_file.set(false);
          break;
        }

        case UploadVaultStatus.INVALID_VERSION: {
          this.translate.get("login.errors.import_vault.invalid_version").subscribe((translation) => {
            this.toast.error(translation);
          });
          this.loading_file.set(false);
          break;
        }
        case UploadVaultStatus.NO_SIGNATURE: {
          this.translate.get("login.errors.import_vault.no_signature").subscribe((translation) => {
            this.toast.error(translation)
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
            this.toast.error(translation)
          });
          this.loading_file.set(false);
          break;
        }
        case UploadVaultStatus.INVALID_ARGUMENT: {
          this.translate.get("login.errors.import_vault.invalid_arg").subscribe((translation) => {
            this.toast.error(translation)
          });
          this.loading_file.set(false);
          break;
        }

        case UploadVaultStatus.UNKNOWN: {
          this.translate.get("login.errors.import_vault.error_unknown").subscribe((translation) => {
            this.toast.error(translation)
          });
          this.loading_file.set(false);
          break;
        }

        default: {
          this.translate.get("login.errors.import_vault.error_unknown").subscribe((translation) => {
            this.toast.error(translation)
          });
          this.loading_file.set(false);
          break;
        }
      }
    });
  }


  openLocalVault() {
    this.userService.clear();
    this.userService.isVaultLocal.set(true);
    this.userService.local_vault_service.set(this.local_vault_service!);
    this.userService.derivedKeySalt.set(this.local_vault_service!.get_derived_key_salt()!);
    this.userService.derivePassphrase(this.userService.derivedKeySalt()!, this.passphrase()).then((derivedKey) => {
      this.userService.decryptZKEKey(this.local_vault_service!.get_zke_key_enc()!, derivedKey, this.userService.isVaultLocal()!).then((zke_key) => {
        this.userService.zke_key.set(zke_key!);
        this.router.navigate(["/vault"]);
      }, (error) => {
        this.toast.error(error)
      });
    }, (error) => {
      this.toast.error(error)
    });
  }


}
