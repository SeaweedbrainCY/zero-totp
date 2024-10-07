import { Component, OnInit } from '@angular/core';
import { faEnvelope, faLock,  faCheck, faUser, faCog, faShield, faHourglassStart, faCircleInfo, faArrowsRotate, faFlask, faCircleNotch, faCircleExclamation, faLightbulb, faVault, faSliders, faShieldHalved } from '@fortawesome/free-solid-svg-icons';
import { UserService } from '../common/User/user.service';
import { HttpClient } from '@angular/common/http';

import { Utils } from '../common/Utils/utils';
import { ActivatedRoute, Router } from '@angular/router';
import { Crypto } from '../common/Crypto/crypto';
import { TranslateService } from '@ngx-translate/core';
import { ToastrService } from 'ngx-toastr';

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
  faVault=faVault;
  faArrowsRotate=faArrowsRotate;
  faShieldHalved=faShieldHalved;
  faSliders=faSliders;
  faHourglassStart=faHourglassStart;
  faCircleNotch=faCircleNotch;
  faCircleExclamation=faCircleExclamation;
  faLightbulb=faLightbulb;
  faCheck=faCheck;
  faCog=faCog;
  faFlask=faFlask;
  buttonLoading  ={"favicon_policy":false}
  moreHelpDisplayed = {"favicon_settings":false}
  isDisplayingAdvancedSettings = false;
  faviconPolicy=""; // never, always, enabledOnly
  loadingPreferences =true;
  loadingPreferencesError = false;
  notification_message :string|undefined;
  autolock_delay=10;
  autolock_display_error=false;
  autolock_is_updating = false;
  autolock_update_done_animation = false;
  autolock_value_updated = false;
  constructor( 
    private http: HttpClient,
    public userService: UserService,
    private utils: Utils,
    private router: Router,
    private route: ActivatedRoute,
    private crypto:Crypto,
    private translate: TranslateService,
    private toastr: ToastrService,
    ){
    }

  
  ngOnInit(): void {
     if(this.userService.getId() == null){
     this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
    } 
    this.get_preferences()
    this.get_internal_notification()
  }

  get_preferences(){
    this.http.get("/api/v1/preferences?fields=all", {withCredentials: true, observe: 'response'}).subscribe((response) => {
      if(response.body != null){
        this.loadingPreferences = false;
        const data = JSON.parse(JSON.stringify(response.body));
        if(data.autolock_delay != null){
          this.autolock_delay = data.autolock_delay;
        } else {
          this.autolock_delay = 10;
        }
        if(data.favicon_policy != null){
          this.faviconPolicy = data.favicon_policy;
        } else {
          this.loadingPreferencesError = true;
          this.faviconPolicy = "enabledOnly";
          this.translate.get('preference.error.fetch').subscribe((translation: string) => {
          this.utils.toastError(this.toastr,translation,"")
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
            errorMessage = "vault.error.server_unreachable"
          } else if (error.status == 401){
            this.userService.clear();
            this.router.navigate(["/login/sessionEnd"], {relativeTo:this.route.root});
            return;
          }
          this.translate.get('preference.error.update').subscribe((translation: string) => {
            this.utils.toastError(this.toastr, translation + " " + this.translate.instant(errorMessage),"");
        });
    });
  }


  changeFaviconSettings(policy: string){
    if(policy == "never" || policy == "always" || policy == "enabledOnly"){
      this.buttonLoading.favicon_policy = true;
      const data = {"id" : "favicon_policy", "value" :policy}
      this.http.put("/api/v1/preferences",  data, {withCredentials: true, observe: 'response'}).subscribe((response) => {
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
            errorMessage = "vault.error.server_unreachable"
          } else if (error.status == 401){
            this.userService.clear();
            this.router.navigate(["/login/sessionEnd"], {relativeTo:this.route.root});
            return;
          }

          this.translate.get('preference.error.update').subscribe((translation: string) => {
            this.utils.toastError(this.toastr, translation + " " + this.translate.instant(errorMessage),"");
          });
    });
  }
  }


  displayAdvancedSettings(){
    this.isDisplayingAdvancedSettings = true;
  }

  get_internal_notification(){
    this.http.get("/api/v1/notification/internal",  {withCredentials:true, observe: 'response'}).subscribe((response) => {
      if(response.status == 200){
        try{
          const data = JSON.parse(JSON.stringify(response.body))
          if (data.display_notification){
            this.notification_message = data.message;
          }
        } catch (error){
          console.log(error);
        }
      }
    }, (error) => {
      console.log(error);
    });
  }

  autolockDelayChange(){
    if(this.autolock_delay < 1){
      this.autolock_delay = 1;
      this.autolock_display_error = true;
    } else if(this.autolock_delay > 60){
      this.autolock_delay = 60;
      this.autolock_display_error = true;
    } else {
      this.autolock_display_error = false;
    }
  }

  autolockDelayUpdate(){
    this.autolock_is_updating = true;
    this.http.put("/api/v1/preferences", {"id":"autolock_delay", "value":this.autolock_delay}, {withCredentials: true, observe: 'response'}).subscribe((response) => {
      this.autolock_value_updated = true;
      this.autolockDelayUpdateDone();
    }, (error) => {
      this.autolock_is_updating = false;
      let errorMessage = "";
          if(error.error.message != null){
            errorMessage = error.error.message;
          } else if(error.error.detail != null){
            errorMessage = error.error.detail;
          }
          if(error.status == 0){
            errorMessage = "vault.error.server_unreachable"
          } else if (error.status == 401){
            this.userService.clear();
            this.router.navigate(["/login/sessionEnd"], {relativeTo:this.route.root});
            return;
          }
          this.translate.get('preference.error.update').subscribe((translation: string) => {
            this.utils.toastError(this.toastr, translation + " " + this.translate.instant(errorMessage),"");
          });
    });
  }

  autolockDelayUpdateDone(){
    this.autolock_is_updating = false
    this.autolock_update_done_animation = true;
    setTimeout(() => {
      this.autolock_update_done_animation = false;
    }, 1000);
  }

  input_auto_compute_size(value:any){
    let size = 5;
    if(value != null){
      size += value.toString().length;
    }
    return size;
  }

}
