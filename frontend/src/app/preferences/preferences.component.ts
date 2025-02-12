import { Component, OnInit } from '@angular/core';
import { faEnvelope, faLock,  faCheck, faUser, faCog, faShield, faHourglassStart, faCircleInfo, faArrowsRotate, faFlask, faCircleNotch, faCircleExclamation, faLightbulb, faVault, faSliders, faShieldHalved, faXmark } from '@fortawesome/free-solid-svg-icons';
import { faHardDrive } from '@fortawesome/free-regular-svg-icons';
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
    styleUrls: ['./preferences.component.css'],
    standalone: false
})
export class PreferencesComponent implements OnInit{
  faUser=faUser;
  faEnvelope=faEnvelope;
  faLock=faLock;
  faShield=faShield;
  faCircleInfo=faCircleInfo;
  faVault=faVault;
  faArrowsRotate=faArrowsRotate;
  faXmark=faXmark;
  faHardDrive=faHardDrive;
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
  autolock_update_failed_animation= false;
  autolock_value_updated = false;
  duration_unit = "";
  minimum_duration = -1;
  maximum_duration = -1;
  loading_backup_configuration = true;
  backup_max_age = -1;
  backup_minimum_count = -1;
  default_backup_max_age = -1;
  default_backup_minimum_count = -1;
  constructor( 
    private http: HttpClient,
    public userService: UserService,
    private utils: Utils,
    private router: Router,
    private route: ActivatedRoute,
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
    this.get_backup_configuration()
    this.duration_unit = "hour";
  }

  get_preferences(){
    this.http.get("/api/v1/preferences?fields=all", {withCredentials: true, observe: 'response'}).subscribe((response) => {
      if(response.body != null){
        this.loadingPreferences = false;
        const data = JSON.parse(JSON.stringify(response.body));
        if(data.autolock_delay != null){
          if(Math.floor(data.autolock_delay/60) == data.autolock_delay/60){
            this.autolock_delay = data.autolock_delay/60;
            this.duration_unit = "hour";
          } else {
            this.autolock_delay = data.autolock_delay;
            this.duration_unit = "minute";
          }
        } else {
          this.autolock_delay = 10;
          this.duration_unit = "minute";
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

  get_backup_configuration(){
    this.http.get("/api/v1/backup/configuration?dv=true",{withCredentials:true, observe: 'response'}).subscribe({
      next:(response) => {
        if(response.body != null){
          const data = JSON.parse(JSON.stringify(response.body));
          this.backup_max_age = data.max_age_in_days;
          this.backup_minimum_count = data.backup_minimum_count;
          this.default_backup_max_age = data.default_max_age_in_days;
          this.default_backup_minimum_count = data.default_backup_minimum_count;
          this.loading_backup_configuration = false;
        } else {
          this.loadingPreferencesError = true;
          this.loading_backup_configuration = false;
          this.translate.get('preference.error.fetch').subscribe((translation: string) => {
          this.utils.toastError(this.toastr,translation,"")
        });
        }
      },
      error: (error)=>{
        this.loadingPreferencesError = true;
       this.loading_backup_configuration = false;
          this.translate.get('preference.error.fetch').subscribe((translation: string) => {
          this.utils.toastError(this.toastr,translation,error.error.message)
          });
      }
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


  autolockDelayToMinutes(){
    if(this.duration_unit == "hour"){
      return this.autolock_delay * 60;
    } else {
      return this.autolock_delay;
    }
  }

  autolockDelayUpdate(){
    this.autolock_display_error = false;
    this.autolock_value_updated = false;
    this.autolock_is_updating = true;
    const autolock_delay_minutes = this.autolockDelayToMinutes();
    this.http.put("/api/v1/preferences", {"id":"autolock_delay", "value":autolock_delay_minutes}, {withCredentials: true, observe: 'response'}).subscribe((response) => {
      this.autolock_value_updated = true;
      this.autolockDelayUpdateDone();
    }, (error) => {
      this.autolock_is_updating = false;
      if(error.status == 400){
        if(error.error.message == "invalid_duration"){
          this.autolock_display_error = true;
          this.autolockDelayUpdateFailed()
          this.minimum_duration = error.error.minimum_duration_min;
          this.maximum_duration = error.error.maximum_duration_min/60;
          return;
        }
      }
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

  autolockDelayUpdateFailed(){
    this.autolock_is_updating = false
    this.autolock_update_failed_animation = true;
    setTimeout(() => {
      this.autolock_update_failed_animation = false;
    }, 1000);
  }

  input_auto_compute_size(value:any){
    let size = 5;
    if(value != null){
      size += value.toString().length;
    }
    return size;
  }

  change_duration_unit(value:string){
    if(value == "minute"){
      this.duration_unit = "minute";
    } else  if(value == "hour"){
      this.duration_unit = "hour";
    } 
  }

}
