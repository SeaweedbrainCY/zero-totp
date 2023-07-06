import { Component, OnInit } from '@angular/core';
import { faEnvelope, faLock,  faCheck, faUser, faXmark, faFlagCheckered } from '@fortawesome/free-solid-svg-icons';
import { HttpClient } from '@angular/common/http';
import { ApiService } from '../common/ApiService/api-service';
import { toast } from 'bulma-toast';
import { toast as superToast } from 'bulma-toast'
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
  terms=false;
  isLoading=false;
  declare bulmaToast : any;
  errors=[''];
  emailHasError = false;
  passwordHasError = false;

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
    return;
  }

  checkPassword(){
    this.passwordHasError = false;
    const special = /[`!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?~]/;
    const upper = /[A-Z]/;
    const number = /[0-9]/;
    if(this.password.length < 8){
      this.errors.push("Your password must be at least 8 characters long");
      this.passwordHasError = true;
    }
    else if(this.password.length > 70){
      this.errors.push("Password must be less than 70 characters long");
      this.passwordHasError = true;
    }
    if(!special.test(this.password)){
      this.errors.push("Your password must contain at least one special character");
      this.passwordHasError = true;
    }
    if(!upper.test(this.password)){
      this.errors.push("Your password must contain at least one uppercase character");
      this.passwordHasError = true;
    }
    if(!number.test(this.password)){
      this.errors.push("Your password must contain at least one number");
      this.passwordHasError = true;
    }
  }

  checkEmail(){
    this.emailHasError = false;
    const emailRegex = /\S+@\S+\.\S+/;
    if(!emailRegex.test(this.email)){
      this.errors.push("Your email is not valid");
      this.emailHasError = true;
    }
  }


  signup() {
    this.emailHasError = false;
    this.passwordHasError = false;
    this.errors = [''];
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
    if(this.emailHasError || this.passwordHasError){return;}
    

    this.isLoading=true;
    const data = {
      username: this.username,
      email: this.email,
      password: this.password
    };

    this.http.post(ApiService.API_URL+"/signup", data, {observe: 'response'}).subscribe((response) => {
      console.log(response);
      this.isLoading=false;
      superToast({
        message: "Account created successfully",
        type: "is-success",
        dismissible: true,
        animate: { in: 'fadeIn', out: 'fadeOut' }
      });
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
