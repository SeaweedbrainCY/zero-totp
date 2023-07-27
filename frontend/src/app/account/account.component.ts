import { Component, OnInit } from '@angular/core';
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 67bb593 (Start of angular functions + Start of API addition for account page requests)
import { toast as superToast } from 'bulma-toast'
import { faEnvelope, faLock,  faCheck, faUser} from '@fortawesome/free-solid-svg-icons';
import { UserService } from '../common/User/user.service';
import { HttpClient } from '@angular/common/http';
import { ApiService } from '../common/ApiService/api-service';
import { Utils } from '../common/Utils/utils';
<<<<<<< HEAD
=======
import { faEnvelope, faLock,  faCheck, faUser} from '@fortawesome/free-solid-svg-icons';
import { UserService } from '../common/User/user.service';
>>>>>>> 8004ceb (Front V1 desktop/mobile for account page)
=======
>>>>>>> 67bb593 (Start of angular functions + Start of API addition for account page requests)
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
<<<<<<< HEAD
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
=======
  isDestroying = false;
  isModalActive = false;
  isLoading=false;
  username:string="";
  email:string = "";
  confirmEmail:string = "";
>>>>>>> 67bb593 (Start of angular functions + Start of API addition for account page requests)
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
      return;
    }
  }

<<<<<<< HEAD
=======
  checkUsername() : boolean{
  if(this.username != this.utils.sanitize(this.username)){
      superToast({
        message: "&, <, >, \" and ' are forbidden",
        type: "is-danger",
        dismissible: true,
        animate: { in: 'fadeIn', out: 'fadeOut' }
      });
      return false;
    } else {
      return true;
    }
  }

>>>>>>> 67bb593 (Start of angular functions + Start of API addition for account page requests)
  changeUsername(){
    //TO DO
  }

<<<<<<< HEAD
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
=======
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
    } if(this.email != this.utils.sanitize(this.email)) {
      superToast({
        message: "&, <, >, \" and ' are forbidden",
        type: "is-danger",
        dismissible: true,
        animate: { in: 'fadeIn', out: 'fadeOut' }
      });
      return false;
    } if(this.email != this.confirmEmail) {
      superToast({
        message: "Your emails do not match !",
        type: "is-danger",
        dismissible: true,
        animate: { in: 'fadeIn', out: 'fadeOut' }
      });
      return false;
>>>>>>> 67bb593 (Start of angular functions + Start of API addition for account page requests)
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

<<<<<<< HEAD
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


=======
>>>>>>> 67bb593 (Start of angular functions + Start of API addition for account page requests)
  deleteAccount(){
    this.isDestroying = true;
  }

  modal(){
    if(!this.isDestroying){
      this.isModalActive = !this.isModalActive;
    }
  }

}


