import { Component, OnInit } from '@angular/core';
import { faPaperPlane, faArrowRotateLeft, faPen } from '@fortawesome/free-solid-svg-icons';
import { UserService } from '../common/User/user.service';
import { HttpClient } from '@angular/common/http';
import { Router, ActivatedRoute } from '@angular/router';
import { ApiService } from '../common/ApiService/api-service';
import { toast as superToast } from 'bulma-toast'


@Component({
  selector: 'app-email-verification',
  templateUrl: './email-verification.component.html',
  styleUrls: ['./email-verification.component.css']
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
  constructor(
    private userService: UserService,
    private http: HttpClient,
    private router: Router,
    private route: ActivatedRoute,
  ) { 
    this.emailAddress = this.userService.getEmail();
    if (this.emailAddress == null) {
      this.router.navigate(['/login'], { queryParams: { returnUrl: this.router.url } });
    }
  }

  ngOnInit(): void {
    this.http.get(ApiService.API_URL+"/role", {withCredentials: true, observe: 'response'}).subscribe((response) => {
      try{
        const user  = JSON.parse(JSON.stringify(response.body));
        if(user.role != "not_verified"){
          if(this.userService.getId() == null){
            this.router.navigate(['/login'], { queryParams: { returnUrl: this.router.url } });
          } else {
            this.router.navigate(['/vault'], { queryParams: { returnUrl: this.router.url } });
          }
        }
        } catch {
          this.router.navigate(['/login'], { queryParams: { returnUrl: this.router.url } });
        }
    }, (error) => {
        this.router.navigate(['/login'], { queryParams: { returnUrl: this.router.url } });
    });
  }


  verify(){
    this.errorMessage = '';
    this.verifyLoading = true;
    const data = {
      "token": this.code
    }
    this.http.put(ApiService.API_URL+"/email/verify",  data, {withCredentials: true, observe: 'response'}).subscribe((response) => {
      if(response.status == 200){
        this.verifyLoading = false;
        superToast({
          message: "Your email is verified ! ✅",
          type: "is-success",
          dismissible: true,
        animate: { in: 'fadeIn', out: 'fadeOut' }
        });
        if(this.userService.getId() == null){
          this.router.navigate(['/login'], { queryParams: { returnUrl: this.router.url } });
        } else {
          this.router.navigate(['/vault'], { queryParams: { returnUrl: this.router.url } });
        }
       

      }
    }, (error) => {
      this.verifyLoading = false;
      if(error.status == 403){
        this.errorMessage = "Invalid or expired code";
      } else {
        superToast({
          message: "An error occured ! ❌",
          type: "is-danger",
          dismissible: true,
        animate: { in: 'fadeIn', out: 'fadeOut' }
        });
      }
    });
  }

  resend(){
    this.verifyLoading = true;
    this.http.get(ApiService.API_URL+"/email/send_verification", {withCredentials: true, observe: 'response'}).subscribe((response) => {
      this.verifyLoading = false;
        superToast({
          message: "Email sent ! ✅",
          type: "is-success",
          dismissible: true,
        animate: { in: 'fadeIn', out: 'fadeOut' }
        });
    }, (error) => {
      this.verifyLoading = false;
      superToast({
        message: "An error occured ! ❌",
        type: "is-danger",
        dismissible: true,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    });
  }

  checkEmail(){
    const forbidden = /["\'<>]/
    this.emailErrorMessage = "";
    const emailRegex = /\S+@\S+\.\S+/;
    if(!emailRegex.test(this.emailAddressUpdated)){
      this.emailErrorMessage = "Your email is not valid";
      return false;
    }
    if(forbidden.test(this.emailAddressUpdated)){
      this.emailErrorMessage = "' \" < > characters are forbidden in passwords";
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
        this.emailErrorMessage ="Did you forget to fill something ?";
        return;
      }
      if(!this.checkEmail()){
        return;
      }
      this.emailLoading = true;
      this.http.put(ApiService.API_URL+"/update/email",  data, {withCredentials: true, observe: 'response'}).subscribe((response) => {
        this.emailLoading = false;
        superToast({
          message: "Email updated with success. You should receive a verification email soon ! ✅",
          type: "is-success",
          dismissible: true,
          animate: { in: 'fadeIn', out: 'fadeOut' }
        });
        this.userService.setEmail(JSON.parse(JSON.stringify(response.body))["message"])
        this.emailAddress = this.userService.getEmail();
        this.isEmailModalActive=false;
        
      }, error =>{
        this.emailLoading = false;
        if(error.error.message == undefined){
          error.error.message = "Something went wrong. Please try again later";
        }
        this.emailErrorMessage = error.error.message;
      });
    }

}

