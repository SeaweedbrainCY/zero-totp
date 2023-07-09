import { Component, OnInit } from '@angular/core';
import { UserService } from '../common/User/user.service';
import { ActivatedRoute, Router, NavigationEnd } from '@angular/router';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit{
  currentUrl:string = "";
  constructor(
    public userService:UserService,
    private router : Router,
    private route : ActivatedRoute
    ) { 
   
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
