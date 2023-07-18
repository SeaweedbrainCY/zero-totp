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
  navbarActive = false;
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

  navigateToRoute(route:string){
    this.router.navigate([route], {relativeTo:this.route.root});
  }

  navbarBurger(){
    this.navbarActive = !this.navbarActive;
  }


}
