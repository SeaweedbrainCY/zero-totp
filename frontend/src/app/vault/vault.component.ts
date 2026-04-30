import { Component, OnInit, OnDestroy, signal, WritableSignal } from '@angular/core';
import { UserService } from '../services/User/user.service';
import { ActivatedRoute, Router, NavigationEnd } from '@angular/router';
import { faPen, faSquarePlus, faCopy, faCheckCircle, faCircleXmark, faDownload, faDesktop, faRotateRight, faChevronUp, faChevronDown, faChevronRight, faLink, faCircleInfo, faUpload, faCircleNotch, faCircleExclamation, faCircleQuestion, faFlask, faMagnifyingGlass, faXmark, faServer, faLock, faEye, faEyeSlash, faKey, faArrowUpRightFromSquare } from '@fortawesome/free-solid-svg-icons';
import { faGoogleDrive } from '@fortawesome/free-brands-svg-icons';
import { HttpClient } from '@angular/common/http';

import { Crypto } from '../common/Crypto/crypto';
import { Utils } from '../common/Utils/utils';
import { formatDate } from '@angular/common';
import { LocalVaultV1Service } from '../services/upload-vault/LocalVaultv1Service.service';
import { TranslateService } from '@ngx-translate/core';
import { ToastrService } from 'ngx-toastr';
import { TOTP } from "totp-generator"
import { VaultService } from '../services/VaultService/vault.service';
import { GlobalConfigurationService } from '../services/GlobalConfiguration/global-configuration.service';


@Component({
  selector: 'app-vault',
  templateUrl: './vault.component.html',
  styleUrls: ['./vault.component.css'],
  standalone: false
})
export class VaultComponent implements OnInit, OnDestroy {
  // Fontawesome icons
  faPen = faPen;
  faSquarePlus = faSquarePlus;
  faCopy = faCopy;
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

  remainingTime = 0;
  local_vault_service: LocalVaultV1Service | null = null;
  isGoogleDriveEnabled = true;
  animationFrameId: number = 0;
  totp_code_expiration = 0;
  generating_next_totp_code = false;
  totp_code_generation_interval: number | undefined;
  passphrase = "";
  filter = "";
  isDecryptingLockedVaut = false;
  currentURL = ""


  // Signals 
  progress_bar_percent = signal(0);
  selectedTags: WritableSignal<string[]> = signal([]);
  vaultDecryptionErrorMessage = signal("");
  google_drive_refresh_token_error_display_modal_active = signal(false);
  google_drive_refresh_token_error = signal(false);
  is_google_drive_enabled_on_this_tenant = signal(false);
  current_domain = signal("");
  google_drive_error_message = signal("");
  isVaultEncrypted: WritableSignal<boolean | undefined> = signal(undefined);
  isPassphraseVisible = signal(false);
  isGoogleDriveSync = signal("loading"); // uptodate, loading, error, false
  vaultUUIDs: WritableSignal<string[]> = signal([]);
  isModalActive = signal(false)
  reloadSpin = signal(false)
  storageOptionOpen = signal(false)
  page_title = signal("vault.title.main");
  vault_date: WritableSignal<string | undefined> = signal(undefined); // for local vault
  isRestoreBackupModaleActive = signal(false);
  vault: WritableSignal<Map<string, Map<string, string>> | undefined> = signal(undefined);
  lastBackupDate = signal("");
  faviconPolicy = signal("");



  constructor(
    public userService: UserService,
    private router: Router,
    private route: ActivatedRoute,
    private http: HttpClient,
    private crypto: Crypto,
    private utils: Utils,
    private translate: TranslateService,
    private toastr: ToastrService,
    private vaultService: VaultService,
    public globalConfigurationService: GlobalConfigurationService
  ) {
    this.current_domain.set(window.location.host);
    router.events.subscribe((url:any) => {
      if (url instanceof NavigationEnd){
          this.currentURL = url.url;
      }
    });

  }

