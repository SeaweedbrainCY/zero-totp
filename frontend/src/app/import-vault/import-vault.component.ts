import { Component, OnInit, OnDestroy, signal, ChangeDetectionStrategy } from '@angular/core';
import { faFileArrowDown, faArrowRight, faCloudArrowUp, faCheck, faUnlockKeyhole, faLock, faUnlock, faCircleCheck, faCircleNotch, faCircleExclamation, faFileCircleCheck } from '@fortawesome/free-solid-svg-icons';
import { faCircle, faFileExcel } from '@fortawesome/free-regular-svg-icons';
import { TranslateService } from '@ngx-translate/core';
import { Router, ActivatedRoute, RouterStateSnapshot, NavigationEnd } from '@angular/router';
import { ViewportRuler } from '@angular/cdk/scrolling';
import { NgZone } from '@angular/core';
import { ToastrService } from 'ngx-toastr';
import { LocalVaultV1Service, UploadVaultStatus } from '../services/upload-vault/LocalVaultv1Service.service';
import { Utils } from '../common/Utils/utils';
import { VaultService } from '../services/VaultService/vault.service';
import { forkJoin, of, Subscription } from 'rxjs';
import { formatDate } from '@angular/common';
import { UserService } from '../services/User/user.service';
import { Crypto } from '../common/Crypto/crypto';
import { HttpClient, HttpResponse } from '@angular/common/http';




