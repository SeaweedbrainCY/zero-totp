import { Component, OnInit } from '@angular/core';
import { faPaperPlane, faArrowRotateLeft, faPen, faEye, faEyeSlash } from '@fortawesome/free-solid-svg-icons';
import { UserService } from '../common/User/user.service';
import { HttpClient } from '@angular/common/http';
import { Router, ActivatedRoute } from '@angular/router';

import { TranslateService } from '@ngx-translate/core';
import { Utils } from '../common/Utils/utils';
import { ToastrService } from 'ngx-toastr';

@Component({
    selector: 'app-email-verification',
    templateUrl: './email-verification.component.html',
    styleUrls: ['./email-verification.component.css'],
    standalone: false
})
export class EmailVerificationComponent implements OnInit {
  faPaperPlane = faPaperPlane;
  faArrowRotateLeft = faArrowRotateLeft;
  faPen = faPen;
  emailAddress: string | null = null;
  code = "";
  errorMessage = "";
  emailErrorMessage="";
  verifyLoading = false;
  emailAddressUpdated="";
  isEmailModalActive=false;
  emailLoading  = false;
  left_attempts = "";
  constructor(
    private userService: UserService,
    private http: HttpClient,
    private router: Router,
    private route: ActivatedRoute,
    private translate: TranslateService,
    private utils: Utils,
    private toastr: ToastrService
  ) { 
    this.emailAddress = this.userService.getEmail();
    if (this.emailAddress == null) {
      this.translate.get("session_expired").subscribe((translation: string) => {
        this.toastr.error(translation)
        this.router.navigate(['/login'], { queryParams: { returnUrl: this.router.url } });
      });
    }
  }

  ngOnInit(): void {
    this.http.get("/api/v1/role", {withCredentials: true, observe: 'response'}).subscribe((response) => {
      try{
        const user  = JSON.parse(JSON.stringify(response.body));
        if(user.role != "not_verified"){
          if(this.userService.getEmail() == null){
            this.utils.toastError(this.toastr,this.translate.instant("email_verif.error.no_email") ,"");
            this.router.navigate(['/login'], { queryParams: { returnUrl: this.router.url } });
          } else {
            this.router.navigate(['/vault'], { queryParams: { returnUrl: this.router.url } });
          }
        }
        } catch {
          this.utils.toastError(this.toastr,this.translate.instant("email_verif.error.unknown") ,"");
          this.router.navigate(['/login'], { queryParams: { returnUrl: this.router.url } });
        }
    }, (error) => {
      this.utils.toastError(this.toastr,this.translate.instant("email_verif.error.unknown") ,"");
        this.router.navigate(['/login'], { queryParams: { returnUrl: this.router.url } });
    });
  }


  verify(){
    this.errorMessage = '';
    this.verifyLoading = true;
    const data = {
      "token": this.code
    }
    this.http.put("/api/v1/email/verify",  data, {withCredentials: true, observe: 'response'}).subscribe((response) => {
      if(response.status == 200){
        this.verifyLoading = false;
        this.utils.toastSuccess(this.toastr, this.translate.instant("email_verif.verify.success") ,"");
        if(this.userService.getId() == null){
          this.router.navigate(['/login'], { queryParams: { returnUrl: this.router.url } });
        } else {
          this.router.navigate(['/vault'], { queryParams: { returnUrl: this.router.url } });
        }
       

      }
    }, (error) => {
      this.verifyLoading = false;
      if(error.status == 403){
        if(error.error.message != undefined){
          if(error.error.message == "email_verif.error.failed"){
            this.left_attempts = error.error.attempt_left;
            console.log(this.left_attempts)
          }
          this.errorMessage = error.error.message;
        } else {
          this.errorMessage = this.translate.instant("email_verif.error.generic");
        }
      } else {
        this.utils.toastError(this.toastr,this.translate.instant("email_verif.error.unknown") ,"");
      }
    });
  }

  resend(){
    this.verifyLoading = true;
    this.http.get("/api/v1/email/send_verification", {withCredentials: true, observe: 'response'}).subscribe((response) => {
      this.verifyLoading = false;
      this.utils.toastSuccess(this.toastr,this.translate.instant("email_verif.resend.success") ,"");
    }, (error) => {
      this.verifyLoading = false;
      if(error.status == 429){
        const ban_time = error.error.ban_time || "few";
        this.translate.get("email_verif.error.rate_limited",{time:String(ban_time)} ).subscribe((translation)=>{
          this.utils.toastError(this.toastr, translation,"");
      });
      } else {
        this.utils.toastError(this.toastr,this.translate.instant("email_verif.resend.error") ,"");
    }
    });
  }

  checkEmail(){
    const forbidden = /["\'<>]/
    this.emailErrorMessage = "";
    const emailRegex = /\S+@\S+\.\S+/;
    if(!emailRegex.test(this.emailAddressUpdated)){
      this.emailErrorMessage = "signup.email.error.invalid";
      return false;
    }
    if(forbidden.test(this.emailAddressUpdated)){
      this.emailErrorMessage = "signup.email.error.forbidden";
      return false;
    }
    return true;
  }

  updateEmail(){
    this.emailErrorMessage = "";
    const data = {
      "email": this.emailAddressUpdated
    }
      if(this.emailAddressUpdated == ""){
        this.emailErrorMessage ="signup.errors.missing_fields";
        return;
      }
      if(!this.checkEmail()){
        return;
      }
      this.emailLoading = true;
      this.http.put("/api/v1/update/email",  data, {withCredentials: true, observe: 'response'}).subscribe((response) => {
        this.emailLoading = false;
        this.translate.get("email_verif.popup.success").subscribe((translation:string) => {
          this.utils.toastSuccess(this.toastr,translation,"");
      });
        this.userService.setEmail(JSON.parse(JSON.stringify(response.body))["message"])
        this.emailAddress = this.userService.getEmail();
        this.isEmailModalActive=false;
        
      }, error =>{
        this.emailLoading = false;
        if(error.error.message == undefined){
          error.error.message = "email_verif.popup.error";
        }
        this.emailErrorMessage = error.error.message;
      });
    }

}

