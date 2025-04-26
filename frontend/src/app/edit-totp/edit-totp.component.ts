import { Component, OnDestroy, OnInit } from '@angular/core';
import { Router, ActivatedRoute, NavigationEnd } from '@angular/router';
import { UserService } from '../common/User/user.service';
import { HttpClient } from '@angular/common/http';
import { faChevronCircleLeft, faGlobe, faKey, faCircleQuestion, faPassport, faPlus, faCheck, faCircleNotch } from '@fortawesome/free-solid-svg-icons';
import { Utils  } from '../common/Utils/utils';

import { Crypto } from '../common/Crypto/crypto';
import { QrCodeTOTP } from '../common/qr-code-totp/qr-code-totp.service';
import { LocalVaultV1Service } from '../common/upload-vault/LocalVaultv1Service.service';
import URLParse from 'url-parse';
import { dom } from '@fortawesome/fontawesome-svg-core';
import { TranslateService } from '@ngx-translate/core';
import { ToastrService } from 'ngx-toastr';
import { TOTP } from 'totp-generator'

@Component({
    selector: 'app-edit-totp',
    templateUrl: './edit-totp.component.html',
    styleUrls: ['./edit-totp.component.css'],
    standalone: false
})
export class EditTOTPComponent implements OnInit, OnDestroy{
  faChevronCircleLeft = faChevronCircleLeft;
  faGlobe = faGlobe;
  faKey = faKey;
  faPassport = faPassport;
  faCircleNotch = faCircleNotch;
  faPlus = faPlus;
  faCheck = faCheck;
  faCircleQuestion = faCircleQuestion;
  faviconURL = "";
  name = "";
  uri="";
  favicon=false;
  uuid="";
  secret = "";
  nameError = "";
  uriError = "";
  secretError = "";
  color="info";
  selected_color="";
  animationFrameId: number=0;
  code = "";
  progress_bar_percent=80;
  currentUrl:string = "";
  secret_uuid:string|null = null;
  isModalActive = false;  
  isDestroying = false;
  faviconPolicy=""; // never, always, enabledOnly
  tags:string[] = [];
  isTagModalActive = false;
  addTagName="";
  isEditing = false; // true if editing, false if adding
  isSaving = false;
  remainingTags:string[] = [];
  totp_code_expiration = 0;
  generating_next_totp_code = false;
  totp_code_generation_interval:NodeJS.Timeout|undefined;
  constructor(
    private router: Router,
    private route : ActivatedRoute,
    public userService : UserService,
    private QRCodeService : QrCodeTOTP,
    private http: HttpClient,
    private utils: Utils,
    private crypto: Crypto,
    private translate: TranslateService,
    private toastr: ToastrService,
  ){
    router.events.subscribe((url:any) => {
      if (url instanceof NavigationEnd){
          this.currentUrl = url.url;
      }
    });

  }

  ngOnInit(){
    if(this.userService.getId() == null  && !this.userService.getIsVaultLocal()){
      this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
    } 
    this.secret_uuid = this.route.snapshot.paramMap.get('id');
    if(this.secret_uuid == null){
        this.isEditing = false;
        if(this.currentUrl != "/vault/add"){
          this.router.navigate(["/vault"], {relativeTo:this.route.root});
          return;
        }
        if(this.QRCodeService.getLabel() != undefined && this.QRCodeService != undefined){
          this.name = this.QRCodeService.getLabel()!
          this.secret = this.QRCodeService.getSecret()!
        }
        this.get_preferences()
        this.translate.get("blue").subscribe((default_color: string) => {
        this.selected_color = default_color;
        });
        this.remainingTags = this.userService.getVaultTags();
        
    } else {
      this.isEditing = true;
      console.log("is editing")
      if(!this.userService.getIsVaultLocal()){
        this.getSecretTOTP()
        this.get_preferences()
      } else {
        const vault = this.userService.getVault()!;
        const property = vault.get(this.secret_uuid);
        this.uuid = this.secret_uuid!;
        this.name = property!.get("name")!;
        this.secret = property!.get("secret")!;
        this.color = property!.get("color")!;
        if(property!.has("uri")){
          this.uri = property!.get("uri")!;
        }
        if(property!.has("favicon")){
          this.favicon = property!.get("favicon")! == "true";
          if(this.favicon){
            this.loadFavicon()
          }
        }
        if(property!.has("tags")){
          this.tags = this.utils.parseTags(property!.get("tags")!); // no remaining tags because the vault is local
        }

      }
    }
    
    this.totp_code_generation_interval = setInterval(()=> { this.compute_totp_expiration() }, 100);
    this.generateCode();
  }

