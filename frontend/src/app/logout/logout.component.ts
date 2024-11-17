import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { UserService } from '../common/User/user.service';
import { HttpClient } from '@angular/common/http';
import {faCircleNotch} from '@fortawesome/free-solid-svg-icons';


@Component({
  selector: 'app-logout',
  templateUrl: './logout.component.html',
  styleUrls: ['./logout.component.css']
})
export class LogoutComponent implements OnInit{
  faCircleNotch = faCircleNotch;

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private userService: UserService,
    private http: HttpClient
    ) { }

  ngOnInit(): void {
    this.loggout();
  }

  loggout(){
    this.http.put('/api/v1/logout', {},{withCredentials: true, observe: 'response'}).subscribe({
      next: (response) => {
        this.userService.clear();
        this.router.navigate(["/login"], {relativeTo:this.route.root});
      },
      error: (error) => {
        this.userService.clear();
        this.router.navigate(["/login"], {relativeTo:this.route.root});
      }
    });
    }
}