@Component({
  selector: 'app-import-vault',
  templateUrl: './import-vault.component.html',
  styleUrl: './import-vault.component.css',
  standalone: false,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ImportVaultComponent implements OnInit, OnDestroy {
  faFileArrowDown = faFileArrowDown;
  faArrowRight = faArrowRight;
  faCloudArrowUp = faCloudArrowUp
  faCircleExclamation = faCircleExclamation;
  faFileCircleCheck = faFileCircleCheck;
  vault_steps: Map<string, String[]> = new Map<string, String[]>();
  faCheck = faCheck;
  faUnlockKeyhole = faUnlockKeyhole;
  faLock = faLock;
  faUnlock = faUnlock;
  faCircleEmpty = faCircle;
  faCircleCheck = faCircleCheck;
  faFileExcel = faFileExcel;
  faCircleNotch = faCircleNotch;

  vault_type = signal<string | null>(null);
  step = signal<string | null>(null);
  continue_button_text = signal("continue");
  local_vault_service = signal<LocalVaultV1Service | null>(null);
  isUnsecureVaultModaleActive = signal(false);
  imported_vault_passphrase = signal("");
  vault_date = signal("");
  loading_file = signal(false);
  isMobileDevice = signal(false);
  is_continue_disabled = signal(false);
  is_importing = signal(false);
  file_name = signal("");
  decrypted_vault = signal<Map<string, Map<string, string>> | undefined>(undefined);
  decryption_error = signal("");
  decrypt_input_visible = signal(true);
  uploading = signal(false);
  upload_state = signal("");
  uploaded_uuid = signal<string[]>([]);
  upload_error_uuid = signal<string[]>([]);
  importSuccess = signal(false);
  import_had_error = signal(false);

  selected_merging_option = "";
  api_public_key: any = undefined;
  width: number = 0;
  height: number = 0;
  apiRequestDelay: number = 500;
  apiBackoffFactor: number = 1.5;

  private readonly viewportChange = this.viewportRuler
    .change(200)
    .subscribe(() => this.ngZone.run(() => this.setSize()));


  constructor(
    private translate: TranslateService,
    private router: Router,
    private route: ActivatedRoute,
    private readonly viewportRuler: ViewportRuler,
    private readonly ngZone: NgZone,
    private toastr: ToastrService,
    private localVaultv1: LocalVaultV1Service,
    private utils: Utils,
    private vaultService: VaultService,
    private userService: UserService,
    private crypto: Crypto,
    private http: HttpClient
  ) {
    this.vault_steps.set("zero-totp", ["import", "decrypt", "encrypt"])
    this.setSize();
  }

  ngOnInit(): void {
    if(!this.userService.isVaultLoadedAndDecryptable()){
        this.router.navigate(["/vault"], {relativeTo:this.route.root});
    }

    this.init_component()

    this.route.paramMap.subscribe(params => {
      this.init_component()
    })
  }

  ngOnDestroy() {
    this.viewportChange.unsubscribe();
  }

  init_component() {
    this.vault_type.set(this.route.snapshot.paramMap.get('type'));
    this.step.set(this.route.snapshot.paramMap.get('step'));
    console.log(this.vault_type())
    console.log(this.step())
    if (this.vault_type() != null) {
      if (!(this.vault_steps.has(this.vault_type()!))) {
        console.log("not found. Redirecting to import")
        this.router.navigate(['/import/vault'])
      }
      if (this.vault_type() == "zero-totp") {
        if (this.step() == null) {
          this.redirectToFirstStep()
        } else {
          if (!(this.vault_steps.get(this.vault_type()!)!.includes(this.step()!))) {
            this.redirectToFirstStep()
          } else {
            if (this.step() == "import") {
              if (this.local_vault_service() == null) {
                this.is_continue_disabled.set(true);
              } else {
                this.is_continue_disabled.set(false);
              }
            } else if (this.step() == "decrypt") {
              if (this.local_vault_service() == null) {
                this.router.navigate(['/import/vault/zero-totp/import'])
              } else {
                if (this.decrypted_vault() == undefined) {
                  this.is_continue_disabled.set(true);
                } else {
                  this.is_continue_disabled.set(false);
                }
              }
            } else if (this.step() == "encrypt") {
              if (this.decrypted_vault() == undefined) {
                this.router.navigate(['/import/vault/zero-totp/import'])
              } else {
                this.continue_button_text.set("confirm");
                try {
                  const vaultDateStr = this.local_vault_service()!.get_date()!.split(".")[0];
                  this.vault_date.set(String(formatDate(new Date(vaultDateStr), 'dd/MM/yyyy HH:mm:ss O', 'en')));
                } catch {
                  this.vault_date.set(this.local_vault_service()!.get_date()!);
                }
              }
            }
          }
        }
      }
    }
  }

  private setSize() {
    const { width, height } = this.viewportRuler.getViewportSize();
    this.width = width;
    this.height = height;
    this.isMobileDevice.set(width < 768);
  }

  redirectToFirstStep() {
    this.router.navigate(['/import/vault/' + this.vault_type() + '/' + this.vault_steps.get(this.vault_type()!)![0]])
  }

  hideDecryptionInput() {
    setTimeout(() => {
      this.decrypt_input_visible.set(false);
    }, 1000);
  }

  openVaultV1(event: any, unsecure_context: string, input: any) {
    this.local_vault_service()!.parseUploadedVault(unsecure_context, this.api_public_key).then((vault_parsing_status) => {
      switch (vault_parsing_status) {
        case UploadVaultStatus.SUCCESS: {
          this.file_name.set(input.files[0].name);
          this.is_continue_disabled.set(false);
          this.loading_file.set(false);
          break
        }
        case UploadVaultStatus.INVALID_JSON: {
          this.translate.get("login.errors.import_vault.invalid_type").subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "");
          });
          this.local_vault_service.set(null);
          event.target.value = null;
          this.loading_file.set(false);
          break;
        }

        case UploadVaultStatus.INVALID_VERSION: {
          this.translate.get("login.errors.import_vault.invalid_version").subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "");
          });
          this.local_vault_service.set(null);
          event.target.value = null;
          this.loading_file.set(false);
          break;
        }
        case UploadVaultStatus.NO_SIGNATURE: {
          this.translate.get("login.errors.import_vault.no_signature").subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "")
          });
          this.local_vault_service.set(null);
          event.target.value = null;
          this.loading_file.set(false);
          break;
        }
        case UploadVaultStatus.INVALID_SIGNATURE: {
          this.isUnsecureVaultModaleActive.set(true);
          this.file_name.set(input.files[0].name);
          this.loading_file.set(false);
          break;
        }
        case UploadVaultStatus.MISSING_ARGUMENT: {
          this.translate.get("login.errors.import_vault.missing_arg").subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "")
          });
          this.local_vault_service.set(null);
          event.target.value = null;
          this.loading_file.set(false);
          break;
        }
        case UploadVaultStatus.INVALID_ARGUMENT: {
          this.translate.get("login.errors.import_vault.invalid_arg").subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "")
          });
          this.local_vault_service.set(null);
          event.target.value = null;
          this.loading_file.set(false);
          break;
        }

        case UploadVaultStatus.UNKNOWN: {
          this.translate.get("login.errors.import_vault.error_unknown").subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "")
          });
          this.local_vault_service.set(null);
          event.target.value = null;
          this.loading_file.set(false);
          break;
        }

        default: {
          this.translate.get("login.errors.import_vault.error_unknown").subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "")
          });
          this.local_vault_service.set(null);
          event.target.value = null;
          this.loading_file.set(false);
          break;
        }
      }
    });
  }


  openFile(event: any): void {
    this.loading_file.set(true);
    console.log(event)
    this.is_importing.set(true);
    const input = event.target;
    const reader = new FileReader();
    reader.readAsText(input.files[0], 'utf-8');
    try {
      reader.onload = (() => {
        this.is_importing.set(false);
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
              this.local_vault_service.set(this.localVaultv1);
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
            } else {
              this.translate.get("login.errors.import_vault.invalid_version").subscribe((translation) => {
                this.utils.toastError(this.toastr, translation, "")
              });
              this.local_vault_service.set(null);
              event.target.value = null;
              this.loading_file.set(false);
            }
          } catch (e) {
            console.log("Zero-totp vault parsing error: " + e)
            this.translate.get("login.errors.import_vault.parse_fail").subscribe((translation) => {
              this.utils.toastError(this.toastr, translation, "")
            });
            this.local_vault_service.set(null);
            event.target.value = null;
            this.loading_file.set(false);
          }
        } else {
          this.translate.get("login.errors.import_vault.parse_fail").subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "")
          });
          this.local_vault_service.set(null);
          event.target.value = null;
          this.loading_file.set(false);
        }
      });
      reader.onerror = (() => {
        this.loading_file.set(false);
      });
    } catch {
      this.is_importing.set(false);
      this.local_vault_service.set(null);
      event.target.value = null;
      this.loading_file.set(false);
    }
  }


  continue() {
    if (this.vault_type() == "zero-totp") {
      const current_step_index = this.vault_steps.get(this.vault_type()!)!.indexOf(this.step()!)
      if (this.step() == "import") {
        this.router.navigate(['/import/vault/' + this.vault_type() + '/' + this.vault_steps.get(this.vault_type()!)![current_step_index + 1]])
      } else if (this.step() == "decrypt") {
        this.router.navigate(['/import/vault/' + this.vault_type() + '/' + this.vault_steps.get(this.vault_type()!)![current_step_index + 1]])
      } else if (this.step() == "encrypt") {
        this.upload()
      }
    }
  }

  cancel() {
    const current_step_index = this.vault_steps.get(this.vault_type()!)!.indexOf(this.step()!)
    if (current_step_index == 0) {
      this.router.navigate(['/import/vault'])
    } else {
      this.router.navigate(['/import/vault/' + this.vault_type() + '/' + this.vault_steps.get(this.vault_type()!)![current_step_index - 1]])
    }
  }

  giveUp() {
    this.router.navigate(['/import/vault'])
  }

  selectMergingOption(option: string) {
    this.selected_merging_option = option
    this.is_continue_disabled.set(false);
  }

  acceptUnsecureVault() {
    this.local_vault_service()!.set_is_signature_valid(true);
    this.isUnsecureVaultModaleActive.set(false);
    this.is_continue_disabled.set(false);
  }

  rejectUnsecureVault() {
    this.local_vault_service.set(null);
    this.isUnsecureVaultModaleActive.set(false);
    this.is_continue_disabled.set(true);
  }


  decrypt() {
    if (!this.decrypt_input_visible()) {
      return;
    }
    this.decryption_error.set("");
    if (this.local_vault_service() != null) {
      this.vaultService.derivePassphrase(this.local_vault_service()!.get_derived_key_salt()!, this.imported_vault_passphrase()).then((derivedKey) => {
        this.vaultService.decryptZKEKey(this.local_vault_service()!.get_zke_key_enc()!, derivedKey, true).then((zke_key) => {
          this.vaultService.decryptVault(this.local_vault_service()!.get_enc_secrets()!, zke_key).then((decrypted_vault) => {
            this.decrypted_vault.set(decrypted_vault);
            this.is_continue_disabled.set(false);
            this.hideDecryptionInput();

          }, (error) => {
            this.translate.get("import_vault.errors.decryption_failure").subscribe((translation) => {
              this.decryption_error.set(translation + ". Error: " + error);
            });

          });

        }, (error) => {
          this.translate.get("import_vault.errors.bad_passphrase").subscribe((translation) => {
            this.decryption_error.set(translation);
          });
        });
      },
        (error) => {
          this.translate.get("import_vault.errors.derivation_failure").subscribe((translation) => {
            this.decryption_error.set(translation);
          });
        });

    } else {
      this.translate.get("login.errors.import_vault.invalid_file").subscribe((translation) => {
        this.utils.toastError(this.toastr, translation, "");
      });
      const current_step_index = this.vault_steps.get(this.vault_type()!)!.indexOf(this.step()!)
      this.router.navigate(['/import/vault/' + this.vault_type() + '/' + this.vault_steps.get(this.vault_type()!)![current_step_index - 1]])
    }
  }


  upload() {
    this.uploading.set(true);
    this.upload_error_uuid.set([]);
    this.uploaded_uuid.set([]);
    this.import_had_error.set(false);
    this.translate.get("import_vault.uploading.steps.encryption").subscribe((translation) => {
      this.upload_state.set(translation);
    });

    this.processVaultConcurrently().then(() => {
      this.uploading.set(false);
      this.importSuccess.set(true);
    });
  }

  async processVaultConcurrently() {
    const concurrencyLimit = 5;
    const queue: (() => Promise<void>)[] = [];

    for (const [uuid, secretMap] of this.decrypted_vault()!) {
      queue.push(async () => {
        try {
          const enc_jsonProperty = await this.encryptSecret(secretMap);
          await this.uploadSecret(uuid, enc_jsonProperty);

          this.uploaded_uuid.update(arr => [...arr, uuid]);
          console.log("Uploaded:", uuid);
        } catch (error) {
          console.error("Error uploading", uuid, error);
          this.upload_error_uuid.update(arr => [...arr, uuid]);
          this.import_had_error.set(true);

          this.translate.get("import_vault.uploading.errors.upload").subscribe((translation) => {
            this.utils.toastError(
              this.toastr,
              translation,
              "Secret name: " + secretMap.get("name") + ". Error: " + error
            );
          });
        }
      });
    }

    const runQueue = async () => {
      const workers = new Array(concurrencyLimit).fill(0).map(async () => {
        while (queue.length) {
          const task = queue.shift();
          if (task) {
            await task();
          }
        }
      });
      await Promise.all(workers);
    };

    await runQueue();
  }


  encryptSecret(secret_properties: Map<string, string>): Promise<string> {
    return new Promise((resolve, reject) => {
      const jsonProperty = this.utils.mapToJson(secret_properties);
      try {
        this.crypto.encrypt(jsonProperty, this.userService.zke_key()!).then((enc_jsonProperty) => {
          resolve(enc_jsonProperty);
        });
      } catch (e) {
        reject(e);
      }
    });
  }

  uploadSecret(uuid: string, enc_jsonProperty: string): Promise<HttpResponse<Object>> {
    return new Promise((resolve, reject) => {
      this.http.post("/api/v1/encrypted_secret", {enc_secret: enc_jsonProperty}, {withCredentials: true, observe: 'response'}).subscribe({
        next: (response) => {
          resolve(response);
        },
        error: (error) => {
          reject(error.message + error.error.message);
        }
      });
    });
  }

  retryFailedOnes() {
    for (let uuid of this.decrypted_vault()!.keys()) {
      if (!this.upload_error_uuid().includes(uuid)) {
        this.decrypted_vault()!.delete(uuid);
      }
    }
    this.uploading.set(true);
    this.upload_error_uuid.set([]);
    this.uploaded_uuid.set([]);
    this.import_had_error.set(false);
    this.importSuccess.set(false);
    this.upload();
  }
}