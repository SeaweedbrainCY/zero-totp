import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ApiService } from '../common/ApiService/api-service';
import { faCircleNotch, faGear, faExclamationTriangle } from '@fortawesome/free-solid-svg-icons';
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
  faExclamationTriangle = faExclamationTriangle;
  isChallengeLoading = false;
  string_challenge: undefined | string = "";
  user_token = "";
  admin_cookie_expiration_s = 600;
  timer = this.admin_cookie_expiration_s;
  interval: any;
  isDeletionModalActive= false;
  deleteAccountConfirmationCountdown=5;
  buttonLoading = {"deletion": false}
  userToDelete: any;
  userToBlock:any;
  
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

  start_10m_timer(){
    this.interval = setInterval(() => {
      this.timer --;
      if(this.timer <= 0){
        this.timer = this.admin_cookie_expiration_s;
        this.isChallengeSolved = false;
        clearInterval(this.interval);
      }
    }, 1000);
  }


  solve_challenge(){
      const data = {
        token: this.user_token,
      }
        this.http.post(ApiService.API_URL+"/admin/login",  data, {withCredentials: true, observe: 'response'}).subscribe((response) => {
          if (response.status == 200){
            this.isChallengeSolved = true;
            this.start_10m_timer();
            this.getUsers();
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
  }


  deletionModal(){
    if(!this.buttonLoading["deletion"]){
      this.deleteAccountConfirmationCountdown = 5;
      if(!this.isDeletionModalActive){
        this.startTimer();
      } else {
        this.pauseTimer();
      }
      this.isDeletionModalActive = !this.isDeletionModalActive;
    }
  }

  startTimer() {
    this.deleteAccountConfirmationCountdown = 5;
    this.interval = setInterval(() => {
      if(this.deleteAccountConfirmationCountdown > 0) {
        this.deleteAccountConfirmationCountdown--;
      } else {
        clearInterval(this.interval);
      }
    },1000)
  }

  pauseTimer() {
    clearInterval(this.interval);
  }

  deleteAccount(){
    this.http.delete(ApiService.API_URL+"/admin/account/"+this.userToDelete.id,  {withCredentials:true, observe: 'response'}).subscribe((response) => {
      this.isDeletionModalActive = false;
      this.getUsers();
      superToast({
        message: "User deleted",
        type: "is-success",
        dismissible: false,
        duration: 20000,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    }, (error) => {
      let errorMessage = "";
      if(error.error.message != null){
        errorMessage = error.error.message;
      } else if(error.error.detail != null){
        errorMessage = error.error.detail;
      }
      superToast({
        message: "Impossible to delete user. "+ errorMessage,
        type: "is-danger",
        dismissible: false,
        duration: 20000,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    });
  }

  blockAccount(){
    this.http.put(ApiService.API_URL+"/admin/account/"+this.userToBlock.id+"/block", {}, {withCredentials:true, observe: 'response'}).subscribe((response) => {
      this.getUsers();
      superToast({
        message: "User blocked",
        type: "is-success",
        dismissible: false,
        duration: 20000,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    }, (error) => {
      let errorMessage = "";
      if(error.error.message != null){
        errorMessage = error.error.message;
      } else if(error.error.detail != null){
        errorMessage = error.error.detail;
      }
      superToast({
        message: "Impossible to block user. "+ errorMessage,
        type: "is-danger",
        dismissible: false,
        duration: 20000,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    });
  }

  unblockAccount(){
    this.http.put(ApiService.API_URL+"/admin/account/"+this.userToBlock.id+"/unblock", {}, {withCredentials:true, observe: 'response'}).subscribe((response) => {
      this.getUsers();
      superToast({
        message: "User unblocked",
        type: "is-success",
        dismissible: false,
        duration: 20000,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    }, (error) => {
      let errorMessage = "";
      if(error.error.message != null){
        errorMessage = error.error.message;
      } else if(error.error.detail != null){
        errorMessage = error.error.detail;
      }
      superToast({
        message: "Impossible to unblock user. "+ errorMessage,
        type: "is-danger",
        dismissible: false,
        duration: 20000,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    });
  }
}
