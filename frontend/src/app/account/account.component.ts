import { Component, OnInit, signal, Signal, WritableSignal } from '@angular/core';
import { faEnvelope, faLock, faCheck, faUser, faCog, faShield, faHourglassStart, faCircleInfo, faArrowsRotate, faFlask, faTrash, faVault, faExclamationTriangle, faEye, faEyeSlash, faCircleExclamation, faCircleNotch, faLightbulb, faL } from '@fortawesome/free-solid-svg-icons';
import { TOTPEntry, UserService, CommonError as UserServiceCommonError } from '../services/User/user.service';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { Utils } from '../common/Utils/utils';
import { ActivatedRoute, Router } from '@angular/router';
import { Crypto } from '../common/Crypto/crypto';
import { Buffer } from 'buffer';
import { TranslateService } from '@ngx-translate/core';
import { ToastrService } from 'ngx-toastr';
import { Writable } from 'node_modules/@angular/core/types/_chrome_dev_tools_performance-chunk';
import { VaultService } from '../services/VaultService/vault.service';
import { TrailingSlashPathLocationStrategy } from '@angular/common';

type LoadingButtons = {
  email: WritableSignal<boolean>;
  username: WritableSignal<boolean>;
  passphrase: WritableSignal<boolean>;
  deletion: WritableSignal<boolean>;
}

@Component({
  selector: 'app-account',
  templateUrl: './account.component.html',
  styleUrls: ['./account.component.css'],
  standalone: false
})
export class AccountComponent implements OnInit {
  faUser = faUser;
  faEnvelope = faEnvelope;
  faLock = faLock;
  faShield = faShield;
  faCircleInfo = faCircleInfo;
  faArrowsRotate = faArrowsRotate;
  faHourglassStart = faHourglassStart;
  faCircleExclamation = faCircleExclamation;
  faCircleNotch = faCircleNotch;
  faExclamationTriangle = faExclamationTriangle;
  faCheck = faCheck;
  faCog = faCog;
  faLightbulb = faLightbulb;
  faFlask = faFlask;
  faTrash = faTrash;
  faEye = faEye;
  faEyeSlash = faEyeSlash;
  isNewConfirmPassphraseVisible = signal(false);
  isNewPassphraseVisible = signal(false);
  isPassphraseVisible = signal(false);
  faVault = faVault;
  isDeletionModalActive = signal(false);
  isPassphraseModalActive = signal(false);
  buttonLoading: LoadingButtons = { username: signal(false), passphrase: signal(false), deletion: signal(false), email: signal(false) }
  username = "";
  usernameErrorMessage = signal("");
  email = "";
  confirmEmail = "";
  emailErrorMessage = signal("");
  emailConfirmErrorMessage = signal("");
  newPassword = "";
  confirmNewPassword = "";
  newPasswordErrorMessage = signal([""]);
  newPasswordConfirmErrorMessage = signal([""]);
  stepsDone: WritableSignal<Array<String>> = signal([""]);
  deletionErrorMessage = signal("")
  password = "";
  hashedOldPassword = "";
  isGoogleDriveBackupEnabled: WritableSignal<boolean | undefined> = signal(undefined);
  deleteGoogleDriveBackup: WritableSignal<boolean | undefined> = signal(undefined);
  googleDriveBackupModaleActive = signal(false);
  deleteAccountConfirmationCountdown = signal(5);
  interval: any;
  loadingAccount: WritableSignal<boolean> = signal(true);
  current_email = signal("Loading your current email ...");
  current_username = signal("Loading your current username ...");
  notification_message: WritableSignal<string | undefined> = signal(undefined);



  constructor(
    private http: HttpClient,
    public userService: UserService,
    private utils: Utils,
    private router: Router,
    private route: ActivatedRoute,
    private crypto: Crypto,
    public translate: TranslateService,
    private toastr: ToastrService,
    private vaultService: VaultService,
  ) { }


  ngOnInit(): void {
    if (this.userService.id() == null) {
      this.userService.refresh_user_id().then((success) => {
        console.log("User refreshed successfully.");
      }, (error) => {
        this.router.navigate(["/login/sessionKilled"], { relativeTo: this.route.root });
      });
    }
    this.get_whoami();
    this.get_internal_notification();
  }

