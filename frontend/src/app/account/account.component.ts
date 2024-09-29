import { Component, OnInit } from '@angular/core';
import { faEnvelope, faLock,  faCheck, faUser, faCog, faShield, faHourglassStart, faCircleInfo, faArrowsRotate, faFlask, faTrash,faVault, faExclamationTriangle, faEye, faEyeSlash, faCircleExclamation, faCircleNotch,faLightbulb } from '@fortawesome/free-solid-svg-icons';
import { UserService } from '../common/User/user.service';
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { Utils } from '../common/Utils/utils';
import { ActivatedRoute, Router } from '@angular/router';
import { Crypto } from '../common/Crypto/crypto';
import { Buffer } from 'buffer';
import { TranslateService } from '@ngx-translate/core';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-account',
  templateUrl: './account.component.html',
  styleUrls: ['./account.component.css']
})
export class AccountComponent implements OnInit {
  faUser=faUser;
  faEnvelope=faEnvelope;
  faLock=faLock;
  faShield=faShield;
  faCircleInfo=faCircleInfo;
  faArrowsRotate=faArrowsRotate;
  faHourglassStart=faHourglassStart;
  faCircleExclamation=faCircleExclamation;
  faCircleNotch=faCircleNotch;
  faExclamationTriangle=faExclamationTriangle;
  faCheck=faCheck;
  faCog=faCog;
  faLightbulb=faLightbulb;
  faFlask=faFlask;
  faTrash=faTrash;
  faEye=faEye;
  faEyeSlash=faEyeSlash;
  isNewConfirmPassphraseVisible = false;
  isNewPassphraseVisible = false;
  isPassphraseVisible = false;
  faVault=faVault;
  isDeletionModalActive=false;
  isPassphraseModalActive=false;
  buttonLoading = {"email":0, "username":0, "passphrase":0, "deletion":0}
  username:string="";
  usernameErrorMessage="";
  email:string="";
  confirmEmail:string="";
  emailErrorMessage="";
  emailConfirmErrorMessage="";
  newPassword="";
  confirmNewPassword="";
  newPasswordErrorMessage : [string]=[""];
  newPasswordConfirmErrorMessage : [string]=[""];
  stepsDone: Array<String> =[""];
  deletionErrorMessage=""
  password="";
  hashedOldPassword="";
  isGoogleDriveBackupEnabled: boolean | undefined= undefined;
  deleteGoogleDriveBackup: boolean | undefined= undefined;
  googleDriveBackupModaleActive = false;
  deleteAccountConfirmationCountdown = 5;
  interval: any;
  accountLoadingError="";
  accountLoadingErrorMessage="";
  loadingAccount=true;
  current_email="";
  current_username="";
  notification_message:string|undefined;
  constructor(
    private http: HttpClient,
    public userService: UserService,
    private utils: Utils,
    private router: Router,
    private route: ActivatedRoute,
    private crypto:Crypto,
    public translate: TranslateService,
    private toastr: ToastrService,
    ){}

  
  ngOnInit(): void {
     if(this.userService.getId() == null){
      this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
       if("email" in this.buttonLoading){
       }
    }
    this.get_whoami();
    this.get_internal_notification();
  }

  get_whoami(){
    this.http.get("/api/v1/whoami",  {withCredentials:true, observe: 'response'}).subscribe((response) => {
      this.loadingAccount = false;
      const data = JSON.parse(JSON.stringify(response.body))
      this.current_username = data.username;
      this.current_email = data.email;
    }, (error) => {
      this.loadingAccount = false;
      if(error.status == 401){
        this.userService.clear();
        this.router.navigate(["/login/sessionEnd"], {relativeTo:this.route.root});
        return;
      }
      if(error.status == 0){
        this.accountLoadingError = "account.errors.network";
      } else if(error.status == 403 && error.error.error =="Not verified"){
        this.accountLoadingError = "account.errors.not_found";
        this.router.navigate(["/emailVerification"], {relativeTo:this.route.root});
      } else {
        this.accountLoadingError = "account.errors.unknown";
        this.accountLoadingErrorMessage = error.status + " "+ error.message + " "+ error.error.message;
      }
    });
  }

