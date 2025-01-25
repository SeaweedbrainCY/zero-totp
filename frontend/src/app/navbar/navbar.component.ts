import { Component, OnInit } from '@angular/core';
import { UserService } from '../common/User/user.service';
import { ActivatedRoute, Router, NavigationEnd } from '@angular/router';
import { TranslateService } from '@ngx-translate/core';
import { Idle, DEFAULT_INTERRUPTSOURCES } from '@ng-idle/core';
import { Subscription } from 'rxjs';
import { faLightbulb, faXmark, faVault, faKey, faGears, faUser} from '@fortawesome/free-solid-svg-icons';
import { faMoon, faSun } from '@fortawesome/free-regular-svg-icons';
import { HttpClient } from '@angular/common/http';



@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit{
  currentUrl:string = "";
  isNavbarExpanded = false;
  isIdleWatchingEnabled = false;
  faXmark=faXmark
  faUser=faUser;
  faSun=faSun;
  faKey=faKey;
  faGears=faGears;
  faMoon=faMoon;
  faVault=faVault;
  faLightbulb = faLightbulb;
  current_language:string = localStorage.getItem('language') || 'en-uk';
  isLangDropdownExpanded = false;
  idleEndSupscription: Subscription | null = null;
  notification_message :string|undefined;
  dismissed_notification_key = "hide_notif_banner";
  is_waiting_for_internal_notif = false
  last_notification_check_date = 0;
  current_theme =  window.document.documentElement.getAttribute('data-theme');
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
    private idle: Idle,
    private http: HttpClient
    ) { 
    router.events.subscribe((url:any) => {
      this.check_notification()
      if (url instanceof NavigationEnd){
      this.currentUrl = url.url;
      if(this.userService.getId() && !this.userService.getIsVaultLocal() && !this.idle.isRunning()){
        this.get_autolock_delay().subscribe((response) => {
          const data = JSON.parse(JSON.stringify(response.body))
          let autolock_delay = 600;
          if(data.autolock_delay != null){
            autolock_delay = data.autolock_delay*60;
          }
          this.idle.setInterrupts(DEFAULT_INTERRUPTSOURCES);
          this.idle.setIdle(autolock_delay);
          this.idle.setTimeout(20);
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
        }, (error) => {
          console.log(error);
        });
      }
    }
    translate.use(this.current_language)
  });
  }

  ngOnInit(): void {
    this.get_global_notification();
    this.last_notification_check_date = Math.floor(Date.now()/1000);
  }

  check_notification(){
    if(this.last_notification_check_date !=0){ // first notif not even been checked yet
      if(this.is_waiting_for_internal_notif && this.userService.getId() !=null){
        this.get_internal_notification()
        this.is_waiting_for_internal_notif = false
        this.last_notification_check_date = Math.floor(Date.now()/1000);
        console.info("auth and waiting")
      } else if (this.last_notification_check_date + 60*2 < Math.floor(Date.now()/1000)){
        console.info("check again")
        this.last_notification_check_date = Math.floor(Date.now()/1000);
        if (this.userService.getId() != null){
          this.get_internal_notification()
        } else {
          this.get_global_notification()
        }
      }
    } else {
      console.log("first check")
    }
  }
  get_global_notification(){
    this.http.get("/api/v1/notification/global",  {withCredentials:true, observe: 'response'}).subscribe((response) => {
      if(response.status == 200){
        try{
          const data = JSON.parse(JSON.stringify(response.body))
          if (data.display_notification){
            if (!data.authenticated_user_only){
              const already_dismissed_date = localStorage.getItem(this.dismissed_notification_key);
              if (already_dismissed_date){
                if(Number(already_dismissed_date) < data.timestamp){
                  this.notification_message = data.message;
                } 
              } else{ // not dismissed yet
                this.notification_message = data.message;
              }
            } else { // authenticated_user_only
              this.is_waiting_for_internal_notif = true
            }
          }
        } catch (error){
          console.log(error);
        }
      }
    }, (error) => {
      console.log(error);
    });
  }

  get_internal_notification(){
    this.http.get("/api/v1/notification/internal",  {withCredentials:true, observe: 'response'}).subscribe((response) => {
      if(response.status == 200){
        try{
          const data = JSON.parse(JSON.stringify(response.body))
          if (data.display_notification){
              const already_dismissed_date = localStorage.getItem(this.dismissed_notification_key);
              if (already_dismissed_date){
                if(Number(already_dismissed_date) < data.timestamp){
                  this.notification_message = data.message;
                } 
              } else{ // not dismissed yet
                this.notification_message = data.message;
              }
          }
        } catch (error){
          console.log(error);
        }
      }
    }, (error) => {
      console.log(error);
    });
  }

  get_autolock_delay(){
    return this.http.get("/api/v1/preferences?fields=autolock_delay",  {withCredentials:true, observe: 'response'})
  }

  hide_notification(){
    this.notification_message = undefined;
    localStorage.setItem(this.dismissed_notification_key, Math.floor(Date.now()/1000).toString()); // unix
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

  toggleThemeButton(){
    if(this.current_theme == 'light'){
      window.document.documentElement.setAttribute('data-theme', 'dark');
      this.current_theme = 'dark';
    } else {
      window.document.documentElement.setAttribute('data-theme', 'light');
      this.current_theme = 'light';
    }
  }



}
