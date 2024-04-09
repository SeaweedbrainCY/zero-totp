import { Component, OnInit } from '@angular/core';
import { UserService } from '../common/User/user.service';
import { ActivatedRoute, Router, NavigationEnd } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';
import { Idle, DEFAULT_INTERRUPTSOURCES } from '@ng-idle/core';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit{
  currentUrl:string = "";
  isNavbarExpanded = false;
  isIdleWatchingEnabled = false;
  current_language:string = localStorage.getItem('language') || 'en-uk';
  isLangDropdownExpanded = false;
  idleEndSupscription: Subscription | null = null;
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
    public translate: TranslateService,
    private idle: Idle
    ) { 
    router.events.subscribe((url:any) => {
      if (url instanceof NavigationEnd){
      this.currentUrl = url.url;
      console.log(this.idle.isRunning())
    /* if(this.idleEndSupscription){
        this.idleEndSupscription.unsubscribe();
        console.log("unsubscribed")
      }*/
      

      if(this.userService.getId() && !this.userService.getIsVaultLocal() && !this.idle.isRunning()){
        this.idle.setInterrupts(DEFAULT_INTERRUPTSOURCES);
        this.idle.setIdle(6);
        this.idle.setTimeout(10);
        this.idleEndSupscription = this.idle.onIdleEnd.subscribe(() => {
          console.log("Idle end " +  this.currentUrl )
        });
        this.idle.onIdleStart.subscribe(() => {
          console.log("Idle start " +  this.currentUrl )
        });
        this.idle.onTimeout.subscribe(() => {
          // As idle.stop() doesn't work (issue #167, we need to check if the user is still logged in before redirecting to the login page)
          if(this.userService.getId() && !this.userService.getIsVaultLocal()){ 
            console.log("Idle timeout " +  this.currentUrl )
            this.userService.clear();
            this.router.navigate(['/login/sessionTimeout'], {relativeTo:this.route.root});
          }
        });
        if(!this.idle.isRunning()){
          this.idle.watch();
        }
        console.log("wathching for idle")
      }
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