  checkUsername(){
  this.usernameErrorMessage = "";
  if(this.username == ""){
    this.usernameErrorMessage = "account.username.error.missing";
    return;
  }
  if(this.username != this.utils.sanitize(this.username)){
    this.usernameErrorMessage = "account.username.error.char";
      return;
    }
  }

  updateUsername(){
    this.checkUsername();
    if(this.usernameErrorMessage == ""){
      this.buttonLoading["username"] = 1
      this.http.put("/api/v1/update/username",  {username: this.username}, {withCredentials: true, observe: 'response'}).subscribe((response) => {
        this.buttonLoading["username"] = 0
        this.utils.toastSuccess(this.toastr, this.translate.instant('account.username.success'), "");
        this.get_whoami();
        
      }, error =>{
        this.buttonLoading["username"] = 0
        if(error.error.message == undefined){
          error.error.message = 'account.username.error.unknown';
        }
        this.utils.toastError(this.toastr,"Error : "+this.translate.instant(error.error.message),"");
      });
    }
  }

  checkEmail(){
    this.emailErrorMessage = "";
    this.emailConfirmErrorMessage="";
    const emailRegex = /\S+@\S+\.\S+/;
    if(!emailRegex.test(this.email)){
      this.emailErrorMessage = "account.email.errors.invalid" ;
      return;
    } if(this.email != this.utils.sanitize(this.email)) {
      this.emailErrorMessage ="account.email.errors.char";
      return;
    } if(this.email != "" && this.confirmEmail != "" && this.email != this.confirmEmail) {
      this.emailConfirmErrorMessage = "account.email.errors.match";
      return;
    } else {
      return true;
    }
  }

  updateEmail(){
    if(this.email == ""){
      this.translate.get("signup.errors.missing_fields").subscribe((translation: string) => {
      this.utils.toastError(this.toastr,translation,"")
    });
      return;
    }
    if(!this.checkEmail()){
      return;
    }
    this.buttonLoading["email"] = 1
    const data = {
      email: this.email
    }
    this.http.put("/api/v1/update/email",  data, {withCredentials: true, observe: 'response'}).subscribe((response) => {
      this.buttonLoading["email"] = 0
      this.utils.toastSuccess(this.toastr, this.translate.instant('account.email.success'),"");
      this.userService.setEmail(JSON.parse(JSON.stringify(response.body))["message"])
      this.get_whoami();
    }, error =>{
      this.buttonLoading["email"] = 0
      if(error.error.message == undefined){
        error.error.message = this.translate.instant('account.email.error');
      }
      this.utils.toastError(this.toastr, "Error : "+ error.error.message,"");
    });
  }

