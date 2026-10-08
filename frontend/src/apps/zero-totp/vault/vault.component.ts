import { Component, OnInit, signal, WritableSignal } from '@angular/core';
import { UserService } from '../../../shared/Services/User/user.service';
import { TOTPEntry } from '../../../shared/models/totp-entry';
import { ActivatedRoute, Router, NavigationEnd, RouterLink } from '@angular/router';
import { faPen, faSquarePlus, faCopy, faCheckCircle, faCircleXmark, faDownload, faDesktop, faRotateRight, faChevronUp, faChevronDown, faChevronRight, faLink, faCircleInfo, faUpload, faCircleNotch, faCircleExclamation, faCircleQuestion, faFlask, faMagnifyingGlass, faXmark, faFingerprint, faServer, faLock, faEye, faEyeSlash, faKey, faArrowUpRightFromSquare } from '@fortawesome/free-solid-svg-icons';
import { faGoogleDrive } from '@fortawesome/free-brands-svg-icons';
import { HttpClient } from '@angular/common/http';

import { Crypto } from '../../../shared/Crypto/crypto';
import { formatDate, NgClass } from '@angular/common';
import { TranslateService, TranslatePipe } from '@ngx-translate/core';
import { ToastService } from '../../../shared/Services/Toast/toast.service';
import { TOTP } from "totp-generator"
import { VaultService, DecryptedVaultResult } from '../../../shared/Services/VaultService/vault.service';
import { GlobalConfigurationService } from '../services/GlobalConfiguration/global-configuration.service';
import { ApiService } from '../services/API/api.service';
import { environment } from 'src/environments/environment';
import { ProtectedKeychainStorageService } from '../services/Capacitor/ProtectedKeychainStorage/protected-keychain-storage.service';
import { CapacitorPersistentStorageService } from '../services/Capacitor/persistentStorage/capacitor-persistent-storage.service';
import { FormsModule } from '@angular/forms';
import { VaultViewComponent } from 'src/shared/Views/vault-view/vault-view.component';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';


@Component({
    selector: 'app-vault',
    templateUrl: './vault.component.html',
    styleUrls: ['./vault.component.css'],
    imports: [FaIconComponent, FormsModule, NgClass, RouterLink, TranslatePipe, VaultViewComponent]
})
export class VaultComponent implements OnInit {
  // Fontawesome icons
  faPen = faPen;
  faSquarePlus = faSquarePlus;
  faCopy = faCopy;
  faFingerprint = faFingerprint;
  faArrowUpRightFromSquare = faArrowUpRightFromSquare;
  faKey = faKey;
  faEye = faEye;
  faEyeSlash = faEyeSlash;
  faGoogleDrive = faGoogleDrive;
  faLock = faLock;
  faServer = faServer;
  faCircleXmark = faCircleXmark;
  faCheckCircle = faCheckCircle;
  faRotateRight = faRotateRight;
  faCircleNotch = faCircleNotch;
  faMagnifyingGlass = faMagnifyingGlass;
  faXmark = faXmark;
  faFlask = faFlask;
  faDesktop = faDesktop;
  faCircleExclamation = faCircleExclamation;
  faDownload = faDownload;
  faChevronUp = faChevronUp;
  faChevronDown = faChevronDown;
  faChevronRight = faChevronRight;
  faLink = faLink;
  faCircleInfo = faCircleInfo;
  faCircleQuestion = faCircleQuestion;
  faUpload = faUpload;

  isGoogleDriveEnabled = true;
  passphrase = "";

  isDecryptingLockedVaut = false;
  currentURL = ""



