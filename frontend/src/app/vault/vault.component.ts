import { Component, OnInit } from '@angular/core';
import { UserService } from '../common/User/user.service';
import { ActivatedRoute, Router } from '@angular/router';
import { faPen, faSquarePlus, faCopy, faCheckCircle, faCircleXmark, faDownload, faDesktop, faRotateRight, faChevronUp, faChevronDown, faChevronRight, faLink, faCircleInfo, faUpload, faCircleNotch, faCircleExclamation } from '@fortawesome/free-solid-svg-icons';
import { faGoogleDrive } from '@fortawesome/free-brands-svg-icons';
import { HttpClient } from '@angular/common/http';
import { ApiService } from '../common/ApiService/api-service';
import { Crypto } from '../common/Crypto/crypto';
import { toast as superToast } from 'bulma-toast'
import { Utils } from '../common/Utils/utils';
import { error } from 'console';
import { formatDate } from '@angular/common';
import { LocalVaultV1Service } from '../common/upload-vault/LocalVaultv1Service.service';
import { BnNgIdleService } from 'bn-ng-idle';

@Component({
  selector: 'app-vault',
  templateUrl: './vault.component.html',
  styleUrls: ['./vault.component.css']
})
export class VaultComponent implements OnInit {
  faPen = faPen;
  faSquarePlus = faSquarePlus;
  faCopy = faCopy;
  faGoogleDrive=faGoogleDrive;
  faCircleXmark= faCircleXmark;
  faCheckCircle = faCheckCircle;
  faRotateRight = faRotateRight;
  faCircleNotch = faCircleNotch;
  faDesktop=faDesktop;
  faCircleExclamation=faCircleExclamation;
  faDownload=faDownload;
  faChevronUp=faChevronUp;
  faChevronDown=faChevronDown;
  faChevronRight=faChevronRight;
  faLink=faLink;
  faCircleInfo=faCircleInfo;
  faUpload=faUpload;
  vault: Map<string, Map<string,string>> | undefined;
  vaultDomain : string[] = [];
  remainingTime = 0;
  totp = require('totp-generator');
  isModalActive = false
  reloadSpin = false
  storageOptionOpen = false
  local_vault_service :LocalVaultV1Service | null  = null;
  page_title="Here is your TOTP vault";
  isRestoreBackupModaleActive=false;
  isGoogleDriveEnabled = true;
  isGoogleDriveSync = "loading"; // uptodate, loading, error, false

  constructor(
    public userService: UserService,
    private router: Router,
    private route: ActivatedRoute,
    private http: HttpClient,
    private crypto: Crypto,
    private utils: Utils,
    private bnIdle: BnNgIdleService,
    ) {  }