  checkNewPassword(){
    this.newPasswordErrorMessage=[""];
    this.newPasswordConfirmErrorMessage=[""];
    const special = /[`!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?~]/;
    const upper = /[A-Z]/;
    const number = /[0-9]/;
    const forbidden = /["\'<>]/
    let isOk = true;
    if(this.password == ""){
      this.translate.get("account.passphrase.no_former_passphrase").subscribe((translation: string) => {
      this.utils.toastError(this.toastr,translation,"")
    });
      isOk = false;
    }
    if(forbidden.test(this.newPassword)){
      this.newPasswordErrorMessage.push("account.passphrase.error.char");
      isOk = false;
    }
    if(this.newPassword.length < 12){
      this.newPasswordErrorMessage.push("account.passphrase.error.length");
      isOk = false;
    }
    if(!special.test(this.newPassword)){
      this.newPasswordErrorMessage.push("account.passphrase.error.special");
      isOk = false;
    }
    if(!upper.test(this.newPassword)){
      this.newPasswordErrorMessage.push("account.passphrase.error.upper");
      isOk = false;
    }
    if(!number.test(this.newPassword)){
      this.newPasswordErrorMessage.push("account.passphrase.error.number");
      isOk = false;
    }
    if(this.newPassword != "" && this.confirmNewPassword != "" && this.newPassword != this.confirmNewPassword){
      this.newPasswordConfirmErrorMessage.push("account.passphrase.error.match");
      isOk = false;
    }
    return isOk;
  }


  deleteAccount(){
    this.buttonLoading['deletion'] =1
    this.deletionErrorMessage = "";
    this.hashPassword().then(hashed => {
      this.verifyPassword(hashed).then(_ => {
        this.hashedOldPassword = hashed;
        this.sendDeleteAccountRequest().then(_ => {
          this.router.navigate(["/logout"], {relativeTo:this.route.root});
          this.utils.toastSuccess(this.toastr, this.translate.instant("account.delete.success"),"");
        }, error => {
          this.buttonLoading['deletion'] =0
        this.deletionErrorMessage = this.translate.instant("account.delete.error.aborted") ;
        });
      }, error => {
        this.buttonLoading['deletion'] =0
        this.deletionErrorMessage = this.translate.instant("account.delete.error.wrong_passphrase") ;
      });
    }, error => {
      this.buttonLoading['deletion'] =0
      this.deletionErrorMessage = this.translate.instant("account.delete.error.aborted") ;
    });

  }

  updatePassphrase(){
    this.stepsDone=[""];
    this.buttonLoading["passphrase"] = 0
    if(!this.checkNewPassword()){
      return;
    }

    this.passphraseModal();
  }

  getGoogleDriveOption(){
      this.http.get("/api/v1/google-drive/option",  {withCredentials:true, observe: 'response'}).subscribe((response) => { 
        const data = JSON.parse(JSON.stringify(response.body))
        if(data.status == "enabled"){
          this.isGoogleDriveBackupEnabled = true;
          this.googleDriveBackupModaleActive = true;
        } else {
          this.isGoogleDriveBackupEnabled = false;
          this.updatePassphraseConfirm();
        }
      }, (error) => {
          let errorMessage = "";
          if(error.error.message != null){
            errorMessage = error.error.message;
          } else if(error.error.detail != null){
            errorMessage = error.error.detail;
          }
          this.isGoogleDriveBackupEnabled = false;
          this.translate.get("account.passphrase.popup.google.fetch_error").subscribe((translation: string) => {
            this.utils.toastError(this.toastr, translation + " " + errorMessage,"");
        });
      });
  }


  deleteAllGoogleDriveBackup(): Promise<boolean>{
    return new Promise<boolean>((resolve, reject) => {
      this.http.delete("/api/v1/google-drive/backup",  {withCredentials:true, observe: 'response'}).subscribe((response) => {
        resolve(true);
      }, (error) => {
        let errorMessage = "";
        if(error.error.message != null){
          errorMessage = error.error.message;
        } else if(error.error.detail != null){
          errorMessage = error.error.detail;
        }
        this.utils.toastError(this.toastr, this.translate.instant("account.passphrase.popup.google.delete_error") + " " + errorMessage,"");
        reject(error)
      });
    });
  }

  backup(): Promise<boolean>{
    return new Promise<boolean>((resolve, reject) => {
      this.http.put("/api/v1/google-drive/backup",  {}, {withCredentials:true, observe: 'response'}).subscribe((response) => {
        resolve(true);
      }, (error) => {
        let errorMessage = "";
        if(error.error.message != null){
          errorMessage = error.error.message;
        } else if(error.error.detail != null){
          errorMessage = error.error.detail;
        }
        this.utils.toastError(this.toastr,this.translate.instant("account.passphrase.popup.google.backup_error") + " "+ errorMessage,"");
        reject(error)
      });
    });
  }

  updatePassphraseConfirm(){
    if(this.isGoogleDriveBackupEnabled == undefined){
      this.getGoogleDriveOption();
      return;
    } else if (this.isGoogleDriveBackupEnabled == true && this.deleteGoogleDriveBackup == undefined){
      this.googleDriveBackupModaleActive = true;
      return;
    }
    this.buttonLoading["passphrase"] = 1
    this.stepsDone = [""];
    this.hashPassword().then(hashed => {
      this.verifyPassword(hashed).then(_ => {
        this.hashedOldPassword = hashed;
          this.stepsDone.push("verifyOldPassword");
          this.get_all_secret().then(vault => {
            this.stepsDone.push("getVault");
            const derivedKeySalt = this.crypto.generateRandomSalt();
            this.deriveNewPassphrase(derivedKeySalt).then(derivedKey => {
              const zke_key_str = this.crypto.generateZKEKey();
              this.stepsDone.push("derivation");
                this.encryptVault(vault, zke_key_str).then(enc_vault => {
                  this.crypto.encrypt(zke_key_str , derivedKey).then((enc_zke_key) => {
                    this.stepsDone.push("encryption");
                    this.verifyEncryption(derivedKey, enc_zke_key, enc_vault, vault).then(_ => {
                      this.stepsDone.push("verification");
                      this.uploadNewVault(enc_vault, enc_zke_key, derivedKeySalt).then(_ => {
                        this.stepsDone.push("upload");
                            if(this.isGoogleDriveBackupEnabled  && this.deleteGoogleDriveBackup){
                              this.deleteAllGoogleDriveBackup().then(_ => {
                                this.stepsDone.push("deleteBackup");
                                if(this.isGoogleDriveBackupEnabled){
                                  this.backup().then(_ => {
                                    this.stepsDone.push("backup");
                                    this.utils.toastSuccess(this.toastr, this.translate.instant("account.passphrase.popup.updating.success") ,"");
                                    this.router.navigate(["/login"], {relativeTo:this.route.root});
                                  }, error =>{
                                    this.updateAborted('#8. Reason : '+error)
                                  });
                                }
                                this.utils.toastSuccess(this.toastr,this.translate.instant("account.passphrase.popup.updating.success") ,"");
                                this.router.navigate(["/login"], {relativeTo:this.route.root});
                              }, error =>{
                                this.updateAborted('#7. Reason : '+error)
                              });
                            } else {
                              if(this.isGoogleDriveBackupEnabled){
                                this.backup().then(_ => {
                                  this.stepsDone.push("backup");
                                  this.utils.toastSuccess(this.toastr, this.translate.instant("account.passphrase.popup.updating.success") ,"");
                                  this.router.navigate(["/login"], {relativeTo:this.route.root});
                                }, error =>{
                                  this.updateAborted('#8. Reason : '+error)
                                });
                              } else {
                                this.utils.toastSuccess(this.toastr, this.translate.instant("account.passphrase.popup.updating.success") ,"");
                                this.router.navigate(["/login"], {relativeTo:this.route.root});
                              }
                            }
                      }, error =>{
                        this.buttonLoading["passphrase"] = 0
                      });
                    }, error =>{
                      this.updateAborted('#6. Reason : '+error)
                    });
                  }, error =>{
                    console.log(error)
                    this.updateAborted('#5')
                  });
                }, error =>{
                  this.updateAborted('#4')
                });
            }, error =>{
              this.updateAborted('#3')
            });
          }, error =>{
            this.updateAborted('#2')
          });
        });
      }, error => {
        this.updateAborted('#1')
      });
  }

  updateAborted(errorCode: string){
    this.buttonLoading["passphrase"] = 0
    this.utils.toastError(this.toastr, this.translate.instant("account.passphrase.error.full_abort") + " " + errorCode,"");
  }



  hashPassword(): Promise<string>{
    return new Promise<string>((resolve, reject) => {
    const salt = this.userService.getPassphraseSalt();
    if (salt == null){
      this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
    } else {
      this.crypto.hashPassphrase(this.password, salt).then  (hashed => {
        if(hashed != null){
            resolve(hashed);
        } else {
          this.utils.toastError(this.toastr, this.translate.instant("account.passphrase.error.hashing"),"");
            reject("hashed is null");
        }
      });
      }
    });
  }

  verifyPassword(hashedPassword:string):Promise<string>{
    return new Promise<string>((resolve, reject) => {
      const data = {
      email: this.userService.getEmail()!,
      password: hashedPassword
    }
      this.http.post("/api/v1/login",  data, {withCredentials: true, observe: 'response'}).subscribe((response) => {
      resolve("ok");
      },
     (error) => {
      this.utils.toastError(this.toastr,this.translate.instant("account.passphrase.error.incorrect"),"");
       this.buttonLoading["passphrase"] = 0
       reject(error)
     });
    });
  }


  get_all_secret():Promise<Map<string, Map<string,string>>>{
    return new Promise<Map<string, Map<string,string>>>((resolve, reject) => {
      let vault = new Map<string, Map<string,string>>();
      this.http.get("/api/v1/all_secrets",  {withCredentials:true, observe: 'response'}).subscribe((response) => {
        try{
          const data = JSON.parse(JSON.stringify(response.body))
         if(this.userService.get_zke_key() != null){
          try{
            for (let secret of data.enc_secrets){
              this.crypto.decrypt(secret.enc_secret, this.userService.get_zke_key()!).then((dec_secret)=>{
                if(dec_secret == null){
                  this.utils.toastError(this.toastr,this.translate.instant("account.passphrase.error.wrong_key"),"");
                  reject("dec_secret is null");
                } else {
                    try{
                      vault.set(secret.uuid, this.utils.mapFromJson(dec_secret));
                    } catch(e) {
                      this.utils.toastError(this.toastr,this.translate.instant("account.passphrase.error.decrypt_one_secret"), "");
                      reject(e)
                    }
                  }
              })
            }
            resolve(vault)
          } catch(e) {
            this.utils.toastError(this.toastr,this.translate.instant("account.passphrase.error.wrong_key_vault"),"");
            reject(e)
          }
        } else {
          this.utils.toastError(this.toastr, this.translate.instant("account.passphrase.error.expired") ,"");
          reject("zke_key is null");
        }
        } catch(e){
          this.utils.toastError(this.toastr, this.translate.instant("account.passphrase.error.fetch_vault"),"");
          reject(e)
        }
      }, (error) => {
        if(error.status == 404){
          this.userService.setVault(new Map<string, Map<string,string>>());
        } else {
          let errorMessage = "";
          if(error.error.message != null){
            errorMessage = error.error.message;
          } else if(error.error.detail != null){
            errorMessage = error.error.detail;
          }
          if(error.status == 0){
            errorMessage = this.translate.instant("account.passphrase.error.network");
          } else if (error.status == 401){
            this.userService.clear();
            this.router.navigate(["/login/sessionEnd"], {relativeTo:this.route.root});
            return;
          }

          this.utils.toastError(this.toastr, this.translate.instant("account.passphrase.error.fetch_vault") + " "+ errorMessage,"");
          reject(error)
        }
      });
  });
}

deriveNewPassphrase(newDerivedKeySalt:string):Promise<CryptoKey>{
  return new Promise<CryptoKey>((resolve, reject) => {
    this.crypto.deriveKey(newDerivedKeySalt, this.newPassword).then((derivedKey) => {
      resolve(derivedKey);
    }, error => {
      this.translate.get("account.passphrase.error.derive").subscribe((translation: string) => {
        this.utils.toastError(this.toastr, translation,"");
      reject(error)
    });
  });
    });
}

  encryptVault(vault:Map<string, Map<string,string>>, zkeKey_str: string):Promise<Map<string, string>>{
    return new Promise<Map<string, string>>((resolve, reject) => {
      try{
      const zke_key_raw = Buffer.from(zkeKey_str, "base64");
      window.crypto.subtle.importKey(
        "raw",
        zke_key_raw,
        "AES-GCM",
        true,
        ["encrypt", "decrypt"]
      ).then((zke_key)=>{
      const enc_vault = new Map<string, string>();
      for(let [uuid, property] of vault){
        try{
          this.crypto.encrypt(this.utils.mapToJson(property), zke_key).then(enc_property => {
            enc_vault.set(uuid, enc_property);
          });
        } catch(e) {
          this.utils.toastError(this.toastr,this.translate.instant("account.passphrase.error.decrypt"),"");
          reject(e)
        }
      }
      resolve(enc_vault);
    });
  } catch(e){
    console.log(e)
  }
  });
  }


  verifyEncryption(derivedKey:CryptoKey, zke_enc:string, enc_vault: Map<string, string>, vault:Map<string, Map<string,string>>):Promise<string>{
    return new Promise<string>((resolve, reject) => {
     this.crypto.decrypt(zke_enc, derivedKey).then((zke_key_str) => {
      if(zke_key_str != null){
        const zke_key_raw = Buffer.from(zke_key_str!, 'base64');
          try{
          window.crypto.subtle.importKey(
            "raw",
            zke_key_raw,
            "AES-GCM",
            true,
            ["encrypt", "decrypt"]
          ).then((zke_key)=>{
          try {
            for (let uuid of enc_vault.keys()){
              if(enc_vault.get(uuid) != undefined){
              this.crypto.decrypt(enc_vault.get(uuid)!, zke_key).then((dec_secret)=>{
                if(dec_secret == null){
                  reject("dec_secret is null");
                } else {
                  try{
                    const secret = this.utils.mapFromJson(dec_secret).get("secret");
                    if(secret != vault.get("uuid")!.get("secret")){
                      reject("secret is different")
                    }
                  } catch(e) {
                    reject(e)
                  }
                  }
              })
            }else {
              reject("enc_vault.get(uuid) is undefined")
            }
          } 
          resolve("ok")
          } catch(e){
            reject(e)
          }
        });
      } catch(e){
        reject(e)
      }

      } else {
        reject("zke_key_str is null")
      }
     });
    });

  }

  uploadNewVault(enc_vault: Map<string, string>, zke_enc:string, derivedKeySalt:string):Promise<string>{
    return new Promise<string>((resolve, reject) => {
      const salt = this.crypto.generateRandomSalt();
      this.crypto.hashPassphrase(this.newPassword, salt).then  (hashed => {
      const data = {
        enc_vault: this.utils.mapToJson(enc_vault),
        old_passphrase: this.hashedOldPassword,
        new_passphrase : hashed,
        zke_enc: zke_enc,
        passphrase_salt: salt,
        derived_key_salt: derivedKeySalt
      }
      this.http.put("/api/v1/update/vault",  data, {withCredentials: true, observe: 'response'}).subscribe((response) => {
        resolve("ok");
      }, error =>{
        if(error.status == 500){
          if (error.error.hashing == 1){
            this.utils.toastError(this.toastr, this.translate.instant('account.passphrase.error.hash_new') ,"");
            reject(error.status)
          } else {
            this.translate.get("account.passphrase.error.fatal").subscribe((translation: string) => {
              this.utils.toastError(this.toastr,translation +error.error.totp +" "+ error.error.zke + error.error.user ,"");
          });
            reject(error.status)
          }
          resolve("ok");
        } else {
          this.utils.toastError(this.toastr,this.translate.instant("account.passphrase.error.fatal_light") + error.status +" "+ error.error.message,"");
          reject(error.status)
        }
      });
    });
  });
  }

  sendDeleteAccountRequest(): Promise<string>{
    return new Promise<string>((resolve, reject) => {
      let headers = new HttpHeaders().set('x-hash-passphrase', this.hashedOldPassword);
      this.http.delete("/api/v1/account",  {headers:headers, withCredentials:true, observe: 'response'}).subscribe((response) => {

       resolve("ok")
      }, (error) => {
        let errorMessage = "";
        if(error.error.message != null){
          errorMessage = error.error.message;
        } else if(error.error.detail != null){
          errorMessage = error.error.detail;
        }
        this.utils.toastError(this.toastr, errorMessage,"");
        reject(errorMessage)
      });
    });

  }

  get_internal_notification(){
    this.http.get("/api/v1/notification/internal",  {withCredentials:true, observe: 'response'}).subscribe((response) => {
      if(response.status == 200){
        try{
          const data = JSON.parse(JSON.stringify(response.body))
          if (data.display_notification){
            this.notification_message = data.message;
          }
        } catch (error){
          console.log(error);
        }
      }
    }, (error) => {
      console.log(error);
    });
  }





  deletionModal(){
    if(!this.buttonLoading["deletion"]){
      this.deleteAccountConfirmationCountdown = 5;
      if(!this.isDeletionModalActive){
        this.startTimer();
      } else {
        this.pauseTimer();
      }
      this.isDeletionModalActive = !this.isDeletionModalActive;
    }
  }

  startTimer() {
    this.deleteAccountConfirmationCountdown = 5;
    this.interval = setInterval(() => {
      if(this.deleteAccountConfirmationCountdown > 0) {
        this.deleteAccountConfirmationCountdown--;
      } else {
        clearInterval(this.interval);
      }
    },1000)
  }

  pauseTimer() {
    clearInterval(this.interval);
  }

  passphraseModal(){
    if(!this.buttonLoading["passphrase"]){
      this.isPassphraseModalActive = !this.isPassphraseModalActive;
    }
  }

}


