import { Component, OnInit, OnDestroy } from '@angular/core';
import { faFileArrowDown, faArrowRight, faCloudArrowUp, faCheck, faUnlockKeyhole, faLock, faUnlock, faCircleCheck, faCircleNotch } from '@fortawesome/free-solid-svg-icons';
import { faCircle } from '@fortawesome/free-regular-svg-icons';
import { TranslateService } from '@ngx-translate/core';
import { Router, ActivatedRoute } from '@angular/router';
import { ViewportRuler } from '@angular/cdk/scrolling';
import { NgZone } from '@angular/core';
import { ToastrService } from 'ngx-toastr';
import { LocalVaultV1Service, UploadVaultStatus } from '../common/upload-vault/LocalVaultv1Service.service';
import { Utils } from '../common/Utils/utils';



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
  vault_password = "";
  continue_button_text = "continue";
  local_vault_service: LocalVaultV1Service | null = null;
  isUnsecureVaultModaleActive = false;

  isMobileDevice = false;

  selected_merging_option = "";
  is_continue_disabled = false;

  is_importing = false;
  file_name = "";

  width: number = 0;
  height: number = 0;

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
    private utils: Utils
  ) {
    this.vault_steps.set("zero-totp", ["import", "decrypt", "select", "encrypt"])
    this.setSize();

  }

  ngOnInit(): void {

    this.init_component()

    this.router.events.subscribe((url: any) => {
      this.init_component()
    });





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
              this.is_continue_disabled = true;
            } else if (this.step == "decrypt") {
              this.is_continue_disabled = true;
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

                      break
                    }
                    case UploadVaultStatus.INVALID_JSON: {
                      this.translate.get("login.errors.import_vault.invalid_type").subscribe((translation) => {
                        this.utils.toastError(this.toastr, translation, "");
                      });

                      break;
                    }

                    case UploadVaultStatus.INVALID_VERSION: {
                      this.translate.get("login.errors.import_vault.invalid_version").subscribe((translation) => {
                        this.utils.toastError(this.toastr, translation, "");
                      });

                      break;
                    }
                    case UploadVaultStatus.NO_SIGNATURE: {
                      this.translate.get("login.errors.import_vault.no_signature").subscribe((translation) => {
                        this.utils.toastError(this.toastr, translation, "")
                      });

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

                      break;
                    }
                    case UploadVaultStatus.INVALID_ARGUMENT: {
                      this.translate.get("login.errors.import_vault.invalid_arg").subscribe((translation) => {
                        this.utils.toastError(this.toastr, translation, "")
                      });

                      break;
                    }

                    case UploadVaultStatus.UNKNOWN: {
                      this.translate.get("login.errors.import_vault.error_unknown").subscribe((translation) => {
                        this.utils.toastError(this.toastr, translation, "")
                      });

                      break;
                    }

                    default: {
                      this.translate.get("login.errors.import_vault.error_unknown").subscribe((translation) => {
                        this.utils.toastError(this.toastr, translation, "")
                      });

                      break;
                    }
                  }
                });
              }
              else {
                this.translate.get("login.errors.import_vault.invalid_version").subscribe((translation) => {
                  this.utils.toastError(this.toastr, translation, "")
                });

              }
            } catch (e) {
              this.translate.get("login.errors.import_vault.parse_fail").subscribe((translation) => {
                this.utils.toastError(this.toastr, translation, "")
              });

            }
          } else {
            this.translate.get("login.errors.import_vault.parse_fail").subscribe((translation) => {
              this.utils.toastError(this.toastr, translation, "")
            });

          }
        });
      } catch {
        this.is_importing = false
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
    }


  }