  ngOnDestroy() {
    if(this.totp_code_generation_interval != undefined){
      clearInterval(this.totp_code_generation_interval);
    }
  }

  checkName(){
    this.nameError = "";
    if(this.name == ""){
      this.nameError = "totp.error.name_empty";
      return;
    }
    if(this.utils.sanitize(this.name) != this.name){
      this.nameError = "totp.error.char";
      return;
    }
  }

  checkURI(){
    this.uriError = "";
    if(this.utils.sanitize(this.uri) != this.uri){
      this.uriError =  "totp.error.char";
      return;
    }
    if(this.uri != "") {
      if(!this.uri.startsWith("http://") && !this.uri.startsWith("https://")){
        this.uri = "https://" + this.uri;
      }
    }
    if(this.favicon == true){
      if(this.uri == ""){
        this.uriError = "totp.error.fav_empty";
        return;
      } else {
        this.loadFavicon()
      }
    }
  }




  compute_totp_expiration(){
      const now = Date.now();
      const remaining = this.totp_code_expiration - now;
      this.progress_bar_percent = (remaining/300);
      if(remaining < 0 && !this.generating_next_totp_code) {
        this.generating_next_totp_code = true;
        this.generateCode();
      } 
  }

  generateCode(){
  try {
    if(this.secret == ""){ return;}
    this.secret = this.secret.replace(/\s/g, "");
      this.code=TOTP.generate(this.secret).otp;
      this.totp_code_expiration = TOTP.generate(this.secret).expires;
      this.generating_next_totp_code = false
      } catch(e) {
        console.log(e)
        this.code = this.translate.instant("totp.error.code");
        this.generating_next_totp_code = false
    }
   }
   

  checkSecret(){
    this.secretError = "";
    this.secret = this.secret.replace(/\s/g, "");
    if(this.secret == ""){
      this.secretError = "totp.error.secret_empty" ;
      return;
    }

    if(this.secret != this.utils.sanitize(this.secret)){
      this.secretError = "totp.error.char";
      return;
    }
    this.generateCode();
  }

  changeColor(colorSelected:string){
    this.translate.get("blue").subscribe((translation: string) => {
    switch(colorSelected){
      case translation:{
        this.color = "info";
        break;
      }
      case this.translate.instant("green"):{
        this.color = "success";
        break;
      }
      case this.translate.instant("orange"):{
        this.color = "warning";
        break;
      }
      case this.translate.instant("red"):{
        this.color = "danger";
        break;
      }
      default:{
        this.color = "info";
        break;
      }
    }
  });
  }

  cancel(){
    this.router.navigate(["/vault"], {relativeTo:this.route.root});
  }