  // Signals
  vaultDecryptionErrorMessage = signal("");
  google_drive_refresh_token_error_display_modal_active = signal(false);
  google_drive_refresh_token_error = signal(false);
  is_google_drive_enabled_on_this_tenant = signal(false);
  current_domain = signal("");
  google_drive_error_message = signal("");
  isVaultEncrypted: WritableSignal<boolean | undefined> = signal(undefined);
  isPassphraseVisible = signal(false);
  isGoogleDriveSync = signal("loading"); // uptodate, loading, error, false
  isVaultLoading = signal(false)
  storageOptionOpen = signal(false)
  page_title = signal("vault.title.main");
  vault_date: WritableSignal<string | undefined> = signal(undefined); // for local vault
  isRestoreBackupModaleActive = signal(false);
  lastBackupDate = signal("");
  faviconPolicy = signal("");
  totpCodesMap: WritableSignal<Map<string, string>> = signal(new Map<string, string>())
  searchBarValue = signal("")
  isBiometricProtectionEnabled = signal(false)



  constructor(
    public userService: UserService,
    private router: Router,
    private route: ActivatedRoute,
    private http: HttpClient,
    private translate: TranslateService,
    private toast: ToastService,
    private vaultService: VaultService,
    public globalConfigurationService: GlobalConfigurationService,
    private apiService: ApiService,
    private protectedKeychainStorageService: ProtectedKeychainStorageService,
    private capacitorPreferencesStorage: CapacitorPersistentStorageService
  ) {
    this.current_domain.set(window.location.host);
    router.events.subscribe((url: any) => {
      if (url instanceof NavigationEnd) {
        this.currentURL = url.url;
      }
    });

  }

  ngOnInit() {
    if (this.userService.zke_key() == null) {
      if (environment.isMobileApp) {
        this.capacitorPreferencesStorage.isBiometricsProtectionEnabled(this.userService.id()!).then((preference) => {
          if (preference == true) {
            this.isBiometricProtectionEnabled.set(true)
          }
        })

      }
      // User refreshed the page
      this.userService.refresh_user_id().then(() => {
        this.isVaultEncrypted.set(true);
      }, () => {
        this.isVaultEncrypted.set(false);
        this.router.navigate(["/login/sessionKilled"], { relativeTo: this.route.root });
      });

    } else {
      // User is logged in, can have vault in memory

      this.isVaultEncrypted.set(false);
      this.get_google_drive_option();
      this.get_preferences();
      if (this.userService.zke_key() == null || !this.userService.is_vault_in_memory) {
        this.refreshUserData()
      }
    }
  }



  mobileLoadZKEKeyFromKeychain() {
    this.protectedKeychainStorageService.getZKEKey().then((zke_key) => {
      this.userService.zke_key.set(zke_key)
      this.ngOnInit()
    },
      (error) => {
        console.log(error)
      })
  }








  // DEPRECATED: Should use user service's own utility
  getUserEncryptedVault(): Promise<Array<Map<string, string>>> {
    return new Promise<Array<Map<string, string>>>((resolve, reject) => {
      this.isVaultLoading.set(true)
      this.userService.vault_tags.set([]);
      this.http.get(this.apiService.baseURL + "/api/v1/all_secrets", { withCredentials: true, observe: 'response' }).subscribe({
        next: (response) => {
          const data = JSON.parse(JSON.stringify(response.body))
          let encrypted_secret_vault = new Array<Map<string, string>>();
          for (let secret of data.enc_secrets) {
            let secret_map = new Map<string, string>();
            secret_map.set("uuid", secret.uuid);
            secret_map.set("enc_secret", secret.enc_secret);
            encrypted_secret_vault.push(secret_map);
          }
          resolve(encrypted_secret_vault)
        },
        error: (error) => {
          this.isVaultLoading.set(true)
          if (error.status == 404) {
            this.userService.vault.set(new Map<string, TOTPEntry>());
            this.isVaultLoading.set(false)
          } else {
            let errorMessage = "";
            if (error.error.message != null) {
              errorMessage = error.error.message;
            } else if (error.error.detail != null) {
              errorMessage = error.error.detail;
            }
            if (error.status == 0) {
              errorMessage = "vault.error.server_unreachable"
            } else if (error.status == 401) {
              this.userService.clear();
              this.router.navigate(["/login/sessionEnd"], { relativeTo: this.route.root });
              return;
            }
            this.translate.get("vault.error.server").subscribe((translation: string) => {
              this.toast.error(translation + " " + this.translate.instant(errorMessage));
            });
          }
          reject(error)
        }
      });
    });
  }

