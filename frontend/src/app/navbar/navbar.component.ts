import { Component, OnInit } from '@angular/core';
import {User} from '../common/User/user';
import { UserService } from '../common/User/user.service';
import { ActivatedRoute, Router, NavigationEnd } from '@angular/router';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit{
  user:User;
  currentUrl:string = "";
  constructor(
    private userService:UserService,
    private router : Router,
    private route : ActivatedRoute
    ) { 
    this.user = userService.getUser();
    router.events.subscribe((url:any) => {
      if (url instanceof NavigationEnd){
      this.currentUrl = url.url;
    }
  }
     
      );
    
  }

  ngOnInit(): void {
   
  }


}