  ngOnInit() {
    if (this.userService.isVaultLocal()) {
      // Local vault, the user uploaded it 
      this.isVaultEncrypted.set(false);
      this.local_vault_service = this.userService.local_vault_service();
      let vaultDate = "unknown"
      try {
        const vaultDateStr = this.local_vault_service!.get_date()!.split(".")[0];
        vaultDate = String(formatDate(new Date(vaultDateStr), 'dd/MM/yyyy HH:mm:ss O', 'en'));
      } catch {
        vaultDate = "error"
      }


      this.page_title.set("vault.title.backup");
      this.vault_date.set(vaultDate);
      this.decrypt_vault(this.local_vault_service!.get_enc_secrets()!);
    } else if (this.userService.zke_key() == null) {
      // User refreshed the page
      this.userService.refresh_user_id().then(() => {
        this.isVaultEncrypted.set(true);
      }, () => {
        this.isVaultEncrypted.set(false);
        this.router.navigate(["/login/sessionKilled"], { relativeTo: this.route.root });
      });

    } else {
      // User is logged in, can have vault in memory
      document.getElementById("add-code-button")!.style.display = "flex";
      document.getElementById("add-code-button")!.onclick = () => { this.isModalActive.set(true); };
      this.isVaultEncrypted.set(false);
      this.get_google_drive_option();
      this.get_preferences();
      if (this.userService.vault() == null || this.currentURL == "/vault/reload") {
        // We need to download and decrypt the vault
        this.getUserEncryptedVault().then(encrypted_vault => {
          this.decrypt_vault(encrypted_vault).then(_ => {
            this.startDisplayingCode()
            this.display_vault()
          })
        })
      } else {
        // The vault is in memory no need to download/decrypt it
        this.vault.set(this.userService.vault()!)
        this.startDisplayingCode()
        this.display_vault()
      }

    }

  }

  ngOnDestroy() {
    if (this.totp_code_generation_interval != undefined) {
      clearInterval(this.totp_code_generation_interval);
    }
    // Hide the add button
    document.getElementById("add-code-button")!.style.display = "none";
  }



  startDisplayingCode() {
    this.totp_code_generation_interval = window.setInterval(() => { this.compute_totp_expiration() }, 100);
    // setInterval(()=> { this.generateTime() }, 20);
    // setInterval(()=> { this.generateCode() }, 100);
  }