  get_whoami() {
    this.http.get("/api/v1/whoami", { withCredentials: true, observe: 'response' }).subscribe({
      next: (response) => {
        this.loadingAccount.set(false);
        const data = JSON.parse(JSON.stringify(response.body))
        this.current_username.set(data.username);
        this.current_email.set(data.email);
      }, error: (error) => {
        if (error.status == 401) {
          this.userService.clear();
          this.router.navigate(["/login/sessionEnd"], { relativeTo: this.route.root });
          return;
        }
        if (error.status == 0) {
          this.translate.get("account.errors.network").subscribe((translation: string) => {
            this.utils.toastError(this.toastr, translation, "")
          });
        } else if (error.status == 403 && error.error.error == "Not verified") {
          this.router.navigate(["/emailVerification"], { relativeTo: this.route.root });
        } else {
          this.translate.get("account.errors.unknown").subscribe((translation: string) => {
            this.utils.toastError(this.toastr, translation, "")
          });
        }
      }
    })
  }

  checkUsername() {
    this.usernameErrorMessage.set("");
    if (this.username == "") {
      this.usernameErrorMessage.set("account.username.error.missing");
      return;
    }
    if (this.username != this.utils.sanitize(this.username)) {
      this.usernameErrorMessage.set("account.username.error.char");
      return;
    }
  }

  updateUsername() {
    this.checkUsername();
    if (this.usernameErrorMessage() == "") {
      this.buttonLoading.username.set(true)
      this.http.put("/api/v1/update/username", { username: this.username }, { withCredentials: true, observe: 'response' }).subscribe({
        next: () => {
          this.buttonLoading.username.set(false)
          this.utils.toastSuccess(this.toastr, this.translate.instant('account.username.success'), "");
          this.get_whoami();

        },
        error: (error) => {
          this.buttonLoading.username.set(false)
          if (error.error.message == undefined) {
            error.error.message = 'account.username.error.unknown';
          }
          this.utils.toastError(this.toastr, "Error : " + this.translate.instant(error.error.message), "");
        },
        complete: () => this.buttonLoading.username.set(false)
      })
    }
  }

  checkEmail() {
    this.emailErrorMessage.set("");
    this.emailConfirmErrorMessage.set("");
    const emailRegex = /\S+@\S+\.\S+/;
    if (!emailRegex.test(this.email)) {
      this.emailErrorMessage.set("account.email.errors.invalid");
      return;
    } if (this.email != this.utils.sanitize(this.email)) {
      this.emailErrorMessage.set("account.email.errors.char");
      return;
    } if (this.email != "" && this.confirmEmail != "" && this.email != this.confirmEmail) {
      this.emailConfirmErrorMessage.set("account.email.errors.match");
      return;
    } else {
      return true;
    }
  }

  updateEmail() {
    if (this.email == "") {
      this.translate.get("signup.errors.missing_fields").subscribe((translation: string) => {
        this.utils.toastError(this.toastr, translation, "")
      });
      return;
    }
    if (!this.checkEmail()) {
      return;
    }
    this.buttonLoading.email.set(true)
    const data = {
      email: this.email
    }
    this.http.put("/api/v1/update/email", data, { withCredentials: true, observe: 'response' }).subscribe({
      next: (response) => {
        this.buttonLoading.email.set(false)
        this.utils.toastSuccess(this.toastr, this.translate.instant('account.email.success'), "");
        this.userService.email.set(JSON.parse(JSON.stringify(response.body))["message"])
        this.get_whoami();
      },
      error: error => {
        this.buttonLoading.email.set(false)
        if (error.error.message == undefined) {
          error.error.message = this.translate.instant('account.email.error');
        }
        this.utils.toastError(this.toastr, "Error : " + error.error.message, "");
      },
      complete: () => this.buttonLoading.email.set(false)
    })
  }

