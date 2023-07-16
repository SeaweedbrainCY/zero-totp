import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute, NavigationEnd } from '@angular/router';
import { UserService } from '../common/User/user.service';
import { HttpClient } from '@angular/common/http';
import { faChevronCircleLeft, faGlobe, faKey } from '@fortawesome/free-solid-svg-icons';
import { Utils  } from '../common/Utils/utils';
import { toast as superToast } from 'bulma-toast'
import { ApiService } from '../common/ApiService/api-service';
import { Crypto } from '../common/Crypto/crypto';

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
  getElementID:string|null = null;
  superToast = require('bulma-toast');
  constructor(
    private router: Router,
    private route : ActivatedRoute,
    private userService : UserService,
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
      //this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
    }
    this.getElementID = this.route.snapshot.paramMap.get('id');
    console.log(this.getElementID)
    if(this.getElementID == null){
        if(this.currentUrl != "/vault/add"){
          this.router.navigate(["/vault"], {relativeTo:this.route.root});
          return;
        }
    } else {
      const vault = this.userService.getVault();
      if(vault == null || !vault.has(this.getElementID)){
        this.router.navigate(["/vault"], {relativeTo:this.route.root});
        return;
      } else {
        const property = vault.get(this.getElementID)!;
        this.uuid = this.getElementID;
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
   if(this.code.length == 6){
    this.code = this.code[0]+this.code[1]+this.code[2] + " " + this.code[3]+this.code[4]+this.code[5] 
  }
  
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

  save(){
    if(this.userService.getId() == null){
      //this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
    }
    this.getVaultFromAPI(); // get the last up to date vault
   let vault = this.userService.getVault();
   if (vault == null){
    superToast({
      message: "Your session has expired. For safety reasons you have to log out and log in again.",
     type: "is-warning",
      dismissible: false,
      duration: 20000,
    animate: { in: 'fadeIn', out: 'fadeOut' }
    });
   }
    if(this.getElementID != null){
      vault!.delete(this.getElementID);
    } else {
      this.uuid = crypto.randomUUID();
    }
    const property = new Map<string,string>();
    property.set("secret", this.secret);
    property.set("color", this.color);
    property.set("name", this.name);
    
    vault!.set(this.uuid, property);
    this.userService.setVault(vault!);
    this.updateVault();
  }

  getVaultFromAPI(){
    this.http.get(ApiService.API_URL+"/vault",  {withCredentials:true, observe: 'response'}).subscribe((response) => {
      try{
        const data = JSON.parse(JSON.stringify(response.body))
       const enc_vault = data.enc_vault;
       if(this.userService.getKey() != null){
        try{
          this.crypto.decrypt(enc_vault, this.userService.getKey()!).then((dec_vault)=>{
            if(dec_vault == null){
              superToast({
                message: "Wrong key. You cannot decrypt this vault or the data retrieved is null. Please log out and log in again.",
               type: "is-warning",
                dismissible: false,
                duration: 20000,
              animate: { in: 'fadeIn', out: 'fadeOut' }
              });
            } else {
                try{
                  const vault = this.utils.vaultFromJson(dec_vault);
                  this.userService.setVault(vault);
                } catch {
                  superToast({
                    message: "Wrong key. You cannot decrypt this vault or the data retrieved not usable. Please log out and log in again.   ",
                   type: "is-warning",
                    dismissible: false,
                    duration: 20000,
                  animate: { in: 'fadeIn', out: 'fadeOut' }
                  });
                }
              }
          })
        } catch {
          superToast({
            message: "Wrong key. You cannot decrypt this vault.",
           type: "is-warning",
            dismissible: false,
            duration: 20000,
          animate: { in: 'fadeIn', out: 'fadeOut' }
          });
        }
      } else {
        superToast({
          message: "Impossible to decrypt your vault, you're decryption key has expired. Please log out and log in again.",
         type: "is-warning",
          dismissible: false,
          duration: 20000,
        animate: { in: 'fadeIn', out: 'fadeOut' }
        });
      }
      } catch(e){
        superToast({
          message: "Error : Impossible to retrieve your vault from the server",
         type: "is-warning",
          dismissible: false,
          duration: 20000,
        animate: { in: 'fadeIn', out: 'fadeOut' }
        });
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
        superToast({
          message: "Error : Impossible to retrieve your vault from the server. "+ errorMessage,
         type: "is-warning",
          dismissible: false,
          duration: 20000,
        animate: { in: 'fadeIn', out: 'fadeOut' }
        });
      }
    });
  }

  updateVault(){
    if(this.userService.getVault() == null || this.userService.getKey() == null){
      superToast({
        message: "Error : Impossible to encrypt your vault. For safety reasons, please log out and log in again.",
       type: "is-warning",
        dismissible: false,
        duration: 20000,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    } else {
      const jsonVault = this.utils.vaultToJson(this.userService.getVault()!);
      try {
        this.crypto.encrypt(jsonVault, this.userService.getKey()!, this. userService.getDerivedKeySalt()!).then((enc_vault)=>{
          this.http.put(ApiService.API_URL+"/vault", {enc_vault:enc_vault}, {withCredentials:true, observe: 'response'}).subscribe((response) => {
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
            message: "Error : Impossible to retrieve your vault from the server. "+ errorMessage,
           type: "is-warning",
            dismissible: false,
            duration: 20000,
          animate: { in: 'fadeIn', out: 'fadeOut' }
          });
          });
        });
      } catch {
        superToast({
          message: "An error happened while encrypting your vault",
         type: "is-warning",
          dismissible: false,
          duration: 20000,
        animate: { in: 'fadeIn', out: 'fadeOut' }
        });
      }

    }
    

  }
  

}
