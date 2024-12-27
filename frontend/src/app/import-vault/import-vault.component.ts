import { Component, OnInit, OnDestroy } from '@angular/core';
import { faFileArrowDown, faArrowRight, faCloudArrowUp, faCheck, faUnlockKeyhole, faLock, faUnlock, faCircleCheck, faCircleNotch } from '@fortawesome/free-solid-svg-icons';
import { faCircle } from '@fortawesome/free-regular-svg-icons';
import { TranslateService } from '@ngx-translate/core';
import { Router, ActivatedRoute, RouterStateSnapshot, NavigationEnd } from '@angular/router';
import { ViewportRuler } from '@angular/cdk/scrolling';
import { NgZone } from '@angular/core';
import { ToastrService } from 'ngx-toastr';
import { LocalVaultV1Service, UploadVaultStatus } from '../common/upload-vault/LocalVaultv1Service.service';
import { Utils } from '../common/Utils/utils';
import { VaultService } from '../common/VaultService/vault.service';
import { of } from 'rxjs';



@Component({
  selector: 'app-import-vault',
  templateUrl: './import-vault.component.html',
  styleUrl: './import-vault.component.css'
})
export class ImportVaultComponent implements OnInit, OnDestroy {
  faFileArrowDown = faFileArrowDown;
  faArrowRight = faArrowRight;
  faCloudArrowUp = faCloudArrowUp
  vault_steps: Map<string, String[]> = new Map<string, String[]>();
  step: string | null = null
  vault_type: string | null = null
  faCheck = faCheck;
  faUnlockKeyhole = faUnlockKeyhole;
  faLock = faLock;
  faUnlock = faUnlock;
  faCircleEmpty = faCircle;
  faCircleCheck = faCircleCheck;
  faCircleNotch = faCircleNotch;
  continue_button_text = "continue";
  local_vault_service: LocalVaultV1Service | null = null;
  isUnsecureVaultModaleActive = false;
  imported_vault_passphrase = "";

  isMobileDevice = false;

  selected_merging_option = "";
  is_continue_disabled = false;

  is_importing = false;
  file_name = "";

  width: number = 0;
  height: number = 0;

