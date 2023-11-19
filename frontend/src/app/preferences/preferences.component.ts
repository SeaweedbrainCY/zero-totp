import { Component, OnInit } from '@angular/core';
import { toast as superToast } from 'bulma-toast'
import { faEnvelope, faLock,  faCheck, faUser, faCog, faShield, faHourglassStart, faCircleInfo, faArrowsRotate, faFlask, faCircleNotch, faCircleExclamation } from '@fortawesome/free-solid-svg-icons';
import { UserService } from '../common/User/user.service';
import { HttpClient } from '@angular/common/http';
import { ApiService } from '../common/ApiService/api-service';
import { Utils } from '../common/Utils/utils';
import { ActivatedRoute, Router } from '@angular/router';
import { Crypto } from '../common/Crypto/crypto';
import { Buffer } from 'buffer';
import { json } from 'stream/consumers';

@Component({
  selector: 'app-preferences',
  templateUrl: './preferences.component.html',
  styleUrls: ['./preferences.component.css']
})
export class PreferencesComponent implements OnInit{
  faUser=faUser;
  faEnvelope=faEnvelope;
  faLock=faLock;
  faShield=faShield;
  faCircleInfo=faCircleInfo;
  faArrowsRotate=faArrowsRotate;
  faHourglassStart=faHourglassStart;
  faCircleNotch=faCircleNotch;
  faCircleExclamation=faCircleExclamation;
  faCheck=faCheck;
  faCog=faCog;
  faFlask=faFlask;
  buttonLoading  ={"favicon_policy":false}
  moreHelpDisplayed = {"favicon_settings":false}
  isDisplayingAdvancedSettings = false;
  faviconPolicy=""; // never, always, enabledOnly
  loadingPreferences = true;
  loadingPreferencesError = false;
  constructor( 
    private http: HttpClient,
    public userService: UserService,
    private utils: Utils,
    private router: Router,
    private route: ActivatedRoute,
    private crypto:Crypto
    ){}

  
  ngOnInit(): void {
     if(this.userService.getId() == null){
      this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
    } 
    this.get_preferences()
  }

  get_preferences(){
    this.http.get(ApiService.API_URL+"/preferences?fields=all", {withCredentials: true, observe: 'response'}).subscribe((response) => {
      if(response.body != null){
        this.loadingPreferences = false;
        const data = JSON.parse(JSON.stringify(response.body));
        if(data.favicon_policy != null){
          this.faviconPolicy = data.favicon_policy;
        } else {
          this.loadingPreferencesError = true;
          this.faviconPolicy = "enabledOnly";
          superToast({
            message: "An error occured while retrieving your preferences",
            type: "is-danger",
            dismissible: false,
            duration: 20000,
          animate: { in: 'fadeIn', out: 'fadeOut' }
          });
        }
      }
    }, (error) => {
      this.loadingPreferencesError = true;
      this.loadingPreferences = false;
        let errorMessage = "";
          if(error.error.message != null){
            errorMessage = error.error.message;
          } else if(error.error.detail != null){
            errorMessage = error.error.detail;
          }
          if(error.status == 0){
            errorMessage = "Server unreachable. Please check your internet connection or try again later. Do not reload this tab to avoid losing your session."
          } else if (error.status == 401){
            this.userService.clear();
            this.router.navigate(["/login/sessionEnd"], {relativeTo:this.route.root});
            return;
          }

          superToast({
            message: "Error : Impossible to update your preferences. "+ errorMessage,
            type: "is-danger",
            dismissible: false,
            duration: 20000,
          animate: { in: 'fadeIn', out: 'fadeOut' }
          });
    });
  }

  changeFaviconSettings(policy: string){
    if(policy == "never" || policy == "always" || policy == "enabledOnly"){
      this.buttonLoading.favicon_policy = true;
      const data = {"id" : "favicon_policy", "value" :policy}
      this.http.put(ApiService.API_URL+"/preferences",  data, {withCredentials: true, observe: 'response'}).subscribe((response) => {
        this.buttonLoading.favicon_policy = false;
        this.faviconPolicy = policy;

    }, (error) => {
      this.buttonLoading.favicon_policy = false;
      let errorMessage = "";
          if(error.error.message != null){
            errorMessage = error.error.message;
          } else if(error.error.detail != null){
            errorMessage = error.error.detail;
          }
          if(error.status == 0){
            errorMessage = "Server unreachable. Please check your internet connection or try again later. Do not reload this tab to avoid losing your session."
          } else if (error.status == 401){
            this.userService.clear();
            this.router.navigate(["/login/sessionEnd"], {relativeTo:this.route.root});
            return;
          }

          superToast({
            message: "Error : Impossible to update your preferences. "+ errorMessage,
            type: "is-danger",
            dismissible: false,
            duration: 20000,
          animate: { in: 'fadeIn', out: 'fadeOut' }
          });
    });
  }
  }


  displayAdvancedSettings(){
    this.isDisplayingAdvancedSettings = true;
  }
}
