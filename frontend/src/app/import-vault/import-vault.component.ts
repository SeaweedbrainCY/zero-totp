import { Component, OnInit, OnDestroy } from '@angular/core';
import { faFileArrowDown, faArrowRight, faCloudArrowUp, faCheck, faUnlockKeyhole, faLock, faUnlock, faCircleCheck, faCircleNotch, faCircleExclamation, faFileCircleCheck } from '@fortawesome/free-solid-svg-icons';
import { faCircle, faFileExcel } from '@fortawesome/free-regular-svg-icons';
import { TranslateService } from '@ngx-translate/core';
import { Router, ActivatedRoute, RouterStateSnapshot, NavigationEnd } from '@angular/router';
import { ViewportRuler } from '@angular/cdk/scrolling';
import { NgZone } from '@angular/core';
import { ToastrService } from 'ngx-toastr';
import { LocalVaultV1Service, UploadVaultStatus } from '../common/upload-vault/LocalVaultv1Service.service';
import { Utils } from '../common/Utils/utils';
import { VaultService } from '../common/VaultService/vault.service';
import { forkJoin, of, Subscription } from 'rxjs';
import { formatDate } from '@angular/common';
import { UserService } from '../common/User/user.service';
import { Crypto } from '../common/Crypto/crypto';
import { HttpClient, HttpResponse } from '@angular/common/http';




@Component({
  selector: 'app-import-vault',
  templateUrl: './import-vault.component.html',
  styleUrl: './import-vault.component.css',
  standalone: false
})
export class ImportVaultComponent implements OnInit, OnDestroy {
  faFileArrowDown = faFileArrowDown;
  faArrowRight = faArrowRight;
  faCloudArrowUp = faCloudArrowUp
  faCircleExclamation = faCircleExclamation;
  faFileCircleCheck = faFileCircleCheck;
  vault_steps: Map<string, String[]> = new Map<string, String[]>();
  step: string | null = null
  vault_type: string | null = null
  faCheck = faCheck;
  faUnlockKeyhole = faUnlockKeyhole;
  faLock = faLock;
  faUnlock = faUnlock;
  faCircleEmpty = faCircle;
  faCircleCheck = faCircleCheck;
  faFileExcel = faFileExcel;
  faCircleNotch = faCircleNotch;
  continue_button_text = "continue";
  local_vault_service: LocalVaultV1Service | null = null;
  isUnsecureVaultModaleActive = false;
  imported_vault_passphrase = "";
  vault_date = "";
  api_public_key = undefined;
  loading_file = false;
  // TO avoid API rate limiting. Might not be relevant
  apiRequestDelay: number = 500;
  apiBackoffFactor: number = 1.5;

  isMobileDevice = false;

  selected_merging_option = "";
  is_continue_disabled = false;

  is_importing = false;
  file_name = "";

  width: number = 0;
  height: number = 0;

  decrypted_vault: Map<string, Map<string, string>> | undefined;
  decryption_error: string = "";
  decrypt_input_visible = true;

