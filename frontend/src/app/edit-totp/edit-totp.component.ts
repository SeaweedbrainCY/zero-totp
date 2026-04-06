import { Component, OnDestroy, OnInit, signal, ChangeDetectionStrategy } from '@angular/core';
import { Router, ActivatedRoute, NavigationEnd } from '@angular/router';
import { UserService } from '../common/User/user.service';
import { HttpClient } from '@angular/common/http';
import { faChevronCircleLeft, faGlobe, faKey, faCircleQuestion, faPassport, faPlus, faCheck, faCircleNotch, faEyeSlash, faEye, faXmark } from '@fortawesome/free-solid-svg-icons';
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
    standalone: false,
    changeDetection: ChangeDetectionStrategy.OnPush,
})
export class EditTOTPComponent implements OnInit, OnDestroy{
  faChevronCircleLeft = faChevronCircleLeft;
  faGlobe = faGlobe;
  faKey = faKey;
  faPassport = faPassport;
  faCircleNotch = faCircleNotch;
  faPlus = faPlus;
  faCheck = faCheck;
  faEyeSlash=faEyeSlash;
  faXmark=faXmark;
  faEye=faEye;
  faCircleQuestion = faCircleQuestion;
  faviconURL = signal("");
  name = signal("");
  uri = signal("");
  favicon = signal(false);
  uuid="";
  secret = signal("");
  nameError = signal("");
  uriError = signal("");
  secretError = signal("");
  color = signal("info");
  selected_color = signal("");
  animationFrameId: number=0;
  code = signal("");
  progress_bar_percent = signal(80);
  currentUrl:string = "";
  secret_uuid:string|null = null;
  isModalActive = signal(false);
  isDestroying = signal(false);
  faviconPolicy = signal(""); // never, always, enabledOnly
  tags = signal<string[]>([]);
  isTagModalActive = signal(false);
  addTagName = signal("");
  isEditing = signal(false); // true if editing, false if adding
  isSaving = signal(false);
  remainingTags = signal<string[]>([]);
  isSecretVisible = signal(true);
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
    if(this.userService.get_zke_key() == null  && !this.userService.getIsVaultLocal()){
      this.userService.refresh_user_id().then((success) => {
        this.router.navigate(["/vault"], {relativeTo:this.route.root});
      }, (error) => {
        this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
      });
    } 
    this.secret_uuid = this.route.snapshot.paramMap.get('id');
    if(this.secret_uuid == null){
        this.isEditing.set(false);
        if(this.currentUrl != "/vault/add"){
          this.router.navigate(["/vault"], {relativeTo:this.route.root});
          return;
        }
        if(this.QRCodeService.getLabel() != undefined && this.QRCodeService != undefined){
          this.name.set(this.QRCodeService.getLabel()!);
          this.secret.set(this.QRCodeService.getSecret()!);
        }
        this.get_preferences()
        this.translate.get("blue").subscribe((default_color: string) => {
          this.selected_color.set(default_color);
        });
        this.remainingTags.set(this.userService.getVaultTags());
        
    } else {
      this.isEditing.set(true);
      this.isSecretVisible.set(false);
      console.log("is editing")
      if(!this.userService.getIsVaultLocal()){
        this.getSecretTOTP()
        this.get_preferences()
      } else {
        const vault = this.userService.getVault()!;
        const property = vault.get(this.secret_uuid);
        this.uuid = this.secret_uuid!;
        this.name.set(property!.get("name")!);
        this.secret.set(property!.get("secret")!);
        this.color.set(property!.get("color")!);
        if(property!.has("uri")){
          this.uri.set(property!.get("uri")!);
        }
        if(property!.has("favicon")){
          this.favicon.set(property!.get("favicon")! == "true");
          if(this.favicon()){
            this.loadFavicon()
          }
        }
        if(property!.has("tags")){
          this.tags.set(this.utils.parseTags(property!.get("tags")!)); // no remaining tags because the vault is local
        }

      }
    }
    
