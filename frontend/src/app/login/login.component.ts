import { Component } from '@angular/core';
import { toast as superToast } from 'bulma-toast'
import { faEnvelope, faLock,  faCheck, faXmark, faFlagCheckered } from '@fortawesome/free-solid-svg-icons';
import { HttpClient } from '@angular/common/http';
import { ApiService } from '../common/ApiService/api-service';

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
  email:string = "";
  password:string = "";
  isLoading = false;

  checkEmail() : boolean{
    const emailRegex = /\S+@\S+\.\S+/;
    if(!emailRegex.test(this.email)){
      superToast({
        message: "Are your sure about your email ? ",
        type: "is-primary",
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
        type: "is-primary",
        dismissible: true,
        animate: { in: 'fadeIn', out: 'fadeOut' }
      });
      return;
    }
    if(!this.checkEmail()){
      return;
    }
    this.isLoading = true;
  }
}