  ngOnInit() {
    if(this.userService.getId() == null && !this.userService.getIsVaultLocal()){
      this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
    } else if(this.userService.getIsVaultLocal()){
      this.local_vault_service = this.userService.getLocalVaultService();
      this.page_title = "Backup from " + this.local_vault_service!.get_date()!.split(".")[0];
      this.decrypt_and_display_vault(this.local_vault_service!.get_enc_secrets()!);
    } else {
      this.reloadSpin = true
      this.vault = new Map<string, Map<string,string>>();
      this.http.get(ApiService.API_URL+"/all_secrets",  {withCredentials:true, observe: 'response'}).subscribe((response) => {
        this.bnIdle.startWatching(600).subscribe((isTimedOut: boolean) => {
          if(isTimedOut){
            this.bnIdle.stopTimer();
            this.userService.clear();
            this.router.navigate(['/login/sessionTimeout'], {relativeTo:this.route.root});
          }
        });
        const data = JSON.parse(JSON.stringify(response.body))
        this.decrypt_and_display_vault(data.enc_secrets);
        this.get_google_drive_option();
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
            errorMessage = "Server unreachable. Please check your internet connection or try again later. Do not reload this tab to avoid losing your session."
          } else if (error.status == 401){
            this.userService.clear();
            this.router.navigate(["/login/sessionEnd"], {relativeTo:this.route.root});
            return;
          }

          superToast({
            message: "Error : Impossible to retrieve your vault from the server. "+ errorMessage,
            type: "is-danger",
            dismissible: false,
            duration: 20000,
          animate: { in: 'fadeIn', out: 'fadeOut' }
          });
        }
      });
    }    
  }

  startDisplayingCode(){
        setInterval(()=> { this.generateTime() }, 20);
        setInterval(()=> { this.generateCode() }, 100);
  }

  decrypt_and_display_vault(encrypted_vault:any){
    this.reloadSpin = true
      this.vault = new Map<string, Map<string,string>>();
    try{
     if(this.userService.get_zke_key() != null){
      try{
        this.startDisplayingCode()
        for (let secret of encrypted_vault){
          this.crypto.decrypt(secret.enc_secret, this.userService.get_zke_key()!).then((dec_secret)=>{
            if(dec_secret == null){
              superToast({
                message: "Wrong key. You cannot decrypt one of the secrets. Displayed secrets can not be complete. Please log out  and log in again.",
                type: "is-danger",
                dismissible: false,
                duration: 20000,
              animate: { in: 'fadeIn', out: 'fadeOut' }
              });
              let fakeProperty = new Map<string, string>();
              fakeProperty.set("color","info");
              fakeProperty.set("name", "🔒")
              fakeProperty.set("secret", "");

              this.vault?.set(secret.uuid, fakeProperty);
            } else {
                try{
                  this.vault?.set(secret.uuid, this.utils.mapFromJson(dec_secret));
                  this.userService.setVault(this.vault!);
                  this.vaultDomain = Array.from(this.vault!.keys()) as string[];
                } catch {
                  superToast({
                    message: "Wrong key. You cannot decrypt one secret. This secret will be ignored. Please log   out and log in again.   ",
                    type: "is-danger",
                    dismissible: false,
                    duration: 20000,
                  animate: { in: 'fadeIn', out: 'fadeOut' }
                  });
                }
              }
          }).catch((error)=>{
            superToast({
              message: "An error occurred while decrypting your secrets." + error,
              type: "is-danger",
              dismissible: false,
              duration: 20000,
            animate: { in: 'fadeIn', out: 'fadeOut' }
            });
          });
        }
        this.reloadSpin = false
      } catch {
        superToast({
          message: "Wrong key. You cannot decrypt this vault.",
          type: "is-danger",
          dismissible: false,
          duration: 20000,
        animate: { in: 'fadeIn', out: 'fadeOut' }
        });
      }
    } else {
      superToast({
        message: "Impossible to decrypt your vault. Please log out and log in again.",
        type: "is-danger",
        dismissible: false,
        duration: 20000,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    }
    } catch(e){
      superToast({
        message: "Error : Impossible to retrieve your vault from the server",
        type: "is-danger",
        dismissible: false,
        duration: 20000,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    }
  }

  navigate(route:string){
    this.router.navigate([route], {relativeTo:this.route.root});
   
  }

  generateTime(){
    const duration = 30 - Math.floor(Date.now() / 10 % 3000)/100;
    this.remainingTime = (duration/30)*100
  }

  generateCode(){
    for(let domain of this.vaultDomain){
      const secret = this.vault!.get(domain)!.get("secret")!;
      try{
        let code=this.totp(secret); 
        this.vault!.get(domain)!.set("code", code);
      } catch (e){
        let code = "Error"
        this.vault!.get(domain)!.set("code", code);
      }
   
    }


  }

  edit(domain:string){
    this.router.navigate(["/vault/edit/"+domain], {relativeTo:this.route.root});
  }

  copy(){
    superToast({
      message: "Copied !",
      type: "is-success",
      dismissible: true,
    animate: { in: 'fadeIn', out: 'fadeOut' }
    });
  }

  reload(){
    this.ngOnInit();
  }
  
  downloadVault(){
    this.http.get(ApiService.API_URL+"/vault/export",  {withCredentials:true, observe: 'response',  responseType: 'blob' }, ).subscribe((response) => {
      const blob = new Blob([response.body!], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const date = String(formatDate(new Date (), 'dd-MM-yyyy-hh-mm-ss', 'en'));
        a.download = 'enc_vault_' + date + '.zero-totp';
        a.click();
        window.URL.revokeObjectURL(url);
      superToast({
        message: "Encrypted vault downloaded ! 🧳\nKeep it in a safe place 🔒",
        type: "is-success",
        dismissible: false,
        duration: 20000,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    }, error => {
      let errorMessage = "";
      if(error.error.message != null){
        errorMessage = error.error.message;
      } else if(error.error.detail != null){
        errorMessage = error.error.detail;
      }

      if(error.status == 0){
        errorMessage = "Server unreachable. Please check your internet connection or try again later. Do not reload this tab to avoid losing your session."
      } else if (error.status == 401){
        this.userService.clear();
        this.router.navigate(["/login/sessionEnd"], {relativeTo:this.route.root});
        return;
      }
      
      superToast({
        message: "Error : Impossible to retrieve your vault from the server. "+ errorMessage,
        type: "is-danger",
        dismissible: false,
        duration: 20000,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    });
  }

  get_oauth_authorization_url(){
    this.http.get(ApiService.API_URL+"/google-drive/oauth/authorization-flow",  {withCredentials:true, observe: 'response'}).subscribe((response) => { 
      const data = JSON.parse(JSON.stringify(response.body))
      sessionStorage.setItem("oauth_state", data.state);
      window.location.href = data.authorization_url;
    }, (error) => {
        let errorMessage = "";
        if(error.error.message != null){
          errorMessage = error.error.message;
        } else if(error.error.detail != null){
          errorMessage = error.error.detail;
        }
        superToast({
          message: "Error : Impossible to retrieve your vault from the server. "+ errorMessage,
          type: "is-danger",
          dismissible: false,
          duration: 20000,
        animate: { in: 'fadeIn', out: 'fadeOut' }
        });
    });
  }



  get_google_drive_option(){
    this.http.get(ApiService.API_URL+"/google-drive/option",  {withCredentials:true, observe: 'response'}).subscribe((response) => { 
      const data = JSON.parse(JSON.stringify(response.body))
      if(data.status == "enabled"){
        this.isGoogleDriveEnabled = true;
        this.check_last_backup();
      } else {
        this.isGoogleDriveEnabled = false;
        this.isGoogleDriveSync = "false";
      }
    }, (error) => {
        let errorMessage = "";
        if(error.error.message != null){
          errorMessage = error.error.message;
        } else if(error.error.detail != null){
          errorMessage = error.error.detail;
        }
        superToast({
          message: "Error : Impossible to retrieve your vault from the server. "+ errorMessage,
          type: "is-danger",
          dismissible: false,
          duration: 20000,
        animate: { in: 'fadeIn', out: 'fadeOut' }
        });
    });
  }

  backup_vault_to_google_drive(){
          this.http.put(ApiService.API_URL+"/google-drive/backup", {}, {withCredentials:true, observe: 'response'}, ).subscribe((response) => {
            this.isGoogleDriveSync = "uptodate";
          }, (error) => {
            this.isGoogleDriveSync = 'error';
            let errorMessage = "";
            if(error.error.message != null){
              errorMessage = error.error.message;
            } else if(error.error.detail != null){
              errorMessage = error.error.title;
            }
            superToast({
              message: "Error : Impossible to backup your vault. "+ errorMessage + ". Please, try to re-sync your Google Drive account.",
              type: "is-danger",
              dismissible: false,
              duration: 20000,
            animate: { in: 'fadeIn', out: 'fadeOut' }
            });
          });
  }

  check_last_backup(){
    this.http.get(ApiService.API_URL+"/google-drive/last-backup/verify",  {withCredentials:true, observe: 'response'}, ).subscribe((response) => {
      const data = JSON.parse(JSON.stringify(response.body))
      if(data.status == "ok"){
        if(data.is_up_to_date == true){
          this.isGoogleDriveSync = "uptodate";
        } else {
          this.backup_vault_to_google_drive();
        }
      } else if (data.status == "corrupted_file"){
        this.isGoogleDriveSync = "error";
        superToast({
          message: "Error : Your vault backup is unreadable. Please, try to re-backup your Google Drive account.",
          type: "is-danger",
          dismissible: false,
          duration: 20000,
        animate: { in: 'fadeIn', out: 'fadeOut' }
        });
      } else {
        this.isGoogleDriveSync = "error";
        superToast({
          message: "Error : Your vault backup is unreadable. Please, try to re-backup your Google Drive account.",
          type: "is-danger",
          dismissible: false,
          duration: 20000,
        animate: { in: 'fadeIn', out: 'fadeOut' }
        });
      }
    }, (error) => {
      if(error.status == 404){
        this.backup_vault_to_google_drive();
      } else {
      this.isGoogleDriveSync = 'error';
      let errorMessage = "";
      if(error.error.message != null){
        errorMessage = error.error.message;
      } else if(error.error.detail != null){
        errorMessage = error.error.detail;
      }
      superToast({
        message: "Error : Impossible to verify your vault backups. "+ errorMessage,
        type: "is-danger",
        dismissible: false,
        duration: 20000,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    }
    });
  }
}