  get_preferences() {
    this.http.get(this.apiService.baseURL + "/api/v1/preferences?fields=favicon_policy", { withCredentials: true, observe: 'response' }).subscribe({
      next: (response) => {
        if (response.body != null) {
          const data = JSON.parse(JSON.stringify(response.body));
          if (data.favicon_policy != null) {
            this.faviconPolicy.set(data.favicon_policy);
          } else {
            this.faviconPolicy.set("enabledOnly");
            this.translate.get("vault.error.preferences").subscribe((translation: string) => {
              this.toast.error(translation);
            });
          }
        }
      },
      error: (error) => {
        let errorMessage = "";
        if (error.error.message != null) {
          errorMessage = error.error.message;
        } else if (error.error.detail != null) {
          errorMessage = error.error.detail;
        }
        if (error.status == 0) {
          errorMessage = "vault.error.server_unreachable"
          return;
        }
        this.translate.get("vault.error.server").subscribe((translation: string) => {
          this.toast.error("Error : Impossible to update your preferences. " + this.translate.instant(errorMessage));
        });
      }
    });
  }

  navigate(route: string) {
    this.router.navigate([route], { relativeTo: this.route.root });
  }















  refreshUserData() {
    this.get_google_drive_option();
    this.get_preferences();
    this.isVaultLoading.set(true)
    this.getUserEncryptedVault().then(encrypted_vault => {
      this.vaultService.decryptVault(encrypted_vault, this.userService.zke_key()!).then(result => {
        this.isVaultLoading.set(false)
        if (result.errors.length != 0) {
          this.translate.get("vault.error.decryption").subscribe((translation: string) => {
            this.toast.error(translation, result.errors.join(". "));
          });
        }
        this.userService.vault.set(result.vault)
        this.userService.updateVaultTagsList()
        this.userService.is_vault_in_memory = true
      },
        error => {
          this.isVaultLoading.set(false)
          this.translate.get("vault.error.decryption").subscribe((translation: string) => {
            this.toast.error(translation, error);
          });
        })
    })
  }

