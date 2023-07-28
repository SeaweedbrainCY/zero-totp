import { Component, OnInit } from '@angular/core';
import { toast as superToast } from 'bulma-toast'
import { faEnvelope, faLock,  faCheck, faUser} from '@fortawesome/free-solid-svg-icons';
import { UserService } from '../common/User/user.service';
import { HttpClient } from '@angular/common/http';
import { ApiService } from '../common/ApiService/api-service';
import { Utils } from '../common/Utils/utils';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-account',
  templateUrl: './account.component.html',
  styleUrls: ['./account.component.css']
})
export class AccountComponent implements OnInit {
  faUser=faUser;
  faEnvelope=faEnvelope;
  faLock=faLock;
  faCheck=faCheck;
  isDestroying=false;
  isModalActive=false;
  isLoading=false;
  username:string="";
  usernameErrorMessage="";
  email:string="";
  confirmEmail:string="";
  emailErrorMessage="";
  emailConfirmErrorMessage="";
  newPassword="";
  confirmNewPassword="";
  newPasswordErrorMessage : [string]=[""];
  newPasswordConfirmErrorMessage : [string]=[""];
  constructor(
    private http: HttpClient,
    private userService: UserService,
    private utils: Utils,
    private router: Router,
    private route: ActivatedRoute,
    ){}

  
  ngOnInit(): void {
    // if(this.userService.getId() == null){
    //   this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
    // } else {
    // }
  }



  checkUsername(){
  this.usernameErrorMessage = "";
  if(this.username != this.utils.sanitize(this.username)){
    this.usernameErrorMessage = "&, <, >, \" and ' are forbidden";
    superToast({
      message: "Special characters are forbidden",
      type: "is-danger",
      dismissible: true,
      animate: { in: 'fadeIn', out: 'fadeOut' }
    });
      return;
    }
  }

  changeUsername(){
    //TO DO
  }

  checkEmail(){
    this.emailErrorMessage = "";
    this.emailConfirmErrorMessage="";
    const emailRegex = /\S+@\S+\.\S+/;
    if(!emailRegex.test(this.email)){
      this.emailErrorMessage = "Are your sure about your email ?";
      return;
    } if(this.email != this.utils.sanitize(this.email)) {
      this.emailErrorMessage = "&, <, >, \" and ' are forbidden";
      return;
    } if(this.email != "" && this.confirmEmail != "" && this.email != this.confirmEmail) {
      this.emailConfirmErrorMessage = "Your emails do not match !";
      return;
    } else {
      return true;
    }
  }

  changeEmail(){
    if(this.email == ""){
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
    const data = {
      email: this.email
    }
    this.http.post(ApiService.API_URL+"/?",  data, {withCredentials: true, observe: 'response'}).subscribe((response) => {
      superToast({
        message: "Welcome back",
        type: "is-success",
        dismissible: true,
        animate: { in: 'fadeIn', out: 'fadeOut' }
      });
      //TO FINISH
    });
  }


  checkNewPassword(){
    this.newPasswordErrorMessage=[""];
    this.newPasswordConfirmErrorMessage=[""];
    const special = /[`!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?~]/;
    const upper = /[A-Z]/;
    const number = /[0-9]/;
    if(this.newPassword.length < 8){
      this.newPasswordErrorMessage.push("Your password must be at least 8 characters long");
    }
    else if(this.newPassword.length > 70){
      this.newPasswordErrorMessage.push("Password must be less than 70 characters long");
    }
    if(!special.test(this.newPassword)){
      this.newPasswordErrorMessage.push("Your password must contain at least one special character");
    }
    if(!upper.test(this.newPassword)){
      this.newPasswordErrorMessage.push("Your password must contain at least one uppercase character");
    }
    if(!number.test(this.newPassword)){
      this.newPasswordErrorMessage.push("Your password must contain at least one number");
    }
    if(this.newPassword != "" && this.confirmNewPassword != "" && this.newPassword != this.confirmNewPassword){
      this.newPasswordConfirmErrorMessage.push("Your passwords do not match");
    }
  }


  deleteAccount(){
    this.isDestroying = true;
  }

  modal(){
    if(!this.isDestroying){
      this.isModalActive = !this.isModalActive;
    }
  }

}