  get_preferences(){
    this.http.get("/api/v1/preferences?fields=favicon_policy", {withCredentials: true, observe: 'response'}).subscribe((response) => {
      if(response.body != null){
        const data = JSON.parse(JSON.stringify(response.body));
        if(data.favicon_policy != null){
          this.faviconPolicy = data.favicon_policy;
          if (this.faviconPolicy == "always"){
            this.favicon = true;
          }
        } else {
          this.faviconPolicy = "enabledOnly";
          this.translate.get("totp.favicon_policy.enabledOnly").subscribe((translation: string) => {
            this.utils.toastError(this.toastr,translation,"")
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
          this.utils.toastError(this.toastr, this.translate.instant("totp.error.update_pref") + this.translate.instant(errorMessage),"");
    });
  }

  getSecretTOTP(){
    this.uuid = this.secret_uuid!;
    this.http.get("/api/v1/encrypted_secret/"+this.uuid,  {withCredentials:true, observe: 'response'}).subscribe((response) => {
      try{
        const data = JSON.parse(JSON.stringify(response.body));
        this.crypto.decrypt(data.enc_secret, this.userService.get_zke_key()!).then((decrypted_secret)=>{
          if(decrypted_secret == null){
            this.translate.get("totp.error.decryption").subscribe((translation: string) => {
              this.utils.toastWarning(this.toastr,translation,"")
            });
          } else {
            const property = this.utils.mapFromJson(decrypted_secret);
            this.uuid = this.secret_uuid!;
            this.name = property.get("name")!;
            this.secret = property.get("secret")!;
            this.color = property.get("color")!;
            this.translate.get("blue").subscribe((blue: string) => {
            switch(this.color){
              case "info":{
                this.selected_color = blue;
                break;
              }
              case "success":{
                this.selected_color = this.translate.instant("green");
                break;
              }
              case "warning":{
                this.selected_color = this.translate.instant("orange");
                break;
              }
              case "danger":{
                this.selected_color = this.translate.instant("red");
                break;
              }
              default:{
                this.selected_color = blue;
                break;
              }
            }
          });
            if(property!.has("uri")){
              this.uri = property!.get("uri")!;
            }
            if(property!.has("favicon")){
              this.favicon = property!.get("favicon")! == "true";
              if(this.favicon){
                this.loadFavicon()
              }
            }
            if(property!.has("tags")){
              this.tags = this.utils.parseTags(property!.get("tags")!);
            }
          if(property!.has("tags")){
            this.tags = this.utils.parseTags(property!.get("tags")!);
          }
          for(let tag of this.userService.getVaultTags()){
            if(!this.tags.includes(tag)){
              this.remainingTags.push(tag);
            }
          }
    
          }
        });
      } catch {
        this.translate.get("totp.error.fetch_secret").subscribe((translation: string) => {
            this.utils.toastWarning(this.toastr,translation,"")
      });
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
      } else if (error.status == 401){
        this.userService.clear();
        this.router.navigate(["/login/sessionEnd"], {relativeTo:this.route.root});
        return;
      }
      this.translate.get("totp.error.fetch_secret_server").subscribe((translation: string) => {
      this.utils.toastError(this.toastr, translation  + " " +this.translate.instant(errorMessage),"");
      });
    });
  }

  save(){
    this.isSaving = true;
    if(this.userService.getId() == null){
      this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
    }

    this.checkName();
    this.checkSecret();
    this.checkURI();
    if(this.nameError != "" || this.secretError != "" ){
      this.isSaving = false;
      return;
    }
    if(this.code == this.translate.instant("totp.error.code")){
      this.utils.toastError(this.toastr, this.translate.instant("totp.error.code"),"");
      this.isSaving = false;
      return;
    }
   
    
    const property = new Map<string,string>();
    property.set("secret", this.secret);
    property.set("color", this.color);
    property.set("name", this.name);
    property.set("uri", this.uri);
    property.set("favicon", this.favicon.toString());
    property.set("tags", JSON.stringify(this.tags));
    if(this.uri != ""){
      if(this.uri.startsWith("http://") || this.uri.startsWith("https://")){
        const parsedUrl = new URLParse(this.uri);
      const domain = parsedUrl.hostname;
      property.set("domain", domain)
      }
    }
    
    const jsonProperty = this.utils.mapToJson(property);
    try{
      this.crypto.encrypt(jsonProperty, this.userService.get_zke_key()!).then  ((enc_jsonProperty)=>{
        if(this.secret_uuid != null){
          this.updateSecret(enc_jsonProperty, property);
        } else { 
          this.addNewSecret(enc_jsonProperty, property);
        }
        this.isSaving = false;
      });
    } catch {
      this.translate.get("totp.error.encryption").subscribe((translation: string) => {
        this.utils.toastWarning(this.toastr,  translation ,"");
        this.isSaving = false;
    });
    }
    this.isSaving = false;
  }

  addNewSecret(enc_property:string, property: Map<string,string>){
    this.http.post("/api/v1/encrypted_secret", {enc_secret:enc_property}, {withCredentials:true, observe: 'response'}).subscribe((response) => {      
      const data = JSON.parse(JSON.stringify(response.body))
      this.uuid = data.uuid;
      this.utils.toastSuccess(this.toastr,  this.translate.instant("totp.secret.add.added"),"");
      this.QRCodeService.setLabel('')
      this.QRCodeService.setSecret('')
      this.router.navigate(["/vault"], {relativeTo:this.route.root});
    }, (error) => {
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
      this.translate.get("totp.error.update").subscribe((translation: string) => {
        this.utils.toastWarning(this.toastr,  translation  + " " +this.translate.instant(errorMessage),"");
    });
    });
  }

  updateSecret(enc_property:string, property: Map<string,string>){
    this.http.put("/api/v1/encrypted_secret/"+this.uuid, {enc_secret:enc_property}, {withCredentials:true, observe: 'response'}).subscribe((response) => {      
      this.utils.toastSuccess(this.toastr, this.translate.instant("totp.secret.add.success") ,"");
      this.router.navigate(["/vault"], {relativeTo:this.route.root});
    }, (error) => {
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
      this.translate.get("totp.error.update").subscribe((translation: string) => {
        this.utils.toastWarning(this.toastr,  translation + " " + this.translate.instant(errorMessage),"");
    });
    });
  }

  delete(){
    this.isDestroying = true;
    this.http.delete("/api/v1/encrypted_secret/"+this.secret_uuid, {withCredentials:true, observe: 'response'}).subscribe((response) => {
      if(response.status == 201){
      this.isDestroying = false;
      this.utils.toastSuccess(this.toastr, this.translate.instant("totp.secret.delete.success"),"");
      this.router.navigate(["/vault"], {relativeTo:this.route.root});
    } else {
      this.isDestroying = false;
      this.utils.toastWarning(this.toastr,  this.translate.instant("totp.error.deleting"),"");
    }
     
    } , (error) => {
      this.isDestroying = false;
      let errorMessage = "";
      if(error.error.message != null){
        errorMessage = error.error.message;
      } else if(error.error.detail != null){
        errorMessage = error.error.detail;
      }
      this.utils.toastWarning(this.toastr,  this.translate.instant("totp.error.deleting") + " " + errorMessage,"");
    });
    
  }

  loadFavicon(){
    this.uriError = "";
    if(this.favicon == true){
      if(this.uri != ""){
        if(!this.uri.startsWith("http://") && !this.uri.startsWith("https://")){
          this.uriError = "totp.error.missing_https";
            return;
        }
        try{
          const parsedUrl = new URLParse(this.uri);
           const domain = parsedUrl.hostname;
           if(domain != null && domain != ""){
            if (this.utils.domain_name_validator(domain)){
              this.faviconURL = "https://icons.duckduckgo.com/ip3/" +domain + ".ico";
            } else {
              this.uriError = "totp.error.invalid_domain";
              return;
            }
           } else {
            this.uriError ="totp.error.invalid_uri" ;
            return;
           }
        } catch{
          this.uriError = "totp.error.invalid_uri";
          return;
        }
        
       
      } else {
        this.uriError = "totp.error.no_fav";
      }
    }
  }

  modal(){
    if(!this.isDestroying){
      this.isModalActive = !this.isModalActive;
    }
  }

  tagModal(){
    this.addTagName = "";
      this.isTagModalActive = !this.isTagModalActive;
  }

  addTag(){
    if(this.addTagName != ""){
      if(this.tags.includes(this.addTagName)){
        this.utils.toastWarning(this.toastr, this.translate.instant("totp.error.tag_exists"),"")
      } else if (this.addTagName.length > 30){
        this.utils.toastWarning(this.toastr, this.translate.instant("totp.error.tag_length"),"")
      } else {
       this.tags.push(this.addTagName);
       if(this.remainingTags.includes(this.addTagName)){
        this.remainingTags = this.remainingTags.filter(item => item !== this.addTagName);
       }
       this.addTagName = "";
       this.toastr.clear()
       this.tagModal()
      }
    } else {
      this.utils.toastWarning(this.toastr, this.translate.instant("totp.error.tag_empty"),"")
    }
    
  }

  selectTag(tag:string){
    this.tags.push(tag);
    this.addTagName = "";
       this.toastr.clear()
       this.tagModal()
       this.remainingTags = this.remainingTags.filter(item => item !== tag);
  }

  deleteTag(tag:string){
    this.tags = this.tags.filter(item => item !== tag);
    if(this.userService.getVaultTags().includes(tag)){
      this.remainingTags.push(tag);
    }
  }

}
