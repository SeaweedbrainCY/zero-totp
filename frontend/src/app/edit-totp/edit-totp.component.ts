import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute, NavigationEnd } from '@angular/router';
import { UserService } from '../common/User/user.service';
import { HttpClient } from '@angular/common/http';
import { faChevronCircleLeft, faGlobe, faKey } from '@fortawesome/free-solid-svg-icons';
import { Utils  } from '../common/Utils/utils';
import { toast as superToast } from 'bulma-toast'
import { ApiService } from '../common/ApiService/api-service';
import { Crypto } from '../common/Crypto/crypto';
import { QrCodeTOTP } from '../common/qr-code-totp/qr-code-totp.service';

@Component({
  selector: 'app-edit-totp',
  templateUrl: './edit-totp.component.html',
  styleUrls: ['./edit-totp.component.css']
})
export class EditTOTPComponent implements OnInit{
  faChevronCircleLeft = faChevronCircleLeft;
  faGlobe = faGlobe;
  faKey = faKey;
  name = "";
  uuid="";
  secret = "";
  nameError = "";
  secretError = "";
  color="info";
  selected_color="Blue";
  totp = require('totp-generator');
  code = "";
  time=80;
  duration = 0;
  currentUrl:string = "";
  secret_uuid:string|null = null;
  superToast = require('bulma-toast');
  isModalActive = false;  
  isDestroying = false;
  constructor(
    private router: Router,
    private route : ActivatedRoute,
    private userService : UserService,
    private QRCodeService : QrCodeTOTP,
    private http: HttpClient,
    private utils: Utils,
    private crypto: Crypto,
  ){
    router.events.subscribe((url:any) => {
      if (url instanceof NavigationEnd){
          this.currentUrl = url.url;
      }
    });
  }

  ngOnInit(){
    if(this.userService.getId() == null){
      this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
    }
    this.secret_uuid = this.route.snapshot.paramMap.get('id');
    console.log(this.secret_uuid)
    if(this.secret_uuid == null){
        if(this.currentUrl != "/vault/add"){
          this.router.navigate(["/vault"], {relativeTo:this.route.root});
          return;
        }
        if(this.QRCodeService.getLabel() != undefined && this.QRCodeService != undefined){
          this.name = this.QRCodeService.getLabel()!
          this.secret = this.QRCodeService.getSecret()!
        }
    } else {
      this.getSecretTOTP()
    }

    setInterval(()=> { this.generateCode() }, 100);
    setInterval(()=> { this.generateTime() }, 20);
  }

  checkName(){
    this.nameError = "";
    if(this.name == ""){
      this.nameError = "Domain cannot be empty";
      return;
    }
    if(this.name.length > 30){
      this.nameError = "Domain cannot be longer than 30 characters";
      return;
    }
    if(this.utils.sanitize(this.name) != this.name){
      this.nameError = "&, <, >, \" and ' are forbidden";
      return;
    }
  }

  generateTime(){
    const duration = 30 - Math.floor(Date.now() / 10 % 3000)/100;
    this.time = (duration/30)*100
  }

  generateCode(){
   this.code=this.totp(this.secret);
  
   }
   

  checkSecret(){
    if(this.secret == ""){
      this.secretError = "Secret cannot be empty";
      return;
    }

    if(this.secret != this.utils.sanitize(this.secret)){
      this.secretError = "&, <, >, \" and ' are forbidden";
      return;
    }
    this.generateCode();
  }

  changeColor(colorSelected:string){
    console.log(colorSelected)
    switch(colorSelected){
      case "Blue":{
        this.color = "info";
        break;
      }
      case "Green":{
        this.color = "primary";
        break;
      }
      case "Orange":{
        this.color = "warning";
        break;
      }
      case "Red":{
        this.color = "danger";
        break;
      }
      default:{
        this.color = "info";
        break;
      }
    }
  }

  cancel(){
    this.router.navigate(["/vault"], {relativeTo:this.route.root});
  }

