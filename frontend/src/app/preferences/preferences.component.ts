import { Component, OnInit } from '@angular/core';
import { toast as superToast } from 'bulma-toast'
import { faEnvelope, faLock,  faCheck, faUser, faCog, faShield, faHourglassStart, faCircleInfo, faArrowsRotate, faFlask } from '@fortawesome/free-solid-svg-icons';
import { UserService } from '../common/User/user.service';
import { HttpClient } from '@angular/common/http';
import { ApiService } from '../common/ApiService/api-service';
import { Utils } from '../common/Utils/utils';
import { ActivatedRoute, Router } from '@angular/router';
import { Crypto } from '../common/Crypto/crypto';
import { Buffer } from 'buffer';

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
  faCheck=faCheck;
  faCog=faCog;
  faFlask=faFlask;
  buttonLoading  ={"favicon_settings":false}
  moreHelpDisplayed = {"favicon_settings":false}
  isDisplayingAdvancedSettings = false;
  faviconPolicy="enabledOnly"; // never, always, enabledOnly
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
      // this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
    } 
  }

  changeFaviconSettings(policy: string){
    console.log("new_policy = ", policy);
    if(policy == "never" || policy == "always" || policy == "enabledOnly"){
      this.faviconPolicy = policy;
    } else {
      console.log("unknown policy")
    }
    console.log("policy =" , this.faviconPolicy);
  }


  displayAdvancedSettings(){
    this.isDisplayingAdvancedSettings = true;
  }
}