  getUserEncryptedVault(): Promise<Array<Map<string, string>>> {
    return new Promise<Array<Map<string, string>>>((resolve, reject) => {
      this.reloadSpin.set(true)
      this.vault.set(new Map<string, Map<string, string>>());
      this.vaultUUIDs.set([]);
      this.userService.vault_tags.set([]);
      this.http.get("/api/v1/all_secrets", { withCredentials: true, observe: 'response' }).subscribe({
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
          this.reloadSpin.set(true)
          if (error.status == 404) {
            this.userService.vault.set(new Map<string, Map<string, string>>());
            this.reloadSpin.set(false)
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
              this.utils.toastError(this.toastr, translation + " " + this.translate.instant(errorMessage), "");
            });
          }
          reject(error)
        }
      });
    });
  }

  get_preferences() {
    this.http.get("/api/v1/preferences?fields=favicon_policy", { withCredentials: true, observe: 'response' }).subscribe({
      next: (response) => {
        if (response.body != null) {
          const data = JSON.parse(JSON.stringify(response.body));
          if (data.favicon_policy != null) {
            this.faviconPolicy.set(data.favicon_policy);
          } else {
            this.faviconPolicy.set("enabledOnly");
            this.translate.get("vault.error.preferences").subscribe((translation: string) => {
              this.utils.toastError(this.toastr, translation, "");
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
          this.utils.toastError(this.toastr, "Error : Impossible to update your preferences. " + this.translate.instant(errorMessage), "");
        });
      }
    });
  }

  decrypt_vault(encrypted_vault: Array<Map<string, string>>): Promise<boolean> {
    return new Promise<boolean>((resolve, reject) => {
      this.reloadSpin.set(true)
      this.vault.set(new Map<string, Map<string, string>>());
      this.vaultUUIDs.set([]);
      try {
        if (this.userService.zke_key() != null) {
          try {
            for (let secret of encrypted_vault) {
              const uuid = secret.get("uuid");
              const enc_secret = secret.get("enc_secret");
              if (uuid != null && enc_secret != null) {
                this.crypto.decrypt(enc_secret, this.userService.zke_key()!).then((dec_secret) => {
                  if (dec_secret == null) {
                    this.translate.get("vault.error.wrong_key").subscribe((translation: string) => {
                      this.utils.toastError(this.toastr, translation, "");
                    });
                    let fakeProperty = new Map<string, string>();
                    fakeProperty.set("color", "info");
                    fakeProperty.set("name", "🔒")
                    fakeProperty.set("secret", "");

                    this.vault.update(vault => vault?.set(uuid, fakeProperty));
                    this.reloadSpin.set(false)
                    reject("dec_secret is null")
                  } else {
                    try {
                      this.vault.update(vault => vault?.set(uuid, this.utils.mapFromJson(dec_secret)));
                      this.userService.vault.set(this.vault()!);
                      this.reloadSpin.set(false)
                      resolve(true)
                    } catch {
                      this.reloadSpin.set(false)
                      this.translate.get("vault.error.wrong_key").subscribe((translation: string) => {
                        this.utils.toastError(this.toastr, "vault.error.wrong_key", "");
                      });
                      reject("vault.error.wrong_key")
                    }
                  }
                }).catch((error) => {
                  console.log(error);
                  this.translate.get("vault.error.decryption").subscribe((translation: string) => {
                    this.utils.toastError(this.toastr, translation + " " + error, "");
                  });
                  this.reloadSpin.set(false)
                  reject(error)
                });
              } else {
                console.log("uuid or enc_secret is null");
                this.translate.get("vault.error.decryption").subscribe((translation: string) => {
                  this.utils.toastError(this.toastr, translation, "");
                });
                this.reloadSpin.set(false)
                reject("uuid or enc_secret is null")
              }

            }
          } catch (e) {
            console.log(e);
            this.translate.get("vault.error.wrong_key_vault").subscribe((translation: string) => {
              this.utils.toastError(this.toastr, translation, "")
            });
            this.reloadSpin.set(false)
            reject(e)
          }
        } else {
          this.translate.get("vault.error.decryption_vault").subscribe((translation: string) => {
            this.utils.toastError(this.toastr, translation, "")
          });
          this.reloadSpin.set(false)
          reject("vault.error.decryption_vault")
        }
      } catch (e) {
        this.translate.get("vault.error.retrieve_vault").subscribe((translation: string) => {
          this.utils.toastError(this.toastr, translation, "")
        });
        this.reloadSpin.set(false)
        reject(e)
      }
    })
  }

  navigate(route: string) {
    this.router.navigate([route], { relativeTo: this.route.root });

  }

  generateTime() {
    const duration = 30 - Math.floor(Date.now() / 10 % 3000) / 100;
    this.remainingTime = (duration / 30) * 100
  }


  compute_totp_expiration() {
    const now = Date.now();
    const remaining = this.totp_code_expiration - now;
    this.progress_bar_percent.set(remaining / 300);
    if (remaining < 0 && !this.generating_next_totp_code) {
      this.generating_next_totp_code = true;
      this.generateCode();
    }
  }

  generateCode() {
    if (this.vaultUUIDs == undefined) {
      this.totp_code_expiration = TOTP.generate("aa").expires; // Fake the timer
      this.generating_next_totp_code = false;
      return;
    }
    for (let uuid of this.vaultUUIDs()) {
      const secret = this.vault()!.get(uuid)!.get("secret")!;
      try {
        let code = TOTP.generate(secret).otp
        this.vault()!.get(uuid)!.set("code", code);
        if (this.generating_next_totp_code) {
          this.totp_code_expiration = TOTP.generate(secret).expires
          this.generating_next_totp_code = false;
        }
      } catch (e) {
        console.log(e);
        let code = "Error"
        this.vault()!.get(uuid)!.set("code", code);
      }
    }

    if (this.generating_next_totp_code) {
      this.totp_code_expiration = TOTP.generate("aa").expires; // New check in 1s
      this.generating_next_totp_code = false;
    }
  }

  filterVault() {
    this.vaultUUIDs.set([]);
    let tmp_vault = Array.from(this.vault()!.keys()) as string[];
    if (this.filter == "" && this.selectedTags.length == 0) {
      this.vaultUUIDs.set(tmp_vault);
      this.generateCode();
      return;
    }
    this.filter = this.filter.replace(/[^a-zA-Z0-9-_]/g, '');
    this.filter = this.filter.toLowerCase();
    if (this.filter.length > 50) {
      this.filter = this.filter.substring(0, 50);
    }
    let regex = new RegExp(this.filter);
    if (this.filter == "") { // we filter on tags
      regex = new RegExp(".*");
    }
    for (let uuid of tmp_vault) {
      let has_tag = false;
      if (this.selectedTags.length > 0) {
        if (this.vault()!.get(uuid)!.has("tags")) {
          const secret_tags = this.utils.parseTags(this.vault()!.get(uuid)!.get("tags")!);
          for (const tag of this.selectedTags()) {
            if (secret_tags.includes(tag)) {
              has_tag = true;
            }
          }
        }
      }
      if (this.selectedTags.length == 0 || has_tag) {
        //filter on search filter
        if (regex.test(this.get_favicon_url(this.vault()!.get(uuid)?.get('domain')).toLowerCase())) {
          this.vaultUUIDs.update(vault => [...vault, uuid]);
        } else if (this.vault()!.get(uuid)?.get('name')) {
          if (regex.test(this.vault()!.get(uuid)?.get('name')!.toLowerCase()!)) {
            this.vaultUUIDs.update(vault => [...vault, uuid]);
          }
        }
      }
    }
    this.generateCode();
  }

  edit(domain: string) {
    this.router.navigate(["/vault/edit/" + domain], { relativeTo: this.route.root });
  }

  copy() {
    this.utils.toastSuccess(this.toastr, this.translate.instant("copied"), "");
  }

  reload() {
    this.get_google_drive_option();
    this.get_preferences();
    this.getUserEncryptedVault().then(encrypted_vault => {
      this.decrypt_vault(encrypted_vault).then(_ => {
        this.startDisplayingCode()
        this.display_vault()
      })
    })
  }

  downloadVault() {
    this.http.get("/api/v1/vault/export", { withCredentials: true, observe: 'response', responseType: 'blob' },).subscribe({
      next: (response) => {
        const blob = new Blob([response.body!], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const date = String(formatDate(new Date(), 'dd-MM-yyyy-hh-mm-ss', 'en'));
        a.download = 'Zero-TOTP_backup_' + date + '.txt';
        a.click();
        window.URL.revokeObjectURL(url);
        this.utils.toastSuccess(this.toastr, this.translate.instant("vault.downloaded"), "");
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
          this.utils.toastError(this.toastr, translation + " " + this.translate.instant(errorMessage), "");
        });
      }
    });
  }

  get_oauth_authorization_url() {
    this.http.get("/api/v1/google-drive/oauth/authorization-flow", { withCredentials: true, observe: 'response' }).subscribe({
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
          this.utils.toastError(this.toastr, translation + ". " + errorMessage, "");
        });
      }
    });
  }




  get_google_drive_option() {
    this.globalConfigurationService.is_google_drive_enabled_on_this_tenant().then((enabled) => {
      this.is_google_drive_enabled_on_this_tenant.set(enabled);
      if (enabled) {
        this.http.get("/api/v1/google-drive/option", { withCredentials: true, observe: 'response' }).subscribe({
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
              this.utils.toastError(this.toastr, translation + " " + errorMessage, "");
            });
          }
        });
      }
    });
  }

  backup_vault_to_google_drive() {
    this.http.put("/api/v1/google-drive/backup", {}, { withCredentials: true, observe: 'response' },).subscribe({
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
          this.utils.toastError(this.toastr, translation + " " + errorMessage + ". " + this.translate.instant("vault.error.backup.part2"), "");
        });
      }
    });
  }

  check_last_backup() {
    this.http.get("/api/v1/google-drive/last-backup/verify", { withCredentials: true, observe: 'response' },).subscribe({
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
            this.utils.toastError(this.toastr, translation, "");
          });
        } else {
          this.translate.get("vault.error.google.unreadable").subscribe((translation: string) => {
            this.utils.toastError(this.toastr, translation, "");
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
    this.http.delete("/api/v1/google-drive/option", { withCredentials: true, observe: 'response' },).subscribe({
      next: (response) => {
        this.isGoogleDriveEnabled = false;
        this.isGoogleDriveSync.set("false");
        this.utils.toastSuccess(this.toastr, this.translate.instant("vault.google.disabled"), "");
      },
      error: (error) => {
        this.isGoogleDriveSync.set('error');
        let errorMessage = "";
        if (error.error.message != null) {
          errorMessage = error.error.message;
        } else if (error.error.detail != null) {
          errorMessage = error.error.detail;
        }

        this.utils.toastError(this.toastr, this.translate.instant("vault.error.google.disable") + " " + errorMessage, "");
      }
    });
  }


  get_favicon_url(unsafe_domain: string | undefined): string {
    if (unsafe_domain == undefined) {
      return "https://icons.duckduckgo.com/ip3/unknown.ico";
    }
    if (this.utils.domain_name_validator(unsafe_domain)) {
      return "https://icons.duckduckgo.com/ip3/" + unsafe_domain + ".ico";
    } else {
      return "https://icons.duckduckgo.com/ip3/unknown.ico";
    }
  }

  resync_after_error() {
    this.disable_google_drive();
    this.isGoogleDriveSync.set("loading");
    setTimeout(() => {
      this.get_oauth_authorization_url();
    }, 2000);

  }


  selectTag(tag: string) {
    if (this.selectedTags().includes(tag)) {
      this.selectedTags.update(tags => tags.filter(e => e !== tag));
    } else {
      this.selectedTags.update(tags => [...tags, tag])
    }
    this.filterVault();
  }

  display_vault() {
    this.filterVault(); // to display all the vault
    for (let uuid of this.vaultUUIDs()) {
      // display all tags, always
      if (this.vault()!.get(uuid)!.has("tags")) {
        const secret_tags = this.utils.parseTags(this.vault()!.get(uuid)!.get("tags")!);
        for (const tag of secret_tags) {
          if (!this.userService.vault_tags().includes(tag)) {
            this.userService.vault_tags.update(current => [...current, tag])
          }
        }
      }
    }
  }

  unlockVault() {
    this.isDecryptingLockedVaut = true;
    this.vaultDecryptionErrorMessage.set("");
    this.http.get("/api/v1/user/derived-key-salt", { withCredentials: true, observe: 'response' }).subscribe({
      next: (response) => {
        if (response.status === 200) {
          const derived_key_salt_req_data = response.body as { derived_key_salt: string };
          this.userService.derivedKeySalt.set(derived_key_salt_req_data.derived_key_salt);
          this.http.get("/api/v1/zke_encrypted_key", { withCredentials: true, observe: 'response' }).subscribe({
            next: (response) => {
              if (response.status === 200) {
                const zke_req_data = response.body as { zke_encrypted_key: string };
                const zke_encrypted_key = zke_req_data.zke_encrypted_key;
                this.vaultService.derivePassphrase(this.userService.derivedKeySalt()!, this.passphrase).then((derivedKey) => {
                  this.vaultService.decryptZKEKey(zke_encrypted_key, derivedKey, this.userService.isVaultLocal()!).then((zke_key) => {
                    this.userService.zke_key.set(zke_key!);
                    this.isVaultEncrypted.set(false);
                    document.getElementById("add-code-button")!.style.display = "flex";
                    document.getElementById("add-code-button")!.onclick = () => { this.isModalActive.set(true); };
                    this.isDecryptingLockedVaut = false;
                    this.getUserEncryptedVault().then(encrypted_vault => {
                      this.decrypt_vault(encrypted_vault).then(_ => {
                        this.startDisplayingCode()
                        this.display_vault()
                      }, error => {
                        console.log(error)
                      })
                    }, (error)=> {
                      console.log(error)
                    })
                  }, (error) => {
                    console.log(error);
                    this.isDecryptingLockedVaut = false;
                    this.vaultDecryptionErrorMessage.set("generic_errors.invalid_creds");
                  });
                }, (error) => {
                  console.log(error);
                  this.isDecryptingLockedVaut = false;
                  this.translate.get("vault.error.unlock").subscribe((translation: string) => {
                    this.utils.toastError(this.toastr, translation + " " + "U5", "");
                  });
                });

              } else {
                console.log(response);
                this.isDecryptingLockedVaut = false;
                this.translate.get("vault.error.unlock").subscribe((translation: string) => {
                  this.utils.toastError(this.toastr, translation + " " + "U3-" + response.statusText, "");
                });
              }

            }, error: (error) => {
              console.log(error);
              this.isDecryptingLockedVaut = false;
              this.translate.get("vault.error.unlock").subscribe((translation: string) => {
                this.utils.toastError(this.toastr, translation + " " + "U4", "");
              });

            }
          });
        } else {
          console.log(response)
          this.isDecryptingLockedVaut = false;
          this.translate.get("vault.error.unlock").subscribe((translation: string) => {
            this.utils.toastError(this.toastr, translation + " " + "U1-" + response.statusText, "");
          });
        }
      }, error: (error) => {
        this.isDecryptingLockedVaut = false;
        console.log(error);
        this.translate.get("vault.error.unlock").subscribe((translation: string) => {
          this.utils.toastError(this.toastr, translation + " " + "U2", "");
        });
      }
    })
  }

  getColorFromTOTPColorType(colorType: string): string {
    switch (colorType) {
      case "success": return "#63A375"
      case "danger": return "#FE6847"
      case "warning": return "#FFCF56"
      default: return "#5AA9E6"
    }
  }
}