  getSecretTOTP(){
    this.uuid = this.secret_uuid!;
    this.http.get(ApiService.API_URL+"/encrypted_secret/"+this.uuid,  {withCredentials:true, observe: 'response'}).subscribe((response) => {
      try{
        const data = JSON.parse(JSON.stringify(response.body));
        console.log("dara = " + data.enc_secret)
        this.crypto.decrypt(data.enc_secret, this.userService.get_zke_key()!).then((decrypted_secret)=>{
          console.log("decrypted secret = " + decrypted_secret)
          if(decrypted_secret == null){
            superToast({
              message: "An error occured while decrypting your secret",
             type: "is-warning",
              dismissible: false,
              duration: 20000,
            animate: { in: 'fadeIn', out: 'fadeOut' }
            });
          } else {
            const property = this.utils.mapFromJson(decrypted_secret);
            this.uuid = this.secret_uuid!;
            this.name = property.get("name")!;
            this.secret = property.get("secret")!;
            this.color = property.get("color")!;
            switch(this.color){
              case "info":{
                this.selected_color = "Blue";
                break;
              }
              case "primary":{
                this.selected_color = "Green";
                break;
              }
              case "warning":{
                this.selected_color = "Orange";
                break;
              }
              case "danger":{
                this.selected_color = "Red";
                break;
              }
              default:{
                this.selected_color = "Blue";
                break;
              }
            }
          }
        });
      } catch {
        superToast({
          message: "An error occured while getting your secret",
         type: "is-warning",
          dismissible: false,
          duration: 20000,
        animate: { in: 'fadeIn', out: 'fadeOut' }
        });
      }
    });
  }

  save(){
    if(this.userService.getId() == null){
      this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
    }
    const property = new Map<string,string>();
    property.set("secret", this.secret);
    property.set("color", this.color);
    property.set("name", this.name);
    const jsonProperty = this.utils.mapToJson(property);
    try{
      this.crypto.encrypt(jsonProperty, this.userService.get_zke_key()!, this. userService.getDerivedKeySalt()!).then  ((enc_jsonProperty)=>{
        if(this.secret_uuid != null){
          this.updateSecret(enc_jsonProperty, property);
        } else { 
          this.addNewSecret(enc_jsonProperty, property);
        }
      });
    } catch {
      superToast({
        message: "An error happened while encrypting your secret",
       type: "is-warning",
        dismissible: false,
        duration: 20000,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    }
  }

  addNewSecret(enc_property:string, property: Map<string,string>){
    this.uuid = window.crypto.randomUUID();
    this.http.post(ApiService.API_URL + "/encrypted_secret/"+this.uuid, {enc_secret:enc_property}, {withCredentials:true, observe: 'response'}).subscribe((response) => {      
      superToast({
        message: "TOTP code updated !",
        type: "is-success",
        dismissible: true,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
      this.router.navigate(["/vault"], {relativeTo:this.route.root});
    }, (error) => {
      let errorMessage = "";
      if(error.error.message != null){
        errorMessage = error.error.message;
      } else if(error.error.detail != null){
        errorMessage = error.error.detail;
      }
      superToast({
        message: "An error occured while updating your vault with a new code. "+ errorMessage,
       type: "is-warning",
        dismissible: false,
        duration: 20000,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    });
  }

  updateSecret(enc_property:string, property: Map<string,string>){
    this.http.put(ApiService.API_URL + "/encrypted_secret/"+this.uuid, {enc_secret:enc_property}, {withCredentials:true, observe: 'response'}).subscribe((response) => {      
      superToast({
        message: "New TOTP code added ! ",
        type: "is-success",
        dismissible: true,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
      this.router.navigate(["/vault"], {relativeTo:this.route.root});
    }, (error) => {
      let errorMessage = "";
      if(error.error.message != null){
        errorMessage = error.error.message;
      } else if(error.error.detail != null){
        errorMessage = error.error.detail;
      }
      superToast({
        message: "An error occured while updating your vault with a new code. "+ errorMessage,
       type: "is-warning",
        dismissible: false,
        duration: 20000,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    });
  }

  delete(){
    this.isDestroying = true;
    this.http.delete(ApiService.API_URL + "/encrypted_secret/"+this.secret_uuid, {withCredentials:true, observe: 'response'}).subscribe((response) => {
      if(response.status == 201){
      this.isDestroying = false;
      superToast({
        message: "TOTP code deleted !",
        type: "is-success",
        dismissible: true,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
      this.router.navigate(["/vault"], {relativeTo:this.route.root});
    } else {
      this.isDestroying = false;
      superToast({
        message: "An error occured while deleting your secret.",
       type: "is-warning",
        dismissible: false,
        duration: 20000,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    }
     
    } , (error) => {
      this.isDestroying = false;
      let errorMessage = "";
      if(error.error.message != null){
        errorMessage = error.error.message;
      } else if(error.error.detail != null){
        errorMessage = error.error.detail;
      }
      superToast({
        message: "An error occured while deleting your secret. "+ errorMessage,
       type: "is-warning",
        dismissible: false,
        duration: 20000,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    });
    
  }

  modal(){
    if(!this.isDestroying){
      this.isModalActive = !this.isModalActive;
    }
  }

}
