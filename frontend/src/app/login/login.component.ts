import { Component } from '@angular/core';
import { toast as superToast } from 'bulma-toast'
import { faEnvelope, faLock,  faCheck, faXmark, faFlagCheckered } from '@fortawesome/free-solid-svg-icons';
import { HttpClient } from '@angular/common/http';
import { ApiService } from '../common/ApiService/api-service';
import { Router, ActivatedRoute } from '@angular/router';
import { UserService } from '../common/User/user.service';
import {Crypto} from '../common/Crypto/crypto';

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

  constructor(
    private http: HttpClient,
    private router: Router,
    private route: ActivatedRoute,
    private userService: UserService
    ) {}


  deriveKeyAndNavigate(){
    const crypto = new Crypto();
    if(this.userService.derivedKeySalt != null){
      crypto.deriveKey(this.userService.derivedKeySalt, this.password).then(key=>{
        this.userService.key = key;
        this.router.navigate(["../vault"], {relativeTo:this.route});
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
    const data = {
      email: this.email,
      password: this.password
    }
    this.http.post(ApiService.API_URL+"/login", data, {observe: 'response'}).subscribe((response) => {
      
     
      superToast({
        message: "Welcome back",
        type: "is-success",
        dismissible: true,
        animate: { in: 'fadeIn', out: 'fadeOut' }
      });
      try{
        const data = JSON.parse(JSON.stringify(response.body))
        this.userService.id = data.id;
        this.userService.username = data.username;
        this.userService.derivedKeySalt = data.derivedKeySalt;
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