  checkNewPassword() {
    this.newPasswordErrorMessage.set([""]);
    this.newPasswordConfirmErrorMessage.set([""]);
    const special = /[`!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?~]/;
    const upper = /[A-Z]/;
    const number = /[0-9]/;
    const forbidden = /["\'<>]/
    let isOk = true;
    if (forbidden.test(this.newPassword)) {
      this.newPasswordErrorMessage.update(current => [...current, "account.passphrase.error.char"])
      isOk = false;
    }
    if (this.newPassword.length < 12) {
      this.newPasswordErrorMessage.update(current => [...current, "account.passphrase.error.length"]);
      isOk = false;
    }
    if (!special.test(this.newPassword)) {
      this.newPasswordErrorMessage.update(current => [...current, "account.passphrase.error.special"]);
      isOk = false;
    }
    if (!upper.test(this.newPassword)) {
      this.newPasswordErrorMessage.update(current => [...current, "account.passphrase.error.upper"]);
      isOk = false;
    }
    if (!number.test(this.newPassword)) {
      this.newPasswordErrorMessage.update(current => [...current, "account.passphrase.error.number"]);
      isOk = false;
    }
    if (this.newPassword != "" && this.confirmNewPassword != "" && this.newPassword != this.confirmNewPassword) {
      this.newPasswordErrorMessage.update(current => [...current, "account.passphrase.error.match"]);
      isOk = false;
    }
    if (this.password == "" && isOk) {
      this.translate.get("account.passphrase.no_former_passphrase").subscribe((translation: string) => {
        this.utils.toastError(this.toastr, translation, "")
      });
      isOk = false;
    }
    return isOk;
  }


  deleteAccount() {
    this.buttonLoading.deletion.set(true)
    this.deletionErrorMessage.set("");
    this.userService.getUserPreHashedPassphrase(this.password).then(hashed => {
      this.verifyPassword(hashed).then(_ => {
        this.hashedOldPassword = hashed;
        this.sendDeleteAccountRequest().then(_ => {
          this.router.navigate(["/logout"], { relativeTo: this.route.root });
          this.utils.toastSuccess(this.toastr, this.translate.instant("account.delete.success"), "");
        }, error => {
          this.buttonLoading.deletion.set(false)
          this.deletionErrorMessage.set(this.translate.instant("account.delete.error.aborted"));
        });
      }, error => {
        this.buttonLoading.deletion.set(false)
        this.deletionErrorMessage.set(this.translate.instant("account.delete.error.wrong_passphrase"));
      });
    }, error => {
      this.buttonLoading.deletion.set(false)
      switch (error) {
        case UserServiceCommonError.UserNeedToLoginAgain:
          this.router.navigate(["/login/sessionKilled"], { relativeTo: this.route.root });
          break;
        default:
          this.utils.toastError(this.toastr, error, "")
          this.deletionErrorMessage.set(this.translate.instant("account.delete.error.aborted"));
          break;
      }
    });

  }

  updatePassphrase() {
    this.stepsDone.set([""]);
    this.buttonLoading.passphrase.set(false)
    if (!this.checkNewPassword()) {
      return;
    }

    this.passphraseModal();
  }

  getGoogleDriveOption() {
    this.http.get("/api/v1/google-drive/option", { withCredentials: true, observe: 'response' }).subscribe((response) => {
      const data = JSON.parse(JSON.stringify(response.body))
      if (data.status == "enabled") {
        this.isGoogleDriveBackupEnabled.set(true);
        this.googleDriveBackupModaleActive.set(true);
      } else {
        this.isGoogleDriveBackupEnabled.set(false);
        this.updatePassphraseConfirm();
      }
    }, (error) => {
      let errorMessage = "";
      if (error.error.message != null) {
        errorMessage = error.error.message;
      } else if (error.error.detail != null) {
        errorMessage = error.error.detail;
      }
      this.isGoogleDriveBackupEnabled.set(false);
      this.translate.get("account.passphrase.popup.google.fetch_error").subscribe((translation: string) => {
        this.utils.toastError(this.toastr, translation + " " + errorMessage, "");
      });
    });
  }


  deleteAllGoogleDriveBackup(): Promise<boolean> {
    return new Promise<boolean>((resolve, reject) => {
      this.http.delete("/api/v1/google-drive/backup", { withCredentials: true, observe: 'response' }).subscribe({
        next: () => resolve(true),
        error: (error) => {
          let errorMessage = "";
          if (error.error.message != null) {
            errorMessage = error.error.message;
          } else if (error.error.detail != null) {
            errorMessage = error.error.detail;
          }
          this.utils.toastError(this.toastr, this.translate.instant("account.passphrase.popup.google.delete_error") + " " + errorMessage, "");
          reject(error)
        }
      });
    });
  }

  backup(): Promise<boolean> {
    return new Promise<boolean>((resolve, reject) => {
      this.http.put("/api/v1/google-drive/backup", {}, { withCredentials: true, observe: 'response' }).subscribe((response) => {
        resolve(true);
      }, (error) => {
        let errorMessage = "";
        if (error.error.message != null) {
          errorMessage = error.error.message;
        } else if (error.error.detail != null) {
          errorMessage = error.error.detail;
        }
        this.utils.toastError(this.toastr, this.translate.instant("account.passphrase.popup.google.backup_error") + " " + errorMessage, "");
        reject(error)
      });
    });
  }

  updatePassphraseConfirm() {
    if (this.isGoogleDriveBackupEnabled() == undefined) {
      this.getGoogleDriveOption();
      return;
    } else if (this.isGoogleDriveBackupEnabled() && this.deleteGoogleDriveBackup() == undefined) {
      this.googleDriveBackupModaleActive.set(true);
      return;
    }
    this.buttonLoading.passphrase.set(true)
    this.stepsDone.set([""]);
    this.userService.getUserPreHashedPassphrase(this.password).then(hashed => {
      this.verifyPassword(hashed).then(_ => {
        this.hashedOldPassword = hashed;
        this.stepsDone.update(steps => [...steps, "verifyOldPassword"])
        this.userService.getUserZKEKey(this.password).then(zke_result => {
          this.userService.derivedKeySalt.set(zke_result.derivedKeySalt)
          this.userService.zke_key.set(zke_result.zkeKey)
          this.get_all_secret().then(vault => {
            this.stepsDone.update(steps => [...steps, "getVault"])
            const derivedKeySalt = this.crypto.generateRandomSalt();
            this.deriveNewPassphrase(derivedKeySalt).then(derivedKey => {
              const zke_key_str = this.crypto.generateZKEKey();
              this.stepsDone.update(steps => [...steps, "derivation"])
              this.encryptVault(vault, zke_key_str).then(enc_vault => {
                this.crypto.encrypt(zke_key_str, derivedKey).then((enc_zke_key) => {
                  this.stepsDone.update(steps => [...steps, "encryption"])
                  this.verifyEncryption(derivedKey, enc_zke_key, enc_vault, vault).then(_ => {
                    this.stepsDone.update(steps => [...steps, "verification"])
                    this.uploadNewVault(enc_vault, enc_zke_key, derivedKeySalt).then(_ => {
                      this.stepsDone.update(steps => [...steps, "upload"])
                      if (this.isGoogleDriveBackupEnabled() && this.deleteGoogleDriveBackup()) {
                        this.deleteAllGoogleDriveBackup().then(_ => {
                          this.stepsDone.update(steps => [...steps, "deleteBackup"])
                          if (this.isGoogleDriveBackupEnabled()) {
                            this.backup().then(_ => {
                              this.stepsDone.update(steps => [...steps, "backup"])
                              this.utils.toastSuccess(this.toastr, this.translate.instant("account.passphrase.popup.updating.success"), "");
                              this.router.navigate(["/login"], { relativeTo: this.route.root });
                            }, error => {
                              this.updateAbortedWithSuccess('#8 Backup of your vault on Google drive. Reason : ' + error)
                              this.router.navigate(["/login"], { relativeTo: this.route.root });
                            });
                          }
                          this.utils.toastSuccess(this.toastr, this.translate.instant("account.passphrase.popup.updating.success"), "");
                          this.router.navigate(["/login"], { relativeTo: this.route.root });
                        }, error => {
                          this.updateAbortedWithSuccess('#7 Deletion of your all google drive backup. Reason : ' + error)
                          this.router.navigate(["/login"], { relativeTo: this.route.root });
                        });
                      } else {
                        if (this.isGoogleDriveBackupEnabled()) {
                          this.backup().then(_ => {

                            this.stepsDone.update(steps => [...steps, "backup"])
                            this.utils.toastSuccess(this.toastr, this.translate.instant("account.passphrase.popup.updating.success"), "");
                            this.router.navigate(["/login"], { relativeTo: this.route.root });
                          }, error => {
                            this.updateAbortedWithSuccess('#8 Backup of your vault on Google drive. . Reason : ' + error.message)
                            this.router.navigate(["/login"], { relativeTo: this.route.root });
                          });
                        } else {
                          this.utils.toastSuccess(this.toastr, this.translate.instant("account.passphrase.popup.updating.success"), "");
                          this.router.navigate(["/login"], { relativeTo: this.route.root });
                        }
                      }
                    }, error => {
                      this.buttonLoading.passphrase.set(false)
                    });
                  }, error => {
                    this.updateAborted('#6. Reason : ' + error)
                  });
                }, error => {
                  console.log(error)
                  this.updateAborted('#5')
                });
              }, error => {
                this.updateAborted('#4')
              });
            }, error => {
              this.updateAborted('#3')
            });
          }, error => {
            this.updateAborted('#2')
          });
        }, error => {
          this.updateAborted("#2")
        });
      });
    }, error => {
      this.updateAborted('#1')
    });
  }

  updateAborted(errorCode: string) {
    this.buttonLoading.passphrase.set(false)
    this.utils.toastError(this.toastr, this.translate.instant("account.passphrase.error.full_abort") + " " + errorCode, "");
  }

  updateAbortedWithSuccess(errorCode: string) {
    this.buttonLoading.passphrase.set(false)
    this.utils.toastWarning(this.toastr, this.translate.instant("account.passphrase.error.light_abort") + " " + errorCode, "");
  }




  verifyPassword(hashedPassword: string): Promise<string> {
    return new Promise<string>((resolve, reject) => {
      const data = {
        email: this.userService.email(),
        password: hashedPassword
      }
      this.http.post("/api/v1/login", data, { withCredentials: true, observe: 'response' }).subscribe({
        next: () => resolve("ok"),
        error: (error) => {
          this.utils.toastError(this.toastr, this.translate.instant("account.passphrase.error.incorrect"), "");
          this.buttonLoading.passphrase.set(false)
          reject(error)
        }
      });
    });
  }


  get_all_secret(): Promise<Map<string, TOTPEntry>> {
    return new Promise<Map<string, TOTPEntry>>((resolve, reject) => {
      if (this.userService.zke_key() == null) {
        console.log("zke key is null")
        this.router.navigate(["/login/sessionKilled"], { relativeTo: this.route.root });
        reject("zke key is null")
      }
      this.userService.getUserEncryptedVault().then(encrypted_vault => {
        this.vaultService.decryptVault(encrypted_vault, this.userService.zke_key()!).then(result => {
          if (result.errors.length != 0) {
            const errors = result.errors.join(". ")
            this.translate.get("vault.error.decryption").subscribe((translation: string) => {
              this.utils.toastError(this.toastr, translation, errors);
            });
            reject(errors)
          }
          resolve(result.vault)
        },
          error => {
            this.translate.get("vault.error.decryption").subscribe((translation: string) => {
              this.utils.toastError(this.toastr, translation, error);
            });
          })
      })
    });
  }

  deriveNewPassphrase(newDerivedKeySalt: string): Promise<CryptoKey> {
    return new Promise<CryptoKey>((resolve, reject) => {
      this.crypto.deriveKey(newDerivedKeySalt, this.newPassword).then((derivedKey) => {
        resolve(derivedKey);
      }, error => {
        this.translate.get("account.passphrase.error.derive").subscribe((translation: string) => {
          this.utils.toastError(this.toastr, translation, "");
          reject(error)
        });
      });
    });
  }

  encryptVault(vault: Map<string, TOTPEntry>, zkeKey_str: string): Promise<Map<string, string>> {
    return new Promise<Map<string, string>>((resolve, reject) => {
      try {
        const zke_key_raw = Buffer.from(zkeKey_str, "base64");
        window.crypto.subtle.importKey(
          "raw",
          zke_key_raw,
          "AES-GCM",
          true,
          ["encrypt", "decrypt"]
        ).then((zke_key) => {
          const enc_vault = new Map<string, string>();
          for (let [uuid, property] of vault) {
            try {
              this.crypto.encrypt(this.userService.TOTPEntryToJSON(property), zke_key).then(enc_property => {
                enc_vault.set(uuid, enc_property);
              });
            } catch (e) {
              this.utils.toastError(this.toastr, this.translate.instant("account.passphrase.error.decrypt"), "");
              reject(e)
            }
          }
          resolve(enc_vault);
        });
      } catch (e) {
        console.log(e)
      }
    });
  }


  verifyEncryption(derivedKey: CryptoKey, zke_enc: string, enc_vault: Map<string, string>, vault: Map<string, TOTPEntry>): Promise<string> {
    return new Promise<string>((resolve, reject) => {
      this.crypto.decrypt(zke_enc, derivedKey).then((zke_key_str) => {
        if (zke_key_str != null) {
          const zke_key_raw = Buffer.from(zke_key_str!, 'base64');
          try {
            window.crypto.subtle.importKey(
              "raw",
              zke_key_raw,
              "AES-GCM",
              true,
              ["encrypt", "decrypt"]
            ).then((zke_key) => {
              try {
                for (let uuid of enc_vault.keys()) {
                  if (enc_vault.get(uuid) != undefined) {
                    this.crypto.decrypt(enc_vault.get(uuid)!, zke_key).then((dec_secret) => {
                      if (dec_secret == null) {
                        reject("dec_secret is null");
                      } else {
                        try {
                          const secret = this.userService.TOTPEntryFromJSON(dec_secret).secret;
                          if (secret != vault.get("uuid")!.secret) {
                            reject("secret is different")
                          }
                        } catch (e) {
                          reject(e)
                        }
                      }
                    })
                  } else {
                    reject("enc_vault.get(uuid) is undefined")
                  }
                }
                resolve("ok")
              } catch (e) {
                reject(e)
              }
            });
          } catch (e) {
            reject(e)
          }

        } else {
          reject("zke_key_str is null")
        }
      });
    });

  }

  uploadNewVault(enc_vault: Map<string, string>, zke_enc: string, derivedKeySalt: string): Promise<string> {
    return new Promise<string>((resolve, reject) => {
      const salt = this.crypto.generateRandomSalt();
      this.crypto.hashPassphrase(this.newPassword, salt).then(hashed => {
        const data = {
          enc_vault: JSON.stringify(enc_vault),
          old_passphrase: this.hashedOldPassword,
          new_passphrase: hashed,
          zke_enc: zke_enc,
          passphrase_salt: salt,
          derived_key_salt: derivedKeySalt
        }
        this.http.put("/api/v1/update/vault", data, { withCredentials: true, observe: 'response' }).subscribe({
          next: () => {
            resolve("ok");
          }, error: (error) => {
            if (error.status == 500) {
              if (error.error.hashing == 1) {
                this.utils.toastError(this.toastr, this.translate.instant('account.passphrase.error.hash_new'), "");
                reject(error.status)
              } else {
                this.translate.get("account.passphrase.error.fatal").subscribe((translation: string) => {
                  this.utils.toastError(this.toastr, translation, error.error.message);
                });
                reject(error.status)
              }
              resolve("ok");
            } else {
              this.utils.toastError(this.toastr, this.translate.instant("account.passphrase.error.fatal_light") + error.status + " " + error.error.message, "");
              reject(error.status)
            }
          }
        });
      });
    });
  }

  sendDeleteAccountRequest(): Promise<string> {
    return new Promise<string>((resolve, reject) => {
      let headers = new HttpHeaders().set('x-hash-passphrase', this.hashedOldPassword);
      this.http.delete("/api/v1/account", { headers: headers, withCredentials: true, observe: 'response' }).subscribe({
        next: () => {
          resolve("ok")
        },
        error: (error) => {
          let errorMessage = "";
          if (error.error.message != null) {
            errorMessage = error.error.message;
          } else if (error.error.detail != null) {
            errorMessage = error.error.detail;
          }
          this.utils.toastError(this.toastr, errorMessage, "");
          reject(errorMessage)
        }
      });
    });

  }

  get_internal_notification() {
    this.http.get("/api/v1/notification/internal", { withCredentials: true, observe: 'response' }).subscribe({
      next: (response) => {
        if (response.status == 200) {
          try {
            const data = JSON.parse(JSON.stringify(response.body))
            if (data.display_notification) {
              this.notification_message.set(data.message);
            }
          } catch (error) {
            console.log(error);
          }
        }
      },
      error: (error) => {
        console.log(error);
      }
    });
  }





  deletionModal() {
    if (!this.buttonLoading.deletion()) {
      this.deleteAccountConfirmationCountdown.set(5);
      if (!this.isDeletionModalActive()) {
        this.startTimer();
      } else {
        this.pauseTimer();
      }
      this.isDeletionModalActive.update(isDeletionModalActive => !isDeletionModalActive);
    }
  }

  startTimer() {
    this.deleteAccountConfirmationCountdown.set(5);
    this.interval = setInterval(() => {
      if (this.deleteAccountConfirmationCountdown() > 0) {
        this.deleteAccountConfirmationCountdown.update(current => current - 1)
      } else {
        clearInterval(this.interval);
      }
    }, 1000)
  }

  pauseTimer() {
    clearInterval(this.interval);
  }

  passphraseModal() {
    if (!this.buttonLoading.passphrase()) {
      this.isPassphraseModalActive.update(isPassphraseModalActive => !isPassphraseModalActive);
    }
  }

}


