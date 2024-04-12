import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute, NavigationEnd } from '@angular/router';
import { UserService } from '../common/User/user.service';
import { HttpClient } from '@angular/common/http';
import { faChevronCircleLeft, faGlobe, faKey, faCircleQuestion, faPassport, faPlus, faCheck } from '@fortawesome/free-solid-svg-icons';
import { Utils  } from '../common/Utils/utils';
import { ApiService } from '../common/ApiService/api-service';
import { Crypto } from '../common/Crypto/crypto';
import { QrCodeTOTP } from '../common/qr-code-totp/qr-code-totp.service';
import { LocalVaultV1Service } from '../common/upload-vault/LocalVaultv1Service.service';
import  * as URLParse from 'url-parse';
import { dom } from '@fortawesome/fontawesome-svg-core';
import { TranslateService } from '@ngx-translate/core';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-edit-totp',
  templateUrl: './edit-totp.component.html',
  styleUrls: ['./edit-totp.component.css']
})
export class EditTOTPComponent implements OnInit{
  faChevronCircleLeft = faChevronCircleLeft;
  faGlobe = faGlobe;
  faKey = faKey;
  faPassport = faPassport;
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
  totp = require('totp-generator');
  code = "";
  time=80;
  duration = 0;
  currentUrl:string = "";
  secret_uuid:string|null = null;
  isModalActive = false;  
  isDestroying = false;
  faviconPolicy=""; // never, always, enabledOnly
  tags:string[] = [];
  isTagModalActive = false;
  addTagName="";
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
        
    } else {
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
          this.tags = this.utils.parseTags(property!.get("tags")!);
        }

      }
    }
    

    setInterval(()=> { this.generateCode() }, 100);
    setInterval(()=> { this.generateTime() }, 20);
    

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
    this.nameError = "";
    if(this.utils.sanitize(this.uri) != this.uri){
      this.nameError =  "totp.error.char";
      return;
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

  generateTime(){
    const duration = 30 - Math.floor(Date.now() / 10 % 3000)/100;
    this.time = (duration/30)*100
  }

  generateCode(){
  try {
    this.secret = this.secret.replace(/\s/g, "");
      this.code=this.totp(this.secret);
      } catch(e) {
        this.code = this.translate.instant("totp.error.code");
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
    this.http.get(ApiService.API_URL+"/preferences?fields=favicon_policy", {withCredentials: true, observe: 'response'}).subscribe((response) => {
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
    this.http.get(ApiService.API_URL+"/encrypted_secret/"+this.uuid,  {withCredentials:true, observe: 'response'}).subscribe((response) => {
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
    if(this.userService.getId() == null){
      this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
    }

    this.checkName();
    this.checkSecret();
    this.checkURI();
    if(this.nameError != "" || this.secretError != "" || this.uriError != ""){
      return;
    }
    if(this.code == this.translate.instant("totp.error.code")){
      this.utils.toastError(this.toastr, this.translate.instant("totp.error.code"),"");
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
      });
    } catch {
      this.translate.get("totp.error.encryption").subscribe((translation: string) => {
        this.utils.toastWarning(this.toastr,  translation ,"");
    });
    }
  }

  addNewSecret(enc_property:string, property: Map<string,string>){
    this.uuid = window.crypto.randomUUID();
    this.http.post(ApiService.API_URL + "/encrypted_secret/"+this.uuid, {enc_secret:enc_property}, {withCredentials:true, observe: 'response'}).subscribe((response) => {      
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
    this.http.put(ApiService.API_URL + "/encrypted_secret/"+this.uuid, {enc_secret:enc_property}, {withCredentials:true, observe: 'response'}).subscribe((response) => {      
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
    this.http.delete(ApiService.API_URL + "/encrypted_secret/"+this.secret_uuid, {withCredentials:true, observe: 'response'}).subscribe((response) => {
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
      } else {
       this.tags.push(this.addTagName);
       this.addTagName = "";
       this.toastr.clear()
       this.tagModal()
      }
    } else {
      this.utils.toastWarning(this.toastr, this.translate.instant("totp.error.tag_empty"),"")
    }
    
  }

  deleteTag(tag:string){
    this.tags = this.tags.filter(item => item !== tag);
  }

}