  uploading = false;
  upload_state = "";
  uploaded_uuid: string[] = [];
  upload_error_uuid: string[] = [];
  importSuccess = false;
  import_had_error = false;


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
    if(this.userService.get_zke_key() == null){
      this.userService.refresh_user_id().then((success) => {
        this.router.navigate(["/vault"], {relativeTo:this.route.root});
      }, (error) => {
        this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
      });
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
    this.vault_type = this.route.snapshot.paramMap.get('type')
    this.step = this.route.snapshot.paramMap.get('step')
    console.log(this.vault_type)
    console.log(this.step)
    if (this.vault_type != null) {
      if (!(this.vault_steps.has(this.vault_type))) {
        console.log("not found. Redirecting to import")
        this.router.navigate(['/import/vault'])
      }
      if (this.vault_type == "zero-totp") {
        if (this.step == null) {
          this.redirectToFirstStep()
        } else {
          if (!(this.vault_steps.get(this.vault_type)!.includes(this.step))) {
            this.redirectToFirstStep()
          } else {
            if (this.step == "import") {
              if (this.local_vault_service == null) {
                this.is_continue_disabled = true;
              } else {
                this.is_continue_disabled = false;
              }
            } else if (this.step == "decrypt") {
              if (this.local_vault_service == null) {
                this.router.navigate(['/import/vault/zero-totp/import'])
              } else {
                if (this.decrypted_vault == undefined) {
                  this.is_continue_disabled = true;
                } else {
                  this.is_continue_disabled = false;
                }
              }
            } else if (this.step == "encrypt") {
              if (this.decrypted_vault == undefined) {
                this.router.navigate(['/import/vault/zero-totp/import'])
              } else {
                this.continue_button_text = "confirm"
                try {
                  const vaultDateStr = this.local_vault_service!.get_date()!.split(".")[0];
                  this.vault_date = String(formatDate(new Date(vaultDateStr), 'dd/MM/yyyy HH:mm:ss O', 'en'));
                } catch {
                  this.vault_date = this.local_vault_service!.get_date()!;
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
    if (width < 768) {
      this.isMobileDevice = true;
    } else {
      this.isMobileDevice = false;
    }
  }

  redirectToFirstStep() {
    this.router.navigate(['/import/vault/' + this.vault_type + '/' + this.vault_steps.get(this.vault_type!)![0]])
  }

  hideDecryptionInput() {
    setTimeout(() => {
      this.decrypt_input_visible = false;
    }, 1000);
  }

  openVaultV1(event:any,unsecure_context:string, input:any) {
    this.local_vault_service!.parseUploadedVault(unsecure_context, this.api_public_key).then((vault_parsing_status) => {
      switch (vault_parsing_status) {
        case UploadVaultStatus.SUCCESS: {
          this.file_name = input.files[0].name
          this.is_continue_disabled = false;
          this.loading_file = false;
          break
        }
        case UploadVaultStatus.INVALID_JSON: {
          this.translate.get("login.errors.import_vault.invalid_type").subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "");
          });
          this.local_vault_service = null;
          event.target.value = null;
          this.loading_file = false;

          break;
        }

        case UploadVaultStatus.INVALID_VERSION: {
          this.translate.get("login.errors.import_vault.invalid_version").subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "");
          });
          this.local_vault_service = null;
          event.target.value = null;
          this.loading_file = false;
          break;
        }
        case UploadVaultStatus.NO_SIGNATURE: {
          this.translate.get("login.errors.import_vault.no_signature").subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "")
          });
          this.local_vault_service = null;
          event.target.value = null;
          this.loading_file = false;

          break;
        }
        case UploadVaultStatus.INVALID_SIGNATURE: {
          this.isUnsecureVaultModaleActive = true;
          this.file_name = input.files[0].name
          this.loading_file = false;
          break;
        }
        case UploadVaultStatus.MISSING_ARGUMENT: {
          this.translate.get("login.errors.import_vault.missing_arg").subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "")
          });
          this.local_vault_service = null;
          event.target.value = null;
          this.loading_file = false;
          break;
        }
        case UploadVaultStatus.INVALID_ARGUMENT: {
          this.translate.get("login.errors.import_vault.invalid_arg").subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "")
          });
          this.local_vault_service = null;
          event.target.value = null;
          this.loading_file = false;
          break;
        }

        case UploadVaultStatus.UNKNOWN: {
          this.translate.get("login.errors.import_vault.error_unknown").subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "")
          });
          this.local_vault_service = null;
          event.target.value = null;
          this.loading_file = false;
          break;
        }

        default: {
          this.translate.get("login.errors.import_vault.error_unknown").subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "")
          });
          this.local_vault_service = null;
          event.target.value = null;
          this.loading_file = false;
          break;
        }
      }
    });
  }


  openFile(event: any): void {
    this.loading_file = true;
    console.log(event)
    this.is_importing = true
    const input = event.target;
    const reader = new FileReader();
    reader.readAsText(input.files[0], 'utf-8');
    try {
      reader.onload = (() => {
        this.is_importing = false
        if (reader.result) {
          try {
            const unsecure_context = reader.result.toString();
            const version = this.localVaultv1.extract_version_from_vault(unsecure_context);
            if (version == null) {
              this.translate.get("login.errors.import_vault.invalid_file").subscribe((translation) => {
                this.utils.toastError(this.toastr, translation, "");
              });
              this.loading_file = false;

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
                  this.loading_file = false;
                  this.openVaultV1(event, unsecure_context, input);
                }
              });
            }
            else {
              this.translate.get("login.errors.import_vault.invalid_version").subscribe((translation) => {
                this.utils.toastError(this.toastr, translation, "")
              });
              this.local_vault_service = null;
              event.target.value = null;
              this.loading_file = false;

            }
          } catch (e) {
            console.log("Zero-totp vault parsing error: " + e)
            this.translate.get("login.errors.import_vault.parse_fail").subscribe((translation) => {
              this.utils.toastError(this.toastr, translation, "")
            });
            this.local_vault_service = null;
            event.target.value = null;
            this.loading_file = false;

          }
        } else {
          this.translate.get("login.errors.import_vault.parse_fail").subscribe((translation) => {
            this.utils.toastError(this.toastr, translation, "")
          });
          this.local_vault_service = null;
          event.target.value = null;
          this.loading_file = false;

        }
      });
         reader.onerror = (() => {
     this.loading_file = false;
   });
    } catch {
      this.is_importing = false
      this.local_vault_service = null;
      event.target.value = null;
      this.loading_file = false;
    }

  }


  continue() {
    if (this.vault_type == "zero-totp") {
      const current_step_index = this.vault_steps.get(this.vault_type)!.indexOf(this.step!)
      if (this.step == "import") {
        this.router.navigate(['/import/vault/' + this.vault_type + '/' + this.vault_steps.get(this.vault_type)![current_step_index + 1]])
      } else if (this.step == "decrypt") {
        this.router.navigate(['/import/vault/' + this.vault_type + '/' + this.vault_steps.get(this.vault_type)![current_step_index + 1]])
      } else if (this.step == "encrypt") {
        this.upload()
      }
    }
  }

  cancel() {
    const current_step_index = this.vault_steps.get(this.vault_type!)!.indexOf(this.step!)
    if (current_step_index == 0) {
      this.router.navigate(['/import/vault'])
    } else {
      this.router.navigate(['/import/vault/' + this.vault_type + '/' + this.vault_steps.get(this.vault_type!)![current_step_index - 1]])
    }
  }

  giveUp() {
    this.router.navigate(['/import/vault'])
  }

  selectMergingOption(option: string) {
    this.selected_merging_option = option
    this.is_continue_disabled = false
  }

  acceptUnsecureVault() {
    this.local_vault_service!.set_is_signature_valid(true);
    this.isUnsecureVaultModaleActive = false;
    this.is_continue_disabled = false;
  }

  rejectUnsecureVault() {
    this.local_vault_service = null;
    this.isUnsecureVaultModaleActive = false;
    this.is_continue_disabled = true;
  }


  decrypt() {
    if (!this.decrypt_input_visible) {
      return;
    }
    this.decryption_error = "";
    if (this.local_vault_service != null) {
      this.vaultService.derivePassphrase(this.local_vault_service!.get_derived_key_salt()!, this.imported_vault_passphrase).then((derivedKey) => {
        this.vaultService.decryptZKEKey(this.local_vault_service!.get_zke_key_enc()!, derivedKey, true).then((zke_key) => {
          this.vaultService.decryptVault(this.local_vault_service!.get_enc_secrets()!, zke_key).then((decrypted_vault) => {
            this.decrypted_vault = decrypted_vault;
            this.is_continue_disabled = false;
            this.hideDecryptionInput();

          }, (error) => {
            this.translate.get("import_vault.errors.decryption_failure").subscribe((translation) => {
              this.decryption_error = translation + ". Error: " + error;
            });

          });

        }, (error) => {
          this.translate.get("import_vault.errors.bad_passphrase").subscribe((translation) => {
            this.decryption_error = translation;
          });
        });
      },
        (error) => {
          this.translate.get("import_vault.errors.derivation_failure").subscribe((translation) => {
            this.decryption_error = translation;
          });
        });;


    } else {
      this.translate.get("login.errors.import_vault.invalid_file").subscribe((translation) => {
        this.utils.toastError(this.toastr, translation, "");
      });
      const current_step_index = this.vault_steps.get(this.vault_type!)!.indexOf(this.step!)
      this.router.navigate(['/import/vault/' + this.vault_type + '/' + this.vault_steps.get(this.vault_type!)![current_step_index - 1]])
    }
  }


  upload() {
    this.uploading = true;
    this.upload_error_uuid = [];
    this.uploaded_uuid = [];
    this.import_had_error = false;
    this.translate.get("import_vault.uploading.steps.encryption").subscribe((translation) => {
      this.upload_state = translation;
    });


      const uploadPromises: Promise<void>[] = [];
      const encryptPromises: Promise<void>[] = [];

     this.processVaultConcurrently().then(() => {
      this.uploading = false;
      this.importSuccess = true;
     });
  }

  async processVaultConcurrently() {
  const concurrencyLimit = 5;
  const queue: (() => Promise<void>)[] = [];
  const tasks: Promise<void>[] = [];

  for (const [uuid, secretMap] of this.decrypted_vault!) {
    // Wrap each upload in a task function
    queue.push(async () => {
      try {
        const enc_jsonProperty = await this.encryptSecret(secretMap);
        await this.uploadSecret(uuid, enc_jsonProperty);

        this.uploaded_uuid.push(uuid);
        console.log("Uploaded:", uuid);
      } catch (error) {
        console.error("Error uploading", uuid, error);
        this.upload_error_uuid.push(uuid);
        this.import_had_error = true;

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

  // Function to run queue with concurrency limit
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
        this.crypto.encrypt(jsonProperty, this.userService.get_zke_key()!).then((enc_jsonProperty) => {
          resolve(enc_jsonProperty);
        });
      } catch (e) {
        reject(e);
      }
    });

  }

  uploadSecret(uuid: string, enc_jsonProperty: string): Promise<HttpResponse<Object>> {

    return new Promise((resolve, reject)=>{
        this.http.post("/api/v1/encrypted_secret", {enc_secret:enc_jsonProperty},{withCredentials:true, observe: 'response'}).subscribe({
          next:(response) => {
            resolve(response);
          },
          error: (error)=>{
            reject(error.message + error.error.message);
          }
        });
    });
  }

  retryFailedOnes() {
    for (let uuid of this.decrypted_vault!.keys()) {
      if (!this.upload_error_uuid.includes(uuid)) {
        this.decrypted_vault!.delete(uuid);
      }
    }
    this.uploading = true;
    this.upload_error_uuid = [];
    this.uploaded_uuid = [];
    this.import_had_error = false;
    this.importSuccess = false;
    this.upload();
  }


}
