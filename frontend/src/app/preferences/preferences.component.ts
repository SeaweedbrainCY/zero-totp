import { Component, OnInit, signal, ChangeDetectionStrategy } from '@angular/core';
import { faEnvelope, faLock,  faCheck, faUser, faCog, faShield, faHourglassStart, faCircleInfo, faArrowsRotate, faFlask, faCircleNotch, faCircleExclamation, faLightbulb, faVault, faSliders, faShieldHalved, faXmark } from '@fortawesome/free-solid-svg-icons';
import { faHardDrive } from '@fortawesome/free-regular-svg-icons';
import { UserService } from '../services/User/user.service';
import { HttpClient } from '@angular/common/http';

import { Utils } from '../common/Utils/utils';
import { ActivatedRoute, Router } from '@angular/router';
import { Crypto } from '../common/Crypto/crypto';
import { TranslateService } from '@ngx-translate/core';
import { ToastrService } from 'ngx-toastr';
import { GlobalConfigurationService } from '../services/GlobalConfiguration/global-configuration.service';

@Component({
    selector: 'app-preferences',
    templateUrl: './preferences.component.html',
    styleUrls: ['./preferences.component.css'],
    standalone: false,
    changeDetection: ChangeDetectionStrategy.OnPush,
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

  buttonLoading = signal({ favicon_policy: false, backup_conf_max_age: false, backup_conf_min_count: false });
  moreHelpDisplayed = signal({ favicon_settings: false });

  isDisplayingAdvancedSettings = signal(false);
  faviconPolicy = signal(""); // never, always, enabledOnly
  loadingPreferences = signal(true);
  loadingPreferencesError = signal(false);
  notification_message = signal<string | undefined>(undefined);
  autolock_delay = signal(10);
  autolock_display_error = signal(false);
  autolock_is_updating = signal(false);
  autolock_update_done_animation = signal(false);
  autolock_update_failed_animation = signal(false);
  autolock_value_updated = signal(false);
  duration_unit = signal("");
  minimum_duration = signal(-1);
  maximum_duration = signal(-1);
  loading_backup_configuration = signal(true);
  backup_max_age = signal(-1);
  backup_minimum_count = signal(-1);
  default_backup_max_age = signal(-1);
  default_backup_minimum_count = signal(-1);
  is_google_drive_enabled_on_this_tenant = signal(false);

  constructor( 
    private http: HttpClient,
    public userService: UserService,
    private utils: Utils,
    private router: Router,
    private route: ActivatedRoute,
    private translate: TranslateService,
    private toastr: ToastrService,
    private globalConfigurationService: GlobalConfigurationService
    ){
    }

  
  ngOnInit(): void {
     if(!this.userService.isUserLoggedIn()){
      this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
    }
    this.get_preferences()
    this.get_internal_notification()
    this.get_backup_configuration()
    this.check_if_google_drive_is_enabled_on_this_tenant()
    this.duration_unit.set("hour");
  }

  get_preferences(){
    this.http.get("/api/v1/preferences?fields=all", {withCredentials: true, observe: 'response'}).subscribe({
      next: (response) => {
      if(response.body != null){
        this.loadingPreferences.set(false);
        const data = JSON.parse(JSON.stringify(response.body));
        if(data.autolock_delay != null){
          if(Math.floor(data.autolock_delay/60) == data.autolock_delay/60){
            this.autolock_delay.set(data.autolock_delay/60);
            this.duration_unit.set("hour");
          } else {
            this.autolock_delay.set(data.autolock_delay);
            this.duration_unit.set("minute");
          }
        } else {
          this.autolock_delay.set(10);
          this.duration_unit.set("minute");
        }
        if(data.favicon_policy != null){
          this.faviconPolicy.set(data.favicon_policy);
        } else {
          this.loadingPreferencesError.set(true);
          this.faviconPolicy.set("enabledOnly");
          this.translate.get('preference.error.fetch').subscribe((translation: string) => {
            this.utils.toastError(this.toastr,translation,"")
          });
        }
      }
    }, 
    error: (error) => {
      this.loadingPreferencesError.set(true);
      this.loadingPreferences.set(false);
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
    }});
  }


  check_if_google_drive_is_enabled_on_this_tenant() {
    return this.globalConfigurationService.is_google_drive_enabled_on_this_tenant().then((enabled) => {
      this.is_google_drive_enabled_on_this_tenant.set(enabled);
    }, (error) => {
      console.log(error);
      this.is_google_drive_enabled_on_this_tenant.set(false);
    });
  }

  get_backup_configuration(){
    this.http.get("/api/v1/backup/configuration?dv=true",{withCredentials:true, observe: 'response'}).subscribe({
      next:(response) => {
        if(response.body != null){
          const data = JSON.parse(JSON.stringify(response.body));
          this.backup_max_age.set(data.max_age_in_days);
          this.backup_minimum_count.set(data.backup_minimum_count);
          this.default_backup_max_age.set(data.default_max_age_in_days);
          this.default_backup_minimum_count.set(data.default_backup_minimum_count);
          this.loading_backup_configuration.set(false);
        } else {
          this.loadingPreferencesError.set(true);
          this.loading_backup_configuration.set(false);
          this.translate.get('preference.error.fetch').subscribe((translation: string) => {
            this.utils.toastError(this.toastr,translation,"")
          });
        }
      },
      error: (error)=>{
        this.loadingPreferencesError.set(true);
        this.loading_backup_configuration.set(false);
        this.translate.get('preference.error.fetch').subscribe((translation: string) => {
          this.utils.toastError(this.toastr,translation,error.error.message)
        });
      }
    });
  }


  changeFaviconSettings(policy: string){
    if(policy == "never" || policy == "always" || policy == "enabledOnly"){
      this.buttonLoading.update(b => ({ ...b, favicon_policy: true }));
      const data = {"id" : "favicon_policy", "value" :policy}
      this.http.put("/api/v1/preferences",  data, {withCredentials: true, observe: 'response'}).subscribe({
        next: () => {
          this.buttonLoading.update(b => ({ ...b, favicon_policy: false }));
          this.faviconPolicy.set(policy);
        }, 
        error:(error) => {
          this.buttonLoading.update(b => ({ ...b, favicon_policy: false }));
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
        }
      });
    }
  }

  updateBackupConfiguration(key:string){
    let value = -1;
    if(key == "max_age_in_days"){
      this.buttonLoading.update(b => ({ ...b, backup_conf_max_age: true }));
      value = this.backup_max_age();
    } else if(key == "backup_minimum_count"){
      this.buttonLoading.update(b => ({ ...b, backup_conf_min_count: true }));
      value = this.backup_minimum_count();
    } else {
      return;
    }

    this.http.put("/api/v1/backup/configuration/"+key, {"value":value}, {withCredentials:true, observe: 'response'}).subscribe({
      next:(response) => {
        if(response.status == 200){
          this.get_backup_configuration();
          if(key == "max_age_in_days"){
            this.buttonLoading.update(b => ({ ...b, backup_conf_max_age: false }));
          } else if(key == "backup_minimum_count"){
            this.buttonLoading.update(b => ({ ...b, backup_conf_min_count: false }));
          }
        }
      },
      error: (error)=>{
        this.get_backup_configuration();
        if(key == "max_age_in_days"){
          this.buttonLoading.update(b => ({ ...b, backup_conf_max_age: false }));
        } else if(key == "backup_minimum_count"){
          this.buttonLoading.update(b => ({ ...b, backup_conf_min_count: false }));
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
      }
    });
  }


  displayAdvancedSettings(){
    this.isDisplayingAdvancedSettings.set(true);
  }

  get_internal_notification(){
    this.http.get("/api/v1/notification/internal",  {withCredentials:true, observe: 'response'}).subscribe({
      next: (response) => {
        if(response.status == 200){
          try{
            const data = JSON.parse(JSON.stringify(response.body))
            if (data.display_notification){
              this.notification_message.set(data.message);
            }
          } catch (error){
            console.log(error);
          }
        }
      }, 
      error: (error) => {
        console.log(error);
      }
    });
  }


  autolockDelayToMinutes(){
    if(this.duration_unit() == "hour"){
      return this.autolock_delay() * 60;
    } else {
      return this.autolock_delay();
    }
  }

  autolockDelayUpdate(){
    this.autolock_display_error.set(false);
    this.autolock_value_updated.set(false);
    this.autolock_is_updating.set(true);
    const autolock_delay_minutes = this.autolockDelayToMinutes();
    this.http.put("/api/v1/preferences", {"id":"autolock_delay", "value":autolock_delay_minutes}, {withCredentials: true, observe: 'response'}).subscribe({
      next: () => {
        this.autolock_value_updated.set(true);
        this.autolockDelayUpdateDone();
      }, 
      error: (error) => {
        this.autolock_is_updating.set(false);
        if(error.status == 400){
          if(error.error.message == "invalid_duration"){
            this.autolock_display_error.set(true);
            this.autolockDelayUpdateFailed();
            this.minimum_duration.set(error.error.minimum_duration_min);
            this.maximum_duration.set(error.error.maximum_duration_min/60);
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
      }
    });
  }

  autolockDelayUpdateDone(){
    this.autolock_is_updating.set(false);
    this.autolock_update_done_animation.set(true);
    setTimeout(() => {
      this.autolock_update_done_animation.set(false);
    }, 1000);
  }

  autolockDelayUpdateFailed(){
    this.autolock_is_updating.set(false);
    this.autolock_update_failed_animation.set(true);
    setTimeout(() => {
      this.autolock_update_failed_animation.set(false);
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
      this.duration_unit.set("minute");
    } else if(value == "hour"){
      this.duration_unit.set("hour");
    } 
  }
}