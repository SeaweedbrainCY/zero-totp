import { Component, OnInit } from '@angular/core';
import { UserService } from '../common/User/user.service';
import { ActivatedRoute, Router, NavigationEnd } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit{
  currentUrl:string = "";
  isNavbarExpanded = false;
  current_language:string = localStorage.getItem('language') || 'en-uk';
  isLangDropdownExpanded = false;
  languages = [
    {
      name:"English", // default one
      code:"en-uk",
      image:"assets/united-kingdom.png"
    },
    {
      name:"Français",
      code:"fr-fr",
      image:"assets/france.png"
    }
  ]
  constructor(
    public userService:UserService,
    private router : Router,
    private route : ActivatedRoute,
    public translate: TranslateService
    ) { 
    router.events.subscribe((url:any) => {
      if (url instanceof NavigationEnd){
      this.currentUrl = url.url;
    }
    translate.use(this.current_language)
  });
    
  }

  ngOnInit(): void {
   
  }

  navigateToRoute(route:string){
    this.isNavbarExpanded = !this.isNavbarExpanded;
    window.document.getElementById('navbarBurger')?.click();
    this.router.navigate([route], {relativeTo:this.route.root});
  }

  changeLocation(url:string){
    window.document.getElementById('navbarBurger')?.click();
    window.location.href = url;
  }

  changeLanguage(language:string){
    this.isLangDropdownExpanded = false;
    if(language == 'fr-fr'){
      localStorage.setItem('language','fr-fr');
      this.current_language = 'fr-fr';
      this.translate.use('fr-fr');
    } else { // 'en-uk' + default
      localStorage.setItem('language','en-uk');
      this.current_language = 'en-uk';
      this.translate.use('en-uk');
    }
  }

  get_current_language_info(){
    for (let lang of this.languages){
      if(lang.code == this.current_language){
        return lang;
      }
    }
    return this.languages[0]; // en-uk
  }



}
