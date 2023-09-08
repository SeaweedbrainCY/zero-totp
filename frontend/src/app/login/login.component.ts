import { Component } from '@angular/core';
import { toast as superToast } from 'bulma-toast'
import { faEnvelope, faLock,  faCheck, faXmark, faFlagCheckered, faCloudArrowUp } from '@fortawesome/free-solid-svg-icons';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { ApiService } from '../common/ApiService/api-service';
import { Router, ActivatedRoute, NavigationEnd } from '@angular/router';
import { UserService } from '../common/User/user.service';
import {Crypto} from '../common/Crypto/crypto';
import { Buffer } from 'buffer';
import { UploadVaultService } from '../common/upload-vault/upload-vault.service';
@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  faEnvelope=faEnvelope;
  faLock=faLock;
  faCheck=faCheck;
  faXmark=faXmark;
  faFlagCheckered=faFlagCheckered;
  faCloudArrowUp=faCloudArrowUp;
  email:string = "";
  password:string = "";
  hashedPassword:string = "";
  isLoading = false;
  warning_message="";
  error_param: string|null=null;
  uploaded_vault:Map<string, Map<string,string>> | null =null;

  constructor(
    private http: HttpClient,
    private router: Router,
    private route: ActivatedRoute,
    private userService: UserService,
    private crypto:Crypto,
    private uploadVaultService: UploadVaultService
    ) {
    }

    ngOnInit(){
      this.error_param = this.route.snapshot.paramMap.get('error_param')
      switch(this.error_param){
        case null:{
          break;
        }
        case 'sessionKilled':{
          this.warning_message = "For your safety, you have been disconnected because you have reloaded or closed the tab";
          this.email = this.userService.getEmail() || "";
          this.userService.clear();
          break;
        }
        case 'sessionTimeout':{
          this.warning_message = "For your safety, you have been disconnected after 10min of inactivity"
          this.email = this.userService.getEmail() || "";
          this.userService.clear();
        }
      }
      
    }

  getZKEKeyAndNavigate(derivedKey: CryptoKey){
    this.http.get(ApiService.API_URL+"/zke_encrypted_key",  {withCredentials:true, observe: 'response'}).subscribe((response) => {
      const data = JSON.parse(JSON.stringify(response.body))
      const zke_key_encrypted = data.zke_encrypted_key
      this.crypto.decrypt(zke_key_encrypted, derivedKey).then(zke_key_b64=>{
        if (zke_key_b64 != null) {
          const zke_key_raw = Buffer.from(zke_key_b64!, 'base64');
          try{
          window.crypto.subtle.importKey(
            "raw",
            zke_key_raw,
            "AES-GCM",
            true,
            ["encrypt", "decrypt"]
          ).then((zke_key)=>{
            this.userService.set_zke_key(zke_key!);
          this.router.navigate(["/vault"], {relativeTo:this.route.root});
          });
        } catch(e) {
          superToast({
            message: "Error : Impossible to import your key." + e,
            type: "is-danger",
            dismissible: false,
            duration: 20000,
            animate: { in: 'fadeIn', out: 'fadeOut' }
          });
        }
        } else {
          superToast({
            message: "Impossible to decrypt your key",
            type: "is-danger",
            dismissible: false,
            duration: 20000,
            animate: { in: 'fadeIn', out: 'fadeOut' }
          });
        }
      
      });
    }, (error)=> {
      superToast({
        message: "Impossible to retrieve your encryption key. Please try again later",
        type: "is-danger",
        dismissible: false,
        duration: 20000,
        animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    });
    
  }


  deriveKeyAndNavigate(){
    const derivedKeySalt = this.userService.getDerivedKeySalt();
    if(derivedKeySalt != null){
      this.crypto.deriveKey(derivedKeySalt, this.password).then(key=>{
       this.getZKEKeyAndNavigate(key)
      });
    } else {
      this.isLoading=false;
      superToast({
        message: "Impossible to retrieve enough data to decrypt your vault",
        type: "is-success",
        dismissible: true,
        animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    }
    
  }

  checkEmail() : boolean{
    const emailRegex = /\S+@\S+\.\S+/;
    if(!emailRegex.test(this.email)){
      superToast({
        message: "Are your sure about your email ? ",
        type: "is-danger",
        dismissible: true,
        animate: { in: 'fadeIn', out: 'fadeOut' }
      });
      return false;
    } else {
      return true;
    }
  }

  
  login(){
    if(this.email == "" || this.password == ""){
      superToast({
        message: "Did you forget to fill something ?",
        type: "is-danger",
        dismissible: true,
        animate: { in: 'fadeIn', out: 'fadeOut' }
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
    reader.onload = (() => {
      if (reader.result) {
        try{
          const unsecure_context = reader.result.toString();
          this.uploaded_vault = this.uploadVaultService.parseVault(unsecure_context);
        }
        catch(e){
          superToast({
            message: "Error : Impossible to parse your file",
            type: "is-danger",
            dismissible: false,
            duration: 20000,
            animate: { in: 'fadeIn', out: 'fadeOut' }
          });
        }
      }
    });
    reader.readAsText(input.files[0], 'utf-8');
    }

  hashPassword(){
    this.http.get(ApiService.API_URL+"/login/specs?username="+this.email,  {withCredentials:true, observe: 'response'}).subscribe((response) => {
      
      try{
        const data = JSON.parse(JSON.stringify(response.body))
        const salt = data.passphrase_salt
        this.crypto.hashPassphrase(this.password, salt).then(hashed => {
          if(hashed != null){
            this.hashedPassword = hashed;
            this.userService.setPassphraseSalt(salt);
            this.postLoginRequest();
          } else {
            superToast({
              message: "An error occured while hashing your password. Please, try again",
              type: "is-danger",
              dismissible: false,
              duration: 20000,
              animate: { in: 'fadeIn', out: 'fadeOut' }
            });
          }
        });
      } catch {
        superToast({
          message: "An error occured while hashing your password. Please, try again",
          type: "is-danger",
          dismissible: false,
          duration: 20000,
          animate: { in: 'fadeIn', out: 'fadeOut' }
        });
      }
    }, error => {
      superToast({
        message: "Impossible to chat with the server ! \nCheck your internet connection or status.zero-totp.com",
        type: "is-danger",
        dismissible: false,
        duration: 20000,
        animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    });
  }


  postLoginRequest(){
    const data = {
      email: this.email,
      password: this.hashedPassword
    }
    this.http.post(ApiService.API_URL+"/login",  data, {withCredentials: true, observe: 'response'}).subscribe((response) => {
      superToast({
        message: "Welcome back",
        type: "is-success",
        dismissible: true,
        animate: { in: 'fadeIn', out: 'fadeOut' }
      });
      try{
        const data = JSON.parse(JSON.stringify(response.body))
        this.userService.setId(data.id);
        this.userService.setEmail(this.email);
        this.userService.setDerivedKeySalt(data.derivedKeySalt);
        this.deriveKeyAndNavigate();
      } catch(e){
        this.isLoading=false;
        console.log(e);
        superToast({
          message: "Error : Impossible ro retrieve information from server",
          type: "is-danger",
          dismissible: true,
        animate: { in: 'fadeIn', out: 'fadeOut' }
        });
      }
    },
    (error) => {
      console.log(error);
      this.isLoading=false;
      superToast({
        message: "Error : "+ error.error.message,
        type: "is-danger",
        dismissible: true,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    });
  }
}
