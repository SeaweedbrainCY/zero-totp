import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ApiService } from '../common/ApiService/api-service';
import { faCircleNotch, faGear } from '@fortawesome/free-solid-svg-icons';
import { UserService } from '../common/User/user.service';
import { ActivatedRoute, Router } from '@angular/router';
import { toast as superToast } from 'bulma-toast'
import { Crypto } from '../common/Crypto/crypto';

@Component({
  selector: 'app-admin-page',
  templateUrl: './admin-page.component.html',
  styleUrls: ['./admin-page.component.css']
})
export class AdminPageComponent implements OnInit {
  users: any = []
  isAdmin: boolean|undefined = undefined;
  faCircleNotch = faCircleNotch;
  faGear = faGear;
  isChallengeSolved: boolean = false;
  isChallengeLoading = false;
  string_challenge: undefined | string = "";
  private_key_b64 = "";
  
    constructor(
      private http: HttpClient,
      private userService: UserService,
      private router: Router,
      private route: ActivatedRoute,
      private crypto: Crypto
      ) { 
    }
    
    ngOnInit(): void {
      if(this.userService.getId() == null){
        this.router.navigate(['/login'], { relativeTo: this.route });
      }
      this.fetch_role_and_challenge();
  } 

  getUsers(){
    this.http.get(ApiService.API_URL+"/admin/users",  {withCredentials:true, observe: 'response'}).subscribe((response) => {
      try{
        const body  = JSON.parse(JSON.stringify(response.body));
        this.users = body.users;

      } catch (e) {
        superToast({
          message: "Impossible to fetch users. "+ e,
          type: "is-danger",
          dismissible: false,
          duration: 20000,
        animate: { in: 'fadeIn', out: 'fadeOut' }
        });
      }
    }, (error) => {
      let errorMessage = "";
      if(error.error.message != null){
        errorMessage = error.error.message;
      } else if(error.error.detail != null){
        errorMessage = error.error.detail;
      }
      superToast({
        message: "Impossible to fetch users. "+ errorMessage,
        type: "is-danger",
        dismissible: false,
        duration: 20000,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    });
  }

  logoutUser(){
    this.userService.clear();
    setTimeout(() => {
      window.location.href = "/login";
    }, 5000);
  }

  fetch_role_and_challenge(){
    this.http.get(ApiService.API_URL+"/role",  {withCredentials:true, observe: 'response'}).subscribe((response) => {
      try{
        const user  = JSON.parse(JSON.stringify(response.body));
        if(user.role == "admin"){
          this.isAdmin= true;
          this.get_admin_challenge();
        } else {
          this.isAdmin= false;
          this.logoutUser();
        }
      } catch (e) {
        this.isAdmin= false;
        this.logoutUser();
      }
    }, (_) => {
      this.isAdmin= false;
      this.logoutUser();
    });
  }

  get_admin_challenge(){
    this.http.get(ApiService.API_URL+"/admin/challenge/generate",  {withCredentials:true, observe: 'response'}).subscribe((response) => {
      try{
        const body  = JSON.parse(JSON.stringify(response.body));
        this.string_challenge = body.challenge;
      } catch (e) {
        superToast({
          message: "Impossible to fetch the admin  challenge. "+ e,
          type: "is-danger",
          dismissible: false,
          duration: 20000,
        animate: { in: 'fadeIn', out: 'fadeOut' }
        });
      }
    }, (error) => {
      let errorMessage = "";
      if(error.error.message != null){
        errorMessage = error.error.message;
      } else if(error.error.detail != null){
        errorMessage = error.error.detail;
      }
      superToast({
        message: "Impossible to fetch the admin  challenge. "+ errorMessage,
        type: "is-danger",
        dismissible: false,
        duration: 20000,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    });
  }

  solve_challenge(){
    this.crypto.sign_rsa(this.string_challenge!, this.private_key_b64).then((signature) => {
      const data = {
        challenge: this.string_challenge,
        signature: signature
      }
        this.http.post(ApiService.API_URL+"/admin/challenge/verify",  data, {withCredentials: true, observe: 'response'}).subscribe((response) => {
          if (response.status == 200){
            console.log("ok")
          }
        }, (error) => {
          let errorMessage = "";
          if(error.error.message != null){
            errorMessage = error.error.message;
          } else if(error.error.detail != null){
            errorMessage = error.error.detail;
          }
          superToast({
            message: "Challenge failed. "+ errorMessage,
            type: "is-danger",
            dismissible: false,
            duration: 20000,
          animate: { in: 'fadeIn', out: 'fadeOut' }
          });
        });
    }).catch((error) => {
      superToast({
        message: "Impossible to sign the challenge. "+ error,
        type: "is-danger",
        dismissible: false,
        duration: 20000,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    });
  }
}