    this.totp_code_generation_interval = setInterval(()=> { this.compute_totp_expiration() }, 100);
    
  }

  ngOnDestroy() {
    if(this.totp_code_generation_interval != undefined){
      clearInterval(this.totp_code_generation_interval);
    }
  }

  checkName(){
    this.nameError.set("");
    if(this.name() == ""){
      this.nameError.set("totp.error.name_empty");
      return;
    }
    if(this.utils.sanitize(this.name()) != this.name()){
      this.nameError.set("totp.error.char");
      return;
    }
  }

  checkURI(){
    this.uriError.set("");
    if(this.utils.sanitize(this.uri()) != this.uri()){
      this.uriError.set("totp.error.char");
      return;
    }
    if(this.uri() != "") {
      if(!this.uri().startsWith("http://") && !this.uri().startsWith("https://")){
        this.uri.set("https://" + this.uri());
      }
    }
    if(this.favicon() == true){
      if(this.uri() == ""){
        this.uriError.set("totp.error.fav_empty");
        return;
      } else {
        this.loadFavicon()
      }
    }
  }




  compute_totp_expiration(){
      const now = Date.now();
      const remaining = this.totp_code_expiration - now;
      this.progress_bar_percent.set(remaining/300);
      if(remaining < 0 && !this.generating_next_totp_code) {
        this.generating_next_totp_code = true;
        this.generateCode();
      } 
  }

  generateCode(){
  try {
    if(this.secret() == ""){ return;}
    this.secret.set(this.secret().replace(/\s/g, ""));
      this.code.set(TOTP.generate(this.secret()).otp);
      this.totp_code_expiration = TOTP.generate(this.secret()).expires;
      this.generating_next_totp_code = false
      } catch(e) {
        console.log(e)
        this.code.set(this.translate.instant("totp.error.code"));
        this.generating_next_totp_code = false
    }
   }
   

  checkSecret(){
    this.secretError.set("");
    this.secret.set(this.secret().replace(/\s/g, ""));
    if(this.secret() == ""){
      this.secretError.set("totp.error.secret_empty");
      return;
    }

    if(this.secret() != this.utils.sanitize(this.secret())){
      this.secretError.set("totp.error.char");
      return;
    }
    this.generateCode();
  }

  changeColor(colorSelected:string){
    this.translate.get("blue").subscribe((translation: string) => {
    switch(colorSelected){
      case translation:{
        this.color.set("info");
        break;
      }
      case this.translate.instant("green"):{
        this.color.set("success");
        break;
      }
      case this.translate.instant("orange"):{
        this.color.set("warning");
        break;
      }
      case this.translate.instant("red"):{
        this.color.set("danger");
        break;
      }
      default:{
        this.color.set("info");
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
          this.faviconPolicy.set(data.favicon_policy);
          if (this.faviconPolicy() == "always"){
            this.favicon.set(true);
          }
        } else {
          this.faviconPolicy.set("enabledOnly");
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
            this.name.set(property.get("name")!);
            this.secret.set(property.get("secret")!);
            this.generateCode();
            this.color.set(property.get("color")!);
            this.translate.get("blue").subscribe((blue: string) => {
            switch(this.color()){
              case "info":{
                this.selected_color.set(blue);
                break;
              }
              case "success":{
                this.selected_color.set(this.translate.instant("green"));
                break;
              }
              case "warning":{
                this.selected_color.set(this.translate.instant("orange"));
                break;
              }
              case "danger":{
                this.selected_color.set(this.translate.instant("red"));
                break;
              }
              default:{
                this.selected_color.set(blue);
                break;
              }
            }
          });
            if(property!.has("uri")){
              this.uri.set(property!.get("uri")!);
            }
            if(property!.has("favicon")){
              this.favicon.set(property!.get("favicon")! == "true");
              if(this.favicon()){
                this.loadFavicon()
              }
            }
            if(property!.has("tags")){
              this.tags.set(this.utils.parseTags(property!.get("tags")!));
            }
          if(property!.has("tags")){
            this.tags.set(this.utils.parseTags(property!.get("tags")!));
          }
          for(let tag of this.userService.getVaultTags()){
            if(!this.tags().includes(tag)){
              this.remainingTags.update(rt => [...rt, tag]);
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
    this.isSaving.set(true);
    if(this.userService.getId() == null){
      this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
    }

    this.checkName();
    this.checkSecret();
    this.checkURI();
    if(this.nameError() != "" || this.secretError() != "" ){
      this.isSaving.set(false);
      return;
    }
    if(this.code() == this.translate.instant("totp.error.code")){
      this.utils.toastError(this.toastr, this.translate.instant("totp.error.code"),"");
      this.isSaving.set(false);
      return;
    }
   
    
    const property = new Map<string,string>();
    property.set("secret", this.secret());
    property.set("color", this.color());
    property.set("name", this.name());
    property.set("uri", this.uri());
    property.set("favicon", this.favicon().toString());
    property.set("tags", JSON.stringify(this.tags()));
    if(this.uri() != ""){
      if(this.uri().startsWith("http://") || this.uri().startsWith("https://")){
        const parsedUrl = new URLParse(this.uri());
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
        this.isSaving.set(false);
      });
    } catch {
      this.translate.get("totp.error.encryption").subscribe((translation: string) => {
        this.utils.toastWarning(this.toastr,  translation ,"");
        this.isSaving.set(false);
    });
    }
    this.isSaving.set(false);
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
    this.isDestroying.set(true);
    this.http.delete("/api/v1/encrypted_secret/"+this.secret_uuid, {withCredentials:true, observe: 'response'}).subscribe((response) => {
      if(response.status == 201){
      this.isDestroying.set(false);
      this.utils.toastSuccess(this.toastr, this.translate.instant("totp.secret.delete.success"),"");
      this.router.navigate(["/vault"], {relativeTo:this.route.root});
    } else {
      this.isDestroying.set(false);
      this.utils.toastWarning(this.toastr,  this.translate.instant("totp.error.deleting"),"");
    }
     
    } , (error) => {
      this.isDestroying.set(false);
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
    this.uriError.set("");
    if(this.favicon() == true){
      if(this.uri() != ""){
        if(!this.uri().startsWith("http://") && !this.uri().startsWith("https://")){
          this.uriError.set("totp.error.missing_https");
            return;
        }
        try{
          const parsedUrl = new URLParse(this.uri());
           const domain = parsedUrl.hostname;
           if(domain != null && domain != ""){
            if (this.utils.domain_name_validator(domain)){
              this.faviconURL.set("https://icons.duckduckgo.com/ip3/" +domain + ".ico");
            } else {
              this.uriError.set("totp.error.invalid_domain");
              return;
            }
           } else {
            this.uriError.set("totp.error.invalid_uri");
            return;
           }
        } catch{
          this.uriError.set("totp.error.invalid_uri");
          return;
        }
        
       
      } else {
        this.uriError.set("totp.error.no_fav");
      }
    }
  }

  modal(){
    if(!this.isDestroying()){
      this.isModalActive.update(v => !v);
    }
  }

  tagModal(){
    this.addTagName.set("");
    this.isTagModalActive.update(v => !v);
  }

  addTag(){
    if(this.addTagName() != ""){
      if(this.tags().includes(this.addTagName())){
        this.utils.toastWarning(this.toastr, this.translate.instant("totp.error.tag_exists"),"")
      } else if (this.addTagName().length > 30){
        this.utils.toastWarning(this.toastr, this.translate.instant("totp.error.tag_length"),"")
      } else {
       this.tags.update(t => [...t, this.addTagName()]);
       if(this.remainingTags().includes(this.addTagName())){
        this.remainingTags.update(rt => rt.filter(item => item !== this.addTagName()));
       }
       this.addTagName.set("");
       this.toastr.clear()
       this.tagModal()
      }
    } else {
      this.utils.toastWarning(this.toastr, this.translate.instant("totp.error.tag_empty"),"")
    }
    
  }

  selectTag(tag:string){
    this.tags.update(t => [...t, tag]);
    this.addTagName.set("");
    this.toastr.clear()
    this.tagModal()
    this.remainingTags.update(rt => rt.filter(item => item !== tag));
  }

  deleteTag(tag:string){
    this.tags.update(t => t.filter(item => item !== tag));
    if(this.userService.getVaultTags().includes(tag)){
      this.remainingTags.update(rt => [...rt, tag]);
    }
  }

}