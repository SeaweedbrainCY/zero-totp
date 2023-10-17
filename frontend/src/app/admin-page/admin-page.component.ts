import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ApiService } from '../common/ApiService/api-service';
import { faCircleNotch, faGear } from '@fortawesome/free-solid-svg-icons';
import { UserService } from '../common/User/user.service';
import { ActivatedRoute, Router } from '@angular/router';


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
  
    constructor(
      private http: HttpClient,
      private userService: UserService,
      private router: Router,
      private route: ActivatedRoute,
      ) { 
      this.users = [
        {"username": "foo", "email": "foo@gmail", "createdAt":"10-10-2023", "isDisabled":false},
        {"username": "barr", "email": "bar@gmail", "createdAt":"10-10-2023", "isDisabled":true},
      ]
    }
    
    ngOnInit(): void {
      if(this.userService.getId() == null){
        this.router.navigate(['/login'], { relativeTo: this.route });
      }
      this.fetch_role_and_users();
  } 

  getUsers(){
  }

  logoutUser(){
    this.userService.clear();
    setTimeout(() => {
      window.location.href = "/login";
    }, 5000);
  }

  fetch_role_and_users(){
    this.http.get(ApiService.API_URL+"/role",  {withCredentials:true, observe: 'response'}).subscribe((response) => {
      try{
        const user  = JSON.parse(JSON.stringify(response.body));
        if(user.role == "admin"){
          this.isAdmin= true;
          this.getUsers();
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
}
