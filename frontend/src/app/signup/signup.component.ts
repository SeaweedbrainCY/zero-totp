import { Component, OnInit } from '@angular/core';
import { faEnvelope, faLock,  faCheck, faUser, faXmark, faFlagCheckered } from '@fortawesome/free-solid-svg-icons';
import { HttpClient } from '@angular/common/http';
import { ApiService } from '../common/ApiService/api-service';
import { toast } from 'bulma-toast';
import { toast as superToast } from 'bulma-toast'
import { Utils } from '../common/Utils/utils';
import { Crypto } from '../common/Crypto/crypto';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-signup',
  templateUrl: './signup.component.html',
  styleUrls: ['./signup.component.css']
})
export class SignupComponent implements OnInit {
  faEnvelope=faEnvelope;
  faLock=faLock;
  faCheck=faCheck;
  faUser=faUser;
  faXmark=faXmark;
  faFlagCheckered=faFlagCheckered;
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

  constructor(
    private http: HttpClient,
    private utils: Utils,
    private crypto:Crypto,
    private router: Router,
    private route: ActivatedRoute
    ) { }

  ngOnInit(): void {
    return;
  }

  checkPassword(){
    this.passwordErrorMessage=[""];
    const special = /[!@#$%^&*()_+\-=[\]{};:\\|,./?~]/;
    const upper = /[A-Z]/;
    const number = /[0-9]/;
    const forbidden = /["\'<>]/
    if(this.password.length < 8){
      this.passwordErrorMessage.push("Your password must be at least 8 characters long");
    }
    else if(this.password.length > 70){
      this.passwordErrorMessage.push("Password must be less than 70 characters long");
    }
    if(!special.test(this.password)){
      this.passwordErrorMessage.push("Your password must contain at least one special character");
    }
    if(!upper.test(this.password)){
      this.passwordErrorMessage.push("Your password must contain at least one uppercase character");
    }
    if(!number.test(this.password)){
      this.passwordErrorMessage.push("Your password must contain at least one number");
    }
    if(forbidden.test(this.password)){
      this.passwordErrorMessage.push("' \" < > characters are forbidden in passwords");
    }
    if(this.password != this.confirmPassword){
      this.passwordErrorMessage.push("Your passwords do not match");
    }

  }

  checkEmail(){
    const forbidden = /["\'<>]/
    this.emailErrorMessage = "";
    const emailRegex = /\S+@\S+\.\S+/;
    if(!emailRegex.test(this.email)){
      this.emailErrorMessage = "Your email is not valid";
      return;
    }
    if(forbidden.test(this.email)){
      this.emailErrorMessage = "' \" < > characters are forbidden in passwords";
      return;
    }
  }

  checkUsername(){
    const forbidden = /["\'<>]/
    this.usernameErrorMessage = "";
    if(this.username == "" ){
      this.usernameErrorMessage = "Your username cannot be empty";
      return;
    }
    if(forbidden.test(this.username)){
      this.usernameErrorMessage = "' \" < > characters are forbidden in usernames";
      return;
    }
  }


  signup() {
    this.modal();
    this.emailErrorMessage="";
    this.usernameErrorMessage="";
    this.passwordErrorMessage = [''];
    if(!this.terms){
      superToast({
        message: "Dont forget to accept terms & conditions !",
        type: "is-link",
        dismissible: true,
        animate: { in: 'fadeIn', out: 'fadeOut' }
      });
      return;
    }
    if(this.username == "" || this.email == "" || this.password == ""){
      superToast({
        message: "Did you forget to fill something ?",
        type: "is-link",
        dismissible: true,
        animate: { in: 'fadeIn', out: 'fadeOut' }
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
      this.crypto.encrypt(ZKEkey, key, randomSalt).then((encryptedZKEkey) => {
        this.signupRequest(encryptedZKEkey, randomSalt);
      });
    });   
  }

  signupRequest(encryptedZKEkey:string, randomSalt:string){
    const data = {
      username: this.username,
      email: this.email,
      password: this.password,
      ZKE_key: encryptedZKEkey,
      salt: randomSalt
    };

    this.http.post(ApiService.API_URL+"/signup", data, {observe: 'response'}).subscribe((response) => {
      console.log(response);
      this.isLoading=false;
      superToast({
        message: "Account created successfully. You can now log in",
        type: "is-success",
        dismissible: true,
        animate: { in: 'fadeIn', out: 'fadeOut' }
      });
      this.router.navigate(["/login"], {relativeTo:this.route.root});

    },
    (error) => {
      console.log(error);
      this.isLoading=false;
      if(error.error.message == undefined){
        error.error.message = "Something went wrong. Please try again later";
      }
      superToast({
        message: "Error : "+ error.error.message,
        type: "is-danger",
        dismissible: true,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    });
  }

  modal(){
    this.isModalActive = !this.isModalActive;
  }
}