  decrypted_vault: Map<string, Map<string, string>> | undefined;
  decryption_error: string | undefined;


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
    private vaultService: VaultService
  ) {
    this.vault_steps.set("zero-totp", ["import", "decrypt", "encrypt"])
    this.setSize();

  }

  ngOnInit(): void {

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
              if(this.local_vault_service == null){
                this.is_continue_disabled = true;
              } else {
                this.is_continue_disabled = false;
              }
            } else if (this.step == "decrypt") {
              if(this.local_vault_service == null){
                console.log("null")
                this.router.navigate(['/import/vault/zero-totp/import'])
              } else {
                this.is_continue_disabled = true;
              }
              
            } else if (this.step == "select") {
              this.is_continue_disabled = true;
            } else if (this.step == "encrypt") {
              this.continue_button_text = "confirm"
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

  openFile(event: any): void {
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

              } else if (version == 1) {
                this.local_vault_service = this.localVaultv1
                this.local_vault_service.parseUploadedVault(unsecure_context).then((vault_parsing_status) => {
                  switch (vault_parsing_status) {
                    case UploadVaultStatus.SUCCESS: {
                      this.file_name = input.files[0].name
                      this.is_continue_disabled = false;
                      

                      break
                    }
                    case UploadVaultStatus.INVALID_JSON: {
                      this.translate.get("login.errors.import_vault.invalid_type").subscribe((translation) => {
                        this.utils.toastError(this.toastr, translation, "");
                      });
                      this.local_vault_service = null;
                      event.target.value = null;

                      break;
                    }

                    case UploadVaultStatus.INVALID_VERSION: {
                      this.translate.get("login.errors.import_vault.invalid_version").subscribe((translation) => {
                        this.utils.toastError(this.toastr, translation, "");
                      });
                      this.local_vault_service = null;
                      event.target.value = null;
                      break;
                    }
                    case UploadVaultStatus.NO_SIGNATURE: {
                      this.translate.get("login.errors.import_vault.no_signature").subscribe((translation) => {
                        this.utils.toastError(this.toastr, translation, "")
                      });
                      this.local_vault_service = null;
                      event.target.value = null;

                      break;
                    }
                    case UploadVaultStatus.INVALID_SIGNATURE: {
                      this.isUnsecureVaultModaleActive = true;
                      this.file_name = input.files[0].name
                      
                      break;
                    }
                    case UploadVaultStatus.MISSING_ARGUMENT: {
                      this.translate.get("login.errors.import_vault.missing_arg").subscribe((translation) => {
                        this.utils.toastError(this.toastr, translation, "")
                      });
                      this.local_vault_service = null;
                      event.target.value = null;

                      break;
                    }
                    case UploadVaultStatus.INVALID_ARGUMENT: {
                      this.translate.get("login.errors.import_vault.invalid_arg").subscribe((translation) => {
                        this.utils.toastError(this.toastr, translation, "")
                      });
                      this.local_vault_service = null;
                      event.target.value = null;

                      break;
                    }

                    case UploadVaultStatus.UNKNOWN: {
                      this.translate.get("login.errors.import_vault.error_unknown").subscribe((translation) => {
                        this.utils.toastError(this.toastr, translation, "")
                      });
                      this.local_vault_service = null;
                      event.target.value = null;

                      break;
                    }

                    default: {
                      this.translate.get("login.errors.import_vault.error_unknown").subscribe((translation) => {
                        this.utils.toastError(this.toastr, translation, "")
                      });
                      this.local_vault_service = null;
                      event.target.value = null;

                      break;
                    }
                  }
                });
              }
              else {
                this.translate.get("login.errors.import_vault.invalid_version").subscribe((translation) => {
                  this.utils.toastError(this.toastr, translation, "")
                });
                this.local_vault_service = null;
                event.target.value = null;

              }
            } catch (e) {
              console.log("Zero-totp vault parsing error: " + e)
              this.translate.get("login.errors.import_vault.parse_fail").subscribe((translation) => {
                this.utils.toastError(this.toastr, translation, "")
              });
              this.local_vault_service = null;
              event.target.value = null;

            }
          } else {
            this.translate.get("login.errors.import_vault.parse_fail").subscribe((translation) => {
              this.utils.toastError(this.toastr, translation, "")
            });
            this.local_vault_service = null;
            event.target.value = null;

          }
        });
      } catch {
        this.is_importing = false
        this.local_vault_service = null;
        event.target.value = null;
      }

    }


  continue(){
      if (this.vault_type == "zero-totp") {
        const current_step_index = this.vault_steps.get(this.vault_type)!.indexOf(this.step!)
        if (this.step == "import") {
          //TODO 
          this.router.navigate(['/import/vault/' + this.vault_type + '/' + this.vault_steps.get(this.vault_type)![current_step_index + 1]])
        } else if (this.step == "decrypt") {
          //TODO 
          this.router.navigate(['/import/vault/' + this.vault_type + '/' + this.vault_steps.get(this.vault_type)![current_step_index + 1]])
        } else if (this.step == "select") {
          //TODO 
          this.router.navigate(['/import/vault/' + this.vault_type + '/' + this.vault_steps.get(this.vault_type)![current_step_index + 1]])
        } else if (this.step == "encrypt") {
          //TODO 
          console.log("done")
        }
      }
    }

    cancel(){
      const current_step_index = this.vault_steps.get(this.vault_type!)!.indexOf(this.step!)
      if (current_step_index == 0) {
        this.router.navigate(['/import/vault'])
      } else {
        this.router.navigate(['/import/vault/' + this.vault_type + '/' + this.vault_steps.get(this.vault_type!)![current_step_index - 1]])
      }
    }

    giveUp(){
      this.router.navigate(['/import/vault'])
    }

    selectMergingOption(option: string){
      this.selected_merging_option = option
      this.is_continue_disabled = false
    }

    acceptUnsecureVault(){
      this.local_vault_service!.set_is_signature_valid(true); 
      this.isUnsecureVaultModaleActive = false;
      this.is_continue_disabled = false;
    }

    rejectUnsecureVault(){
      this.local_vault_service = null;
      this.isUnsecureVaultModaleActive = false;
      this.is_continue_disabled = true;
    }


    decrypt(){
      this.decryption_error = "";
      if(this.local_vault_service != null){
        this.vaultService.derivePassphrase(this.local_vault_service!.get_derived_key_salt()!, this.imported_vault_passphrase).then((derivedKey)=>{
          this.vaultService.decryptZKEKey(this.local_vault_service!.get_zke_key_enc()!, derivedKey, true).then((zke_key)=>{
            this.vaultService.decryptVault(this.local_vault_service!.get_enc_secrets()!, zke_key).then((decrypted_vault)=>{
              this.decrypted_vault = decrypted_vault;

            }, (error)=>{
              this.translate.get("import_vault.errors.decryption_failure").subscribe((translation)=>{
               this.decryption_error = translation + ". Error: " + error;
              });

            });

          }, (error)=>{
            this.translate.get("import_vault.errors.bad_passphrase").subscribe((translation)=>{
             this.decryption_error = translation;
            });
          });
        }, 
        (error)=>{
          this.translate.get("import_vault.errors.derivation_failure").subscribe((translation)=>{
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


  }
