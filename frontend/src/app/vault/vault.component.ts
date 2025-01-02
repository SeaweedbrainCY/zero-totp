import { Component, OnInit } from '@angular/core';
import { UserService } from '../common/User/user.service';
import { ActivatedRoute, Router } from '@angular/router';
import { faPen, faSquarePlus, faCopy, faCheckCircle, faCircleXmark, faDownload, faDesktop, faRotateRight, faChevronUp, faChevronDown, faChevronRight, faLink, faCircleInfo, faUpload, faCircleNotch, faCircleExclamation, faCircleQuestion, faFlask, faMagnifyingGlass, faXmark, faServer} from '@fortawesome/free-solid-svg-icons';
import { faGoogleDrive } from '@fortawesome/free-brands-svg-icons';
import { HttpClient } from '@angular/common/http';

import { Crypto } from '../common/Crypto/crypto';
import { Utils } from '../common/Utils/utils';
import { error } from 'console';
import { formatDate } from '@angular/common';
import { LocalVaultV1Service } from '../common/upload-vault/LocalVaultv1Service.service';
import { TranslateService } from '@ngx-translate/core';
import { ToastrService } from 'ngx-toastr'; 

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
  faServer=faServer;
  faCircleXmark= faCircleXmark;
  faCheckCircle = faCheckCircle;
  faRotateRight = faRotateRight;
  faCircleNotch = faCircleNotch;
  faMagnifyingGlass = faMagnifyingGlass;
  faXmark = faXmark;
  faFlask = faFlask;
  faDesktop=faDesktop;
  faCircleExclamation=faCircleExclamation;
  faDownload=faDownload;
  faChevronUp=faChevronUp;
  faChevronDown=faChevronDown;
  faChevronRight=faChevronRight;
  faLink=faLink;
  faCircleInfo=faCircleInfo;
  faCircleQuestion=faCircleQuestion;
  faUpload=faUpload;
  vault: Map<string, Map<string,string>> | undefined;
  vaultUUIDs : string[] = [];
  remainingTime = 0;
  totp = require('totp-generator');
  isModalActive = false
  reloadSpin = false
  storageOptionOpen = false
  local_vault_service :LocalVaultV1Service | null  = null;
  page_title="vault.title.main";
  vault_date :string | undefined = undefined; // for local vault
  isRestoreBackupModaleActive=false;
  isGoogleDriveEnabled = true;
  isGoogleDriveSync = "loading"; // uptodate, loading, error, false
  lastBackupDate = "";
  faviconPolicy = "";
  filter="";
  google_drive_error_message = "";
  selectedTags:string[]=[];
  constructor(
    public userService: UserService,
    private router: Router,
    private route: ActivatedRoute,
    private http: HttpClient,
    private crypto: Crypto,
    private utils: Utils,
    private translate: TranslateService,
    private toastr: ToastrService,
    ) {}

  ngOnInit() {
    if(this.userService.getId() == null && !this.userService.getIsVaultLocal()){
      this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
    } else if(this.userService.getIsVaultLocal()){
      this.local_vault_service = this.userService.getLocalVaultService();
      let vaultDate = "unknown"
      try{
        const vaultDateStr = this.local_vault_service!.get_date()!.split(".")[0];
        vaultDate = String(formatDate(new Date(vaultDateStr), 'dd/MM/yyyy HH:mm:ss O', 'en'));
      }catch{
        vaultDate = "error"
      }
      

      this.page_title = "vault.title.backup";
      this.vault_date = vaultDate;
      this.decrypt_and_display_vault(this.local_vault_service!.get_enc_secrets()!);
    } else {
      this.get_google_drive_option();
      this.get_preferences();

      this.reloadSpin = true
      this.vault = new Map<string, Map<string,string>>();
      this.vaultUUIDs = [];
      this.userService.setVaultTags([]);
      this.http.get("/api/v1/all_secrets",  {withCredentials:true, observe: 'response'}).subscribe((response) => {
        const data = JSON.parse(JSON.stringify(response.body))
        let encrypted_secret_vault = new Array<Map<string, string>>();
        for (let secret of data.enc_secrets){
          let secret_map = new Map<string, string>();
          secret_map.set("uuid", secret.uuid);
          secret_map.set("enc_secret", secret.enc_secret);
          encrypted_secret_vault.push(secret_map);
        }
        this.decrypt_and_display_vault(encrypted_secret_vault);
      }, (error) => {
        this.reloadSpin = true
        if(error.status == 404){
          this.userService.setVault(new Map<string, Map<string,string>>());
          this.reloadSpin = false
        } else {
          let errorMessage = "";
          if(error.error.message != null){
            errorMessage = error.error.message;
          } else if(error.error.detail != null){
            errorMessage = error.error.detail;
          }
          if(error.status == 0){
            errorMessage = "vault.error.server_unreachable"
          } else if (error.status == 401){
            this.userService.clear();
            this.router.navigate(["/login/sessionEnd"], {relativeTo:this.route.root});
            return;
          }
          this.translate.get("vault.error.server").subscribe((translation: string) => {
          this.utils.toastError(this.toastr, translation +  " " + this.translate.instant(errorMessage),"");
        });
        }
      });
      
    }    
  }



  startDisplayingCode(){
        setInterval(()=> { this.generateTime() }, 20);
        setInterval(()=> { this.generateCode() }, 100);
  }

  get_preferences(){
    this.http.get("/api/v1/preferences?fields=favicon_policy", {withCredentials: true, observe: 'response'}).subscribe((response) => {
      if(response.body != null){
        const data = JSON.parse(JSON.stringify(response.body));
        if(data.favicon_policy != null){
          this.faviconPolicy = data.favicon_policy;
        } else {
          this.faviconPolicy = "enabledOnly";
          this.translate.get("vault.error.preferences").subscribe((translation: string) => {
            this.utils.toastError(this.toastr,translation ,"");
        });
        }
      }
    }, (error) => {
        let errorMessage = "";
          if(error.error.message != null){
            errorMessage = error.error.message;
          } else if(error.error.detail != null){
            errorMessage = error.error.detail;
          }
          if(error.status == 0){
            errorMessage = "vault.error.server_unreachable"
            return;
          } 
          this.translate.get("vault.error.server").subscribe((translation: string) => {
            this.utils.toastError(this.toastr, "Error : Impossible to update your preferences. "+ this.translate.instant(errorMessage),"");
        });
    });
  }

  decrypt_and_display_vault(encrypted_vault:Array<Map<string, string>>){
    this.reloadSpin = true
      this.vault = new Map<string, Map<string,string>>();
      this.vaultUUIDs = [];
    try{
     if(this.userService.get_zke_key() != null){
      try{
        this.startDisplayingCode()
        for (let secret of encrypted_vault){
          const uuid = secret.get("uuid");
          const enc_secret = secret.get("enc_secret");
          if(uuid != null && enc_secret != null){
          this.crypto.decrypt(enc_secret, this.userService.get_zke_key()!).then((dec_secret)=>{
            if(dec_secret == null){
              this.translate.get("vault.error.wrong_key").subscribe((translation: string) => {
                this.utils.toastError(this.toastr, translation,"");
            });
              let fakeProperty = new Map<string, string>();
              fakeProperty.set("color","info");
              fakeProperty.set("name", "🔒")
              fakeProperty.set("secret", "");

              this.vault?.set(uuid, fakeProperty);
            } else {
                try{
                  this.vault?.set(uuid, this.utils.mapFromJson(dec_secret));
                  this.userService.setVault(this.vault!);

                  this.filterVault(); // to display all the vault
                  for (let uuid of this.vaultUUIDs){
                    // display all tags, always
                    if(this.vault!.get(uuid)!.has("tags")){
                      const secret_tags = this.utils.parseTags(this.vault!.get(uuid)!.get("tags")!);
                      for (const tag of secret_tags){
                        if(!this.userService.getVaultTags().includes(tag)){
                        this.userService.getVaultTags().push(tag);
                        }
                      }
                    }
                  }
                } catch {
                  this.translate.get("vault.error.wrong_key").subscribe((translation: string) => {
                    this.utils.toastError(this.toastr,"vault.error.wrong_key","");
                });
                }
              }
          }).catch((error)=>{
            console.log(error);
            this.translate.get("vault.error.decryption").subscribe((translation: string) => {
              this.utils.toastError(this.toastr,  translation + " " + error,"");
          });
          });
        } else {
          console.log("uuid or enc_secret is null");
            this.translate.get("vault.error.decryption").subscribe((translation: string) => {
              this.utils.toastError(this.toastr,  translation,"");
            });
        }
        
        }
        this.reloadSpin = false
      } catch (e){
        console.log(e);
        this.translate.get("vault.error.wrong_key_vault").subscribe((translation: string) => {
            this.utils.toastError(this.toastr,translation,"")
      });
      }
    } else {
      this.translate.get("vault.error.decryption_vault").subscribe((translation: string) => {
          this.utils.toastError(this.toastr,translation,"")
    });
    }
    } catch(e){
      this.translate.get("vault.error.retrieve_vault").subscribe((translation: string) => {
        this.utils.toastError(this.toastr,translation,"")
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
    if(this.vault == undefined){
      return;
    }
    for(let uuid of this.vaultUUIDs){
      const secret = this.vault!.get(uuid)!.get("secret")!;
      try{
        let code=this.totp(secret); 
        this.vault!.get(uuid)!.set("code", code);
      } catch (e){
        let code = "Error"
        this.vault!.get(uuid)!.set("code", code);
      }
    }


  }

  filterVault(){
    this.vaultUUIDs = [];
    let tmp_vault =  Array.from(this.vault!.keys()) as string[];
    if (this.filter == "" && this.selectedTags.length == 0){
      this.vaultUUIDs = tmp_vault;
      return;
    }
    this.filter = this.filter.replace(/[^a-zA-Z0-9-_]/g, '');
    this.filter = this.filter.toLowerCase();
    if(this.filter.length > 50){
      this.filter = this.filter.substring(0,50);
    }
    let regex = new RegExp(this.filter);
    if(this.filter == ""){ // we filter on tags
      regex = new RegExp(".*");
    }
    for (let uuid of tmp_vault){
      let has_tag = false;
      if(this.selectedTags.length > 0){
        if(this.vault!.get(uuid)!.has("tags")){
          const secret_tags = this.utils.parseTags(this.vault!.get(uuid)!.get("tags")!);
          for(const tag of this.selectedTags){
            if(secret_tags.includes(tag)){
              has_tag = true;
            }
          }
      }
    }
      if(this.selectedTags.length == 0 || has_tag){
      //filter on search filter
      if(regex.test(this.get_favicon_url(this.vault!.get(uuid)?.get('domain')).toLowerCase()))
      {
        this.vaultUUIDs.push(uuid);
      } else if (this.vault!.get(uuid)?.get('name')){
        if(regex.test(this.vault!.get(uuid)?.get('name')!.toLowerCase()!))
        {
          this.vaultUUIDs.push(uuid);
        }
      }
    }
  }
  }

  edit(domain:string){
    this.router.navigate(["/vault/edit/"+domain], {relativeTo:this.route.root});
  }

  copy(){
    this.utils.toastSuccess(this.toastr,this.translate.instant("copied"),"");
  }

  reload(){
    this.ngOnInit();
  }
  
  downloadVault(){
    this.http.get("/api/v1/vault/export",  {withCredentials:true, observe: 'response',  responseType: 'blob' }, ).subscribe((response) => {
      const blob = new Blob([response.body!], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const date = String(formatDate(new Date (), 'dd-MM-yyyy-hh-mm-ss', 'en'));
        a.download = 'enc_vault_' + date + '.zero-totp';
        a.click();
        window.URL.revokeObjectURL(url);
        this.utils.toastSuccess(this.toastr, this.translate.instant("vault.downloaded") ,"");
    }, error => {
      let errorMessage = "";
      if(error.error.message != null){
        errorMessage = error.error.message;
      } else if(error.error.detail != null){
        errorMessage = error.error.detail;
      }

      if(error.status == 0){
        errorMessage = "vault.error.server_unreachable"
      } else if (error.status == 401){
        this.userService.clear();
        this.router.navigate(["/login/sessionEnd"], {relativeTo:this.route.root});
        return;
      }
      this.translate.get("vault.error.server").subscribe((translation: string) => {
        this.utils.toastError(this.toastr,  translation + " " + this.translate.instant(errorMessage),"");
    });
    });
  }

  get_oauth_authorization_url(){
    this.http.get("/api/v1/google-drive/oauth/authorization-flow",  {withCredentials:true, observe: 'response'}).subscribe((response) => { 
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
        this.translate.get("vault.oauth.error.server").subscribe((translation: string) => {
          this.utils.toastError(this.toastr,  translation + ". "+ errorMessage,"");
      });
    });
  }



  get_google_drive_option(){
    this.http.get("/api/v1/google-drive/option",  {withCredentials:true, observe: 'response'}).subscribe((response) => { 
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
        this.translate.get("vault.error.server").subscribe((translation: string) => {
          this.utils.toastError(this.toastr,  translation + " "+ errorMessage,"");
        });
    });
  }

  backup_vault_to_google_drive(){
          this.http.put("/api/v1/google-drive/backup", {}, {withCredentials:true, observe: 'response'}, ).subscribe((response) => {
            this.isGoogleDriveSync = "uptodate";
            this.lastBackupDate =  String(formatDate(new Date(), 'dd/MM/yyyy HH:mm:ss', 'en'));
          }, (error) => {
            this.isGoogleDriveSync = 'error';
            let errorMessage = "";
            if(error.error.message != null){
              errorMessage = error.error.message;
            } else if(error.error.detail != null){
              errorMessage = error.error.title;
            }
            this.translate.get("vault.error.backup.part1").subscribe((translation: string) => {
              this.utils.toastError(this.toastr,  translation + " " + errorMessage + ". " + this.translate.instant("vault.error.backup.part2"),"");
          });
          });
  }

  check_last_backup(){
    this.http.get("/api/v1/google-drive/last-backup/verify",  {withCredentials:true, observe: 'response'}, ).subscribe((response) => {
      const data = JSON.parse(JSON.stringify(response.body))
      if(data.status == "ok"){
        if(data.is_up_to_date == true){
          this.isGoogleDriveSync = "uptodate";
          const date_str = data.last_backup_date.split("T")[0] + " " + data.last_backup_date.split("T")[1];
          this.lastBackupDate =  String(formatDate(new Date(date_str), 'dd/MM/yyyy HH:mm:ss', 'en'));
        } else {
          this.backup_vault_to_google_drive();
        }
      } else if (data.status == "corrupted_file"){
        this.isGoogleDriveSync = "error";
        this.translate.get("vault.error.google.unreadable").subscribe((translation: string) => {
          this.utils.toastError(this.toastr,  translation,"");
      });
      } else {
        this.translate.get("vault.error.google.unreadable").subscribe((translation: string) => {
          this.utils.toastError(this.toastr,  translation,"");
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
      } else if(error.error.error != null){
        errorMessage = error.error.error;
      }
      this.google_drive_error_message = "An error occured while checking your backup. Got error " + error.status + ". " + errorMessage;
    }
    });
  }

  disable_google_drive(){
    this.http.delete("/api/v1/google-drive/option",  {withCredentials:true, observe: 'response'}, ).subscribe((response) => {
      this.isGoogleDriveEnabled = false;
      this.isGoogleDriveSync = "false";
      this.utils.toastSuccess(this.toastr, this.translate.instant("vault.google.disabled"),"");
    }, (error) => {
      this.isGoogleDriveSync = 'error';
      let errorMessage = "";
      if(error.error.message != null){
        errorMessage = error.error.message;
      } else if(error.error.detail != null){
        errorMessage = error.error.detail;
      }

      this.utils.toastError(this.toastr, this.translate.instant("vault.error.google.disable") + " " + errorMessage,"");
    });
    }


  get_favicon_url(unsafe_domain:string | undefined): string{
    if(unsafe_domain == undefined){
      return "https://icons.duckduckgo.com/ip3/unknown.ico";
    }
    if(this.utils.domain_name_validator(unsafe_domain)){
      return  "https://icons.duckduckgo.com/ip3/" +unsafe_domain + ".ico";
    } else {
      return "https://icons.duckduckgo.com/ip3/unknown.ico";
    }
  }

  resync_after_error(){
    this.disable_google_drive();
    this.isGoogleDriveSync = "loading";
    setTimeout(()=> {
      this.get_oauth_authorization_url();
  }, 2000);
    
  }


  selectTag(tag:string){
    if(this.selectedTags.includes(tag)){
      this.selectedTags = this.selectedTags.filter(e => e !== tag);
    } else {
      this.selectedTags.push(tag);
    }
    this.filterVault();
  }


  

}

