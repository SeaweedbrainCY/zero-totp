import { Component } from '@angular/core';
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
export class EmailVerificationComponent {
  faPaperPlane = faPaperPlane;
  faArrowRotateLeft = faArrowRotateLeft;
  faPen = faPen;
  emailAddress: string | null = null;
  code = "";
  errorMessage = "";
  constructor(
    private userService: UserService,
    private http: HttpClient,
    private router: Router,
    private route: ActivatedRoute,
  ) { 
    this.emailAddress = this.userService.getEmail();
  }


  verify(){
    this.errorMessage = '';
    const data = {
      "token": this.code
    }
    this.http.put(ApiService.API_URL+"/email/verify",  data, {withCredentials: true, observe: 'response'}).subscribe((response) => {
      if(response.status == 200){
        superToast({
          message: "Your email is verified ! ✅",
          type: "is-success",
          dismissible: true,
        animate: { in: 'fadeIn', out: 'fadeOut' }
        });
        this.router.navigate(['/login']);
      }
    }, (error) => {
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

}
