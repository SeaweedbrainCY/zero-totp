import { Component, OnInit } from '@angular/core';
import { faEnvelope, faKey,  faCheck, faUser, faXmark, faFlagCheckered, faEye, faEyeSlash , faFlask} from '@fortawesome/free-solid-svg-icons';
import { faDiscord } from '@fortawesome/free-brands-svg-icons';
import { HttpClient } from '@angular/common/http';
import { ApiService } from '../common/ApiService/api-service';
import { toast } from 'bulma-toast';
import { toast as superToast } from 'bulma-toast'
import { Utils } from '../common/Utils/utils';
import { Crypto } from '../common/Crypto/crypto';
import { ActivatedRoute, Router } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';


@Component({
  selector: 'app-signup',
  templateUrl: './signup.component.html',
  styleUrls: ['./signup.component.css']
})
export class SignupComponent implements OnInit {
  faEnvelope=faEnvelope;
  faKey=faKey;
  faCheck=faCheck;
  faUser=faUser;
  faDiscord=faDiscord;
  faXmark=faXmark;
  faFlagCheckered=faFlagCheckered;
  faEye=faEye;
  faEyeSlash=faEyeSlash;
  faFlask=faFlask;
  username="";
  email="";
  password="";
  confirmPassword="";
  terms=false;
  isLoading=false;
  declare bulmaToast : any;
  emailErrorMessage = "";
  usernameErrorMessage=""
  passwordErrorMessage : [string]=[""];
  isModalActive=false;
  input="";
  encryptedZKEkey=""
  derivedKeySalt=""
  passphraseSalt=""
  modal_confim_button_diabled=true;
  beta=false;
  isModalSentenceCompleted=false;
  isPasswordVisible=false;
  isConfirmPasswordVisible=false;


  constructor(
    private http: HttpClient,
    private utils: Utils,
    private crypto:Crypto,
    private router: Router,
    private route: ActivatedRoute,
    private translate: TranslateService
    ) { }

  ngOnInit(): void {
    return;
  }

  checkPassword(){
    this.passwordErrorMessage=[""];
    const special = /[!@#$%^&*()_+\-=[\]{};:\\|,./?~]/;
    const upper = /[A-Z]/;
    const number = /[0-9]/;
    if(this.password.length < 12){
      this.passwordErrorMessage.push(this.translate.instant("signup.passphrase.error.char"));
    }
    
    if(!special.test(this.password)){
      this.passwordErrorMessage.push(this.translate.instant("signup.passphrase.error.special_char"));
    }
    if(!upper.test(this.password)){
      this.passwordErrorMessage.push(this.translate.instant("signup.passphrase.error.upper"));
    }
    if(!number.test(this.password)){
      this.passwordErrorMessage.push(this.translate.instant("signup.passphrase.error.number"));
    }
    if(this.password != this.confirmPassword){
      this.passwordErrorMessage.push(this.translate.instant("signup.passphrase.error.match"));
    }

  }

  checkEmail(){
    const forbidden = /["\'<>]/
    this.emailErrorMessage = "";
    if(this.email == "" ){
      this.emailErrorMessage = " ";
      return;
    }
    const emailRegex = /\S+@\S+\.\S+/;
    if(!emailRegex.test(this.email)){
      this.emailErrorMessage = this.translate.instant("signup.email.error.invalid");
      return;
    }
    if(forbidden.test(this.email)){
      this.emailErrorMessage = this.translate.instant("signup.email.error.forbidden");
      return;
    }
  }

  checkUsername(){
    const forbidden = /["\'<>]/
    this.usernameErrorMessage = "";
    if(this.username == "" ){
      this.usernameErrorMessage = " ";
      return;
    }
    if(forbidden.test(this.username)){
      this.usernameErrorMessage =  this.translate.instant("signup.username.error.forbidden");
      return;
    }
  }


  signup() {
    if(!this.isModalSentenceCompleted){
      this.openModal();
    } else {
this.closeModal()
    this.emailErrorMessage="";
    this.usernameErrorMessage="";
    this.passwordErrorMessage = [''];
    if(!this.terms){
      superToast({
        message: this.translate.instant("signup.errors.terms"),
        type: "is-danger",
        dismissible: true,
        duration: 20000,
        animate: { in: 'fadeIn', out: 'fadeOut' }
      });
      return;
    }
    if(!this.beta){
      superToast({
        message: this.translate.instant("signup.errors.beta"),
        type: "is-danger",
        dismissible: true,
        duration: 20000,
        animate: { in: 'fadeIn', out: 'fadeOut' },
      });
      return;
    }
    if(this.username == "" || this.email == "" || this.password == ""){
      superToast({
        message: this.translate.instant("signup.errors.missing_fields") ,
        type: "is-danger",
        dismissible: true,
        duration: 20000,
        animate: { in: 'fadeIn', out: 'fadeOut' },
        extraClasses: "has-text-weight-bold "
      });
      return;
    }
    this.checkPassword();
    this.checkEmail();
    this.checkUsername();
    if(this.emailErrorMessage != '' || this.passwordErrorMessage.length > 1  || this.usernameErrorMessage != ''){return;}
    this.isLoading=true;
    const ZKEkey = this.crypto.generateZKEKey();
    const randomSalt = this.crypto.generateRandomSalt();
    this.crypto.deriveKey(randomSalt, this.password).then((key) => {
      this.crypto.encrypt(ZKEkey, key).then((encryptedZKEkey) => {
        this.encryptedZKEkey = encryptedZKEkey
        this.derivedKeySalt = randomSalt
        this.hashPassword()
      });
    });   
  }
  }

  hashPassword(){
    this.passphraseSalt = this.crypto.generateRandomSalt();
        this.crypto.hashPassphrase(this.password, this.passphraseSalt).then(hashed => {
          if(hashed != null){
            this.password = hashed;
            this.signupRequest();
          } else {
            superToast({
              message: this.translate.instant("signup.errors.hashing") ,
              type: "is-danger",
              dismissible: false,
              duration: 20000,
              animate: { in: 'fadeIn', out: 'fadeOut' }
            });
          }
        });
  }

  signupRequest(){
    const data = {
      username: this.username,
      email: this.email,
      password: this.password,
      ZKE_key: this.encryptedZKEkey,
      derivedKeySalt: this.derivedKeySalt,
      passphraseSalt: this.passphraseSalt
    };

    this.http.post(ApiService.API_URL+"/signup", data, {observe: 'response'}).subscribe((response) => {
      this.isLoading=false;
      superToast({
        message: this.translate.instant("signup.success"),
        type: "is-success",
        dismissible: true,
        animate: { in: 'fadeIn', out: 'fadeOut' }
      });
      this.router.navigate(["/emailVerification"], {relativeTo:this.route.root});

    },
    (error) => {
      console.log(error);
      this.isLoading=false;
      if(error.error.message == undefined){
        error.error.message = this.translate.instant("signup.errors.unknown");
      }
      superToast({
        message: "Error : "+ error.error.message,
        type: "is-danger",
        dismissible: true,
        duration: 20000,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    });
  }

 openModal(){
    this.isModalActive=true;
  }

  closeModal(){
    this.isModalActive=false;
  }

  confirmSentence(){
    if(this.input.replace(/[^a-zA-Z]/g, '') == this.translate.instant("signup.popup.phrase").replace(/[^a-zA-Z]/g, '')){
      this.modal_confim_button_diabled = false
      this.isModalSentenceCompleted = true
    }
  }
}
