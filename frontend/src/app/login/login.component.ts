import { Component,OnInit } from '@angular/core';
import { toast as superToast } from 'bulma-toast'
import { faEnvelope, faLock,  faCheck, faXmark, faFlagCheckered, faCloudArrowUp, faBriefcaseMedical, faEye, faEyeSlash, faKey } from '@fortawesome/free-solid-svg-icons';
import { HttpClient } from '@angular/common/http';
import { ApiService } from '../common/ApiService/api-service';
import { Router, ActivatedRoute } from '@angular/router';
import { UserService } from '../common/User/user.service';
import {Crypto} from '../common/Crypto/crypto';
import { Buffer } from 'buffer';
import { LocalVaultV1Service, UploadVaultStatus } from '../common/upload-vault/LocalVaultv1Service.service';
import { TranslateService } from '@ngx-translate/core';
import { error } from 'console';
@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  faEnvelope=faEnvelope;
  faLock=faLock;
  faCheck=faCheck;
  faXmark=faXmark;
  faKey=faKey;
  faFlagCheckered=faFlagCheckered;
  faCloudArrowUp=faCloudArrowUp;
  faEye=faEye;
  faEyeSlash=faEyeSlash;
  email:string = "";
  faBriefcaseMedical=faBriefcaseMedical;
  password:string = "";
  hashedPassword:string = "";
  isLoading = false;
  warning_message="";
  warning_message_color="is-warning";
  error_param: string|null=null;
  isUnsecureVaultModaleActive = false;
  isPassphraseModalActive = false;
  local_vault_service: LocalVaultV1Service | null = null;
  is_oauth_flow=false;
  login_button="login.open_button"
  isPassphraseVisible=false;
  isLocalVaultPassphraseVisible=false;

  constructor(
    private http: HttpClient,
    private router: Router,
    private route: ActivatedRoute,
    private userService: UserService,
    private crypto:Crypto,
    private localVaultv1: LocalVaultV1Service,
    private translate: TranslateService
    ) {
    }

    ngOnInit(){
      this.error_param = this.route.snapshot.paramMap.get('error_param')
      switch(this.error_param){
        case null:{
          break;
        }
        case 'sessionKilled':{
            this.warning_message = 'login.errors.session_killed';
          this.email = this.userService.getEmail() || "";
          this.userService.clear();
          break;
        }
        case 'sessionTimeout':{
            this.warning_message = 'login.errors.session_timeout';
          this.email = this.userService.getEmail() || "";
          this.userService.clear();
          break;
        }

        case 'sessionEnd':{
            this.warning_message = 'login.errors.session_end';
          this.email = this.userService.getEmail() || "";
          break;
        }
        case 'oauth':{
          this.warning_message = 'login.errors.oauth'
          this.email = this.userService.getEmail() || "";
          this.warning_message_color="is-success";
          this.userService.clear();
          this.is_oauth_flow=true;
          this.login_button="login.authorize" 
          break;
        }
        case 'confirmPassphrase':{
            this.warning_message = 'login.errors.confirm_passphrase';
          this.email = this.userService.getEmail() || "";
          this.warning_message_color="is-success";
          this.userService.clear();
          this.is_oauth_flow=true;
          break;
        }
      }
      
    }

    

  
  

  checkEmail() : boolean{
    const emailRegex = /\S+@\S+\.\S+/;
    if(!emailRegex.test(this.email)){
      this.translate.get("login.errors.email").subscribe((translation)=>{
      superToast({
        message:  translation,
        type: "is-danger",
        dismissible: true,
        duration: 20000,
        animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    });
      return false;
    } else {
      return true;
    }
  }

  
  login(){
    if(this.email == "" || this.password == ""){
      this.translate.get("login.errors.empty").subscribe((translation)=>{
      superToast({
        message: translation,
        type: "is-danger",
        dismissible: true,
        duration: 20000,
        animate: { in: 'fadeIn', out: 'fadeOut' }
      });
     });
      return;
    }
    if(!this.checkEmail()){
      return;
    }
    this.isLoading = true;
    this.hashPassword()
    
  }

  openFile(event: any): void {
    const input = event.target;
    const reader = new FileReader();
    reader.readAsText(input.files[0], 'utf-8');
    reader.onload = (() => {
      if (reader.result) {
        try{
          const unsecure_context = reader.result.toString();
          const version = this.localVaultv1.extract_version_from_vault(unsecure_context);
          if(version == null){
            this.translate.get("login.errors.import_vault.invalid_file").subscribe((translation)=>{
            superToast({
              message: translation,
              type: "is-danger",
              dismissible: false,
              duration: 20000,
              animate: { in: 'fadeIn', out: 'fadeOut' }
            });
          });
            
          } else if (version == 1){
            this.local_vault_service = this.localVaultv1
          this.local_vault_service.parseUploadedVault(unsecure_context).then((vault_parsing_status) => {
          switch (vault_parsing_status) {
            case UploadVaultStatus.SUCCESS:{
              this.isPassphraseModalActive = true;
              
              break
            }
            case UploadVaultStatus.INVALID_JSON: {
              this.translate.get("login.errors.import_vault.invalid_type").subscribe((translation)=>{
              superToast({
                message: translation,
                type: "is-danger",
                dismissible: false,
                duration: 20000,
                animate: { in: 'fadeIn', out: 'fadeOut' }
              });
            });
              
              break;
            }

            case UploadVaultStatus.INVALID_VERSION: {
              this.translate.get("login.errors.import_vault.invalid_version").subscribe((translation)=>{
                superToast({
                  message: translation,
                  type: "is-danger",
                  dismissible: false,
                  duration: 20000,
                  animate: { in: 'fadeIn', out: 'fadeOut' }
                });
              });
              
              break;
            }
            case UploadVaultStatus.NO_SIGNATURE: {
              this.translate.get("login.errors.import_vault.no_signature").subscribe((translation)=>{
                superToast({
                  message: translation,
                  type: "is-danger",
                  dismissible: false,
                  duration: 20000,
                  animate: { in: 'fadeIn', out: 'fadeOut' }
                });
              });
              
              break;
            }
            case UploadVaultStatus.INVALID_SIGNATURE: {
              this.isUnsecureVaultModaleActive = true;
              
              break;
            }
            case UploadVaultStatus.MISSING_ARGUMENT: {
              this.translate.get("login.errors.import_vault.missing_arg").subscribe((translation)=>{
                superToast({
                  message: translation,
                  type: "is-danger",
                  dismissible: false,
                  duration: 20000,
                  animate: { in: 'fadeIn', out: 'fadeOut' }
                });
              });
              
              break;
            }
            case UploadVaultStatus.INVALID_ARGUMENT: {
              this.translate.get("login.errors.import_vault.invalid_arg").subscribe((translation)=>{
                superToast({
                  message: translation,
                  type: "is-danger",
                  dismissible: false,
                  duration: 20000,
                  animate: { in: 'fadeIn', out: 'fadeOut' }
                });
              });
              
              break;
            }

              case UploadVaultStatus.UNKNOWN: {
                this.translate.get("login.errors.import_vault.error_unknown").subscribe((translation)=>{
                  superToast({
                    message: translation,
                    type: "is-danger",
                    dismissible: false,
                    duration: 20000,
                    animate: { in: 'fadeIn', out: 'fadeOut' }
                  });
                });
                
                break;
              }

            default: {
              this.translate.get("login.errors.import_vault.error_unknown").subscribe((translation)=>{
                superToast({
                  message: translation,
                  type: "is-danger",
                  dismissible: false,
                  duration: 20000,
                  animate: { in: 'fadeIn', out: 'fadeOut' }
                });
              });
              
              break;
          }
        }
      });
    }
    else {
      this.translate.get("login.errors.import_vault.invalid_version").subscribe((translation)=>{
        superToast({
          message: translation,
          type: "is-danger",
          dismissible: false,
          duration: 20000,
          animate: { in: 'fadeIn', out: 'fadeOut' }
        });
      });
      
    }
      } catch(e){
        this.translate.get("login.errors.import_vault.parse_fail").subscribe((translation)=>{
          superToast({
            message: translation,
            type: "is-danger",
            dismissible: false,
            duration: 20000,
            animate: { in: 'fadeIn', out: 'fadeOut' }
          });
        });
          
        }
      } else {
        this.translate.get("login.errors.import_vault.parse_fail").subscribe((translation)=>{
          superToast({
            message: translation,
            type: "is-danger",
            dismissible: false,
            duration: 20000,
            animate: { in: 'fadeIn', out: 'fadeOut' }
          });
        });
        
      }
    });

    }

    
      


    openLocalVault(){
      this.userService.clear();
      this.userService.setVaultLocal(true);
      this.userService.setLocalVaultService(this.local_vault_service!);
      this.userService.setDerivedKeySalt(this.local_vault_service!.get_derived_key_salt()!);
        this.deriveKey().then((derivedKey)=>{
            this.decryptZKEKey(this.local_vault_service!.get_zke_key_enc()!, derivedKey).then((zke_key)=>{
              this.userService.set_zke_key(zke_key!);
              this.router.navigate(["/vault"], {relativeTo:this.route.root});
            }, (error)=>{
              superToast({
                message: error,
                type: "is-danger",
                dismissible: false,
                duration: 20000,
                animate: { in: 'fadeIn', out: 'fadeOut' }
              });
              this.isLoading=false;
            });
        },(error)=>{
          superToast({
            message: error,
            type: "is-danger",
            dismissible: false,
            duration: 20000,
            animate: { in: 'fadeIn', out: 'fadeOut' }
          });
              this.isLoading=false;
        });
    }

  hashPassword(){
    this.http.get(ApiService.API_URL+"/login/specs?username="+encodeURIComponent(this.email),  {withCredentials:true, observe: 'response'}).subscribe((response) => {
      
      try{
        const data = JSON.parse(JSON.stringify(response.body))
        const salt = data.passphrase_salt
        this.crypto.hashPassphrase(this.password, salt).then(hashed => {
          if(hashed != null){
            this.hashedPassword = hashed;
            this.userService.setPassphraseSalt(salt);
            this.postLoginRequest();
          } else {
            this.translate.get("login.errors.hashing").subscribe((translation)=>{
            superToast({
              message: translation,
              type: "is-danger",
              dismissible: false,
              duration: 20000,
              animate: { in: 'fadeIn', out: 'fadeOut' }
            });
          });
            this.isLoading=false;
          }
        });
      } catch {
        this.translate.get("login.errors.hashing").subscribe((translation)=>{
          superToast({
            message: translation,
            type: "is-danger",
            dismissible: false,
            duration: 20000,
            animate: { in: 'fadeIn', out: 'fadeOut' }
          });
        });
        this.isLoading=false;
      }
    }, error => {
      if(error.status == 429){
        this.translate.get("login.errors.rate_limited").subscribe((translation)=>{
        superToast({
          message: translation,
          type: "is-danger",
          dismissible: true,
          duration: 20000,
        animate: { in: 'fadeIn', out: 'fadeOut' }
        });
      });
    } else {
      this.translate.get("login.errors.no_connection").subscribe((translation)=>{
        superToast({
          message: translation,
          type: "is-danger",
          dismissible: false,
          duration: 20000,
          animate: { in: 'fadeIn', out: 'fadeOut' }
        });
      });
    }
      this.isLoading=false;
    });
  }


  postLoginRequest(){
    const data = {
      email: this.email,
      password: this.hashedPassword
    }
    this.http.post(ApiService.API_URL+"/login",  data, {withCredentials: true, observe: 'response'}).subscribe((response) => {
      try{
        const data = JSON.parse(JSON.stringify(response.body))
        this.userService.setId(data.id);
        this.userService.setEmail(this.email);
        this.userService.setDerivedKeySalt(data.derivedKeySalt);
        if(data.isVerified == false){
          this.router.navigate(["/emailVerification"], {relativeTo:this.route.root});
        } else {

        
        if(data.role == "admin"){
          this.userService.setIsAdmin(true);
        }
        this.userService.setGoogleDriveSync(data.isGoogleDriveSync);
        this.final_zke_flow();
        }
      } catch(e){
        this.isLoading=false;
        console.log(e);
        this.translate.get("login.errors.server_error").subscribe((translation)=>{
        superToast({
          message: translation ,
          type: "is-danger",
          duration: 20000,
          dismissible: true,
        animate: { in: 'fadeIn', out: 'fadeOut' }
        });
      });
      }
      
    },
    (error) => {
      console.log(error);
      console.log(error.error.message)
      this.isLoading=false;
      if(error.status == 429){
        const ban_time = error.error.ban_time || "few";
        this.translate.get("login.errors.rate_limited",{time:String(ban_time)} ).subscribe((translation)=>{
        superToast({
          message: translation,
          type: "is-danger",
          dismissible: true,
          duration: 20000,
        animate: { in: 'fadeIn', out: 'fadeOut' }
        });
      });
      } else if(error.error.message == "blocked"){
        this.translate.get("login.errors.account_blocked").subscribe((translation)=>{
        superToast({
          message: translation,
          type: "is-danger",
          dismissible: true,
          duration: 99000,
        animate: { in: 'fadeIn', out: 'fadeOut' }
        });
      });
      } else {
        this.translate.get("generic_errors.error").subscribe((trans)=>{
          superToast({
            message: trans + " : "+ this.translate.instant((error.error.message) ? error.error.message : ""),
            type: "is-danger",
            dismissible: true,
            duration: 20000,
          animate: { in: 'fadeIn', out: 'fadeOut' }
          });
        });
      }
      
    });
  }

  final_zke_flow(){
    this.deriveKey().then((derivedKey)=>{
      this.getZKEKey().then((zke_key_encrypted)=>{
        this.decryptZKEKey(zke_key_encrypted, derivedKey).then((zke_key)=>{
          this.userService.set_zke_key(zke_key!);
          if(this.is_oauth_flow){
            this.router.navigate(["/oauth/synchronize"], {relativeTo:this.route.root});
          } else {
            this.router.navigate(["/vault"], {relativeTo:this.route.root});
          }
        }, (error)=>{
          superToast({
            message: error,
            type: "is-danger",
            dismissible: false,
            duration: 20000,
            animate: { in: 'fadeIn', out: 'fadeOut' }
          });
          this.isLoading=false;
        });
      }, (error)=>{
        superToast({
          message: error,
          type: "is-danger",
          dismissible: false,
          duration: 20000,
          animate: { in: 'fadeIn', out: 'fadeOut' }
        });
        this.isLoading=false;
      });
    },(error)=>{
      superToast({
        message: error,
        type: "is-danger",
        dismissible: false,
        duration: 20000,
        animate: { in: 'fadeIn', out: 'fadeOut' }
      });
          this.isLoading=false;
    });
  }


  deriveKey() : Promise<CryptoKey>{
    return new Promise((resolve, reject) => {
      const derivedKeySalt = this.userService.getDerivedKeySalt();
      if(derivedKeySalt != null){
        this.crypto.deriveKey(derivedKeySalt, this.password).then(key=>{
          resolve(key);
        });
      } else {
        this.isLoading=false;
        reject("Impossible to retrieve enough data to decrypt your vault");
      }
    });
  }

  getZKEKey(): Promise<string> {
    return new Promise((resolve, reject) => {
      this.http.get(ApiService.API_URL+"/zke_encrypted_key",  {withCredentials:true, observe: 'response'}).subscribe((response) => {
        const data = JSON.parse(JSON.stringify(response.body))
        const zke_key_encrypted = data.zke_encrypted_key
        resolve(zke_key_encrypted);
      }, (error)=> {
        reject("Impossible to retrieve your encryption key. Please try again later. " + error.error.error);
      });
    });
    
  }


  decryptZKEKey(zke_key_encrypted: string, derivedKey: CryptoKey): Promise<CryptoKey> {
    return new Promise((resolve, reject) => {
      this.crypto.decrypt(zke_key_encrypted, derivedKey).then(zke_key_b64=>{
        if (zke_key_b64 != null) {
          const zke_key_raw = Buffer.from(zke_key_b64!, 'base64');

          window.crypto.subtle.importKey(
            "raw",
            zke_key_raw,
            "AES-GCM",
            true,
            ["encrypt", "decrypt"]
          ).then((zke_key)=>{
            resolve(zke_key);
          }, (error)=>{
            this.translate.get("login.errors.import_vault.key_dec").subscribe((translation)=>{
            reject(translation + " " + error);
            });
          });;
        } else {
          if(this.userService.getIsVaultLocal()!){
            this.translate.get("login.errors.import_vault.wrong_passphrase").subscribe((translation)=>{
            reject(translation);
            });
          } else {
            this.translate.get("login.errors.import_vault.key_dec").subscribe((translation)=>{
            reject(translation);
            });
          }
          
        }
        
      });
  });
  }
}