  downloadVault() {
    this.http.get(this.apiService.baseURL + "/api/v1/vault/export", { withCredentials: true, observe: 'response', responseType: 'blob' },).subscribe({
      next: (response) => {
        const blob = new Blob([response.body!], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const date = String(formatDate(new Date(), 'dd-MM-yyyy-hh-mm-ss', 'en'));
        a.download = 'Zero-TOTP_backup_' + date + '.txt';
        a.click();
        window.URL.revokeObjectURL(url);
        this.toast.success(this.translate.instant("vault.downloaded"));
      },
      error: error => {
        let errorMessage = "";
        if (error.error.message != null) {
          errorMessage = error.error.message;
        } else if (error.error.detail != null) {
          errorMessage = error.error.detail;
        }

        if (error.status == 0) {
          errorMessage = "vault.error.server_unreachable"
        } else if (error.status == 401) {
          this.userService.clear();
          this.router.navigate(["/login/sessionEnd"], { relativeTo: this.route.root });
          return;
        }
        this.translate.get("vault.error.server").subscribe((translation: string) => {
          this.toast.error(translation + " " + this.translate.instant(errorMessage));
        });
      }
    });
  }

  get_oauth_authorization_url() {
    this.http.get(this.apiService.baseURL + "/api/v1/google-drive/oauth/authorization-flow", { withCredentials: true, observe: 'response' }).subscribe({
      next: (response) => {
        const data = JSON.parse(JSON.stringify(response.body))
        sessionStorage.setItem("oauth_state", data.state);
        window.location.href = data.authorization_url;
      },
      error: (error) => {
        let errorMessage = "";
        if (error.error.message != null) {
          errorMessage = error.error.message;
        } else if (error.error.detail != null) {
          errorMessage = error.error.detail;
        }
        this.translate.get("vault.oauth.error.server").subscribe((translation: string) => {
          this.toast.error(translation + ". " + errorMessage);
        });
      }
    });
  }




  get_google_drive_option() {
    this.globalConfigurationService.is_google_drive_enabled_on_this_tenant().then((enabled) => {
      this.is_google_drive_enabled_on_this_tenant.set(enabled);
      if (enabled) {
        this.http.get(this.apiService.baseURL + "/api/v1/google-drive/option", { withCredentials: true, observe: 'response' }).subscribe({
          next: (response) => {
            const data = JSON.parse(JSON.stringify(response.body))
            if (data.status == "enabled") {
              this.isGoogleDriveEnabled = true;
              this.check_last_backup();
            } else {
              this.isGoogleDriveEnabled = false;
              this.isGoogleDriveSync.set("false");
            }
          }, error: (error) => {
            let errorMessage = "";
            if (error.error.message != null) {
              errorMessage = error.error.message;
            } else if (error.error.detail != null) {
              errorMessage = error.error.detail;
            }
            this.translate.get("vault.error.server").subscribe((translation: string) => {
              this.toast.error(translation + " " + errorMessage);
            });
          }
        });
      }
    });
  }

  backup_vault_to_google_drive() {
    this.http.put(this.apiService.baseURL + "/api/v1/google-drive/backup", {}, { withCredentials: true, observe: 'response' },).subscribe({
      next: (response) => {
        this.isGoogleDriveSync.set("uptodate");
        this.lastBackupDate.set(String(formatDate(new Date(), 'dd/MM/yyyy HH:mm:ss', 'en')));
      },
      error: (error) => {
        this.isGoogleDriveSync.set('error');
        let errorMessage = "";
        if (error.error.message != null) {
          errorMessage = error.error.message;
        } else if (error.error.detail != null) {
          errorMessage = error.error.title;
        }
        this.translate.get("vault.error.backup.part1").subscribe((translation: string) => {
          this.toast.error(translation + " " + errorMessage + ". " + this.translate.instant("vault.error.backup.part2"));
        });
      }
    });
  }

  check_last_backup() {
    this.http.get(this.apiService.baseURL + "/api/v1/google-drive/last-backup/verify", { withCredentials: true, observe: 'response' },).subscribe({
      next: (response) => {
        const data = JSON.parse(JSON.stringify(response.body))
        if (data.status == "ok") {
          if (data.is_up_to_date == true) {
            this.isGoogleDriveSync.set("uptodate");
            const date_str = data.last_backup_date.split("T")[0] + " " + data.last_backup_date.split("T")[1];
            this.lastBackupDate.set(String(formatDate(new Date(date_str), 'dd/MM/yyyy HH:mm:ss', 'en')));
          } else {
            this.backup_vault_to_google_drive();
          }
        } else if (data.status == "corrupted_file") {
          this.isGoogleDriveSync.set("error");
          this.translate.get("vault.error.google.unreadable").subscribe((translation: string) => {
            this.toast.error(translation);
          });
        } else {
          this.translate.get("vault.error.google.unreadable").subscribe((translation: string) => {
            this.toast.error(translation);
          });
        }
      }, error: (error) => {
        if (error.status == 404) {
          this.backup_vault_to_google_drive();
        } else if (error.status == 400) {
          const error_info = error.error as { message: string, error_id: string | undefined };
          if (error_info.error_id != undefined && error_info.error_id == "3c071611-744a-4c93-95c8-c87ee3fce00d") {
            this.isGoogleDriveSync.set('error');
            this.google_drive_error_message = this.translate.instant("vault.google_drive_refresh_token_error.title");
            this.google_drive_refresh_token_error_display_modal_active.set(true);
            this.google_drive_refresh_token_error.set(true);
          } else {
            this.google_drive_error_message.set("An error occured while checking your backup. Got error " + error.status + ". " + error.error.message);
          }
        } else {
          this.isGoogleDriveSync.set('error');
          let errorMessage = "";
          if (error.error.message != null) {
            errorMessage = error.error.message;
          } else if (error.error.detail != null) {
            errorMessage = error.error.detail;
          } else if (error.error.error != null) {
            errorMessage = error.error.error;
          }
          this.google_drive_error_message.set("An error occured while checking your backup. Got error " + error.status + ". " + errorMessage);
        }
      }
    });
  }

  disable_google_drive() {
    this.http.delete(this.apiService.baseURL + "/api/v1/google-drive/option", { withCredentials: true, observe: 'response' },).subscribe({
      next: (response) => {
        this.isGoogleDriveEnabled = false;
        this.isGoogleDriveSync.set("false");
        this.toast.success(this.translate.instant("vault.google.disabled"));
      },
      error: (error) => {
        this.isGoogleDriveSync.set('error');
        let errorMessage = "";
        if (error.error.message != null) {
          errorMessage = error.error.message;
        } else if (error.error.detail != null) {
          errorMessage = error.error.detail;
        }

        this.toast.error(this.translate.instant("vault.error.google.disable") + " " + errorMessage);
      }
    });
  }




  resync_after_error() {
    this.disable_google_drive();
    this.isGoogleDriveSync.set("loading");
    setTimeout(() => {
      this.get_oauth_authorization_url();
    }, 2000);

  }





  unlockVault() {
    this.isDecryptingLockedVaut = true;
    this.vaultDecryptionErrorMessage.set("");
    this.http.get(this.apiService.baseURL + "/api/v1/user/derived-key-salt", { withCredentials: true, observe: 'response' }).subscribe({
      next: (response) => {
        if (response.status === 200) {
          const derived_key_salt_req_data = response.body as { derived_key_salt: string };
          this.userService.derivedKeySalt.set(derived_key_salt_req_data.derived_key_salt);
          this.http.get(this.apiService.baseURL + "/api/v1/zke_encrypted_key", { withCredentials: true, observe: 'response' }).subscribe({
            next: (response) => {
              if (response.status === 200) {
                const zke_req_data = response.body as { zke_encrypted_key: string };
                const zke_encrypted_key = zke_req_data.zke_encrypted_key;
                this.userService.derivePassphrase(this.userService.derivedKeySalt()!, this.passphrase).then((derivedKey) => {
                  this.userService.decryptZKEKey(zke_encrypted_key, derivedKey, this.userService.isVaultLocal()!).then((zke_key) => {
                    this.userService.zke_key.set(zke_key!);
                    this.isVaultEncrypted.set(false);
                    this.isDecryptingLockedVaut = false;
                    this.refreshUserData()
                  }, (error) => {
                    console.log(error);
                    this.isDecryptingLockedVaut = false;
                    this.vaultDecryptionErrorMessage.set("generic_errors.invalid_creds");
                  });
                }, (error) => {
                  console.log(error);
                  this.isDecryptingLockedVaut = false;
                  this.translate.get("vault.error.unlock").subscribe((translation: string) => {
                    this.toast.error(translation + " " + "U5");
                  });
                });

              } else {
                console.log(response);
                this.isDecryptingLockedVaut = false;
                this.translate.get("vault.error.unlock").subscribe((translation: string) => {
                  this.toast.error(translation + " " + "U3-" + response.status);
                });
              }

            }, error: (error) => {
              console.log(error);
              this.isDecryptingLockedVaut = false;
              this.translate.get("vault.error.unlock").subscribe((translation: string) => {
                this.toast.error(translation + " " + "U4");
              });

            }
          });
        } else {
          console.log(response)
          this.isDecryptingLockedVaut = false;
          this.translate.get("vault.error.unlock").subscribe((translation: string) => {
            this.toast.error(translation + " " + "U1-" + response.statusText);
          });
        }
      }, error: (error) => {
        this.isDecryptingLockedVaut = false;
        console.log(error);
        this.translate.get("vault.error.unlock").subscribe((translation: string) => {
          this.toast.error(translation + " " + "U2");
        });
      }
    })
  }
}
