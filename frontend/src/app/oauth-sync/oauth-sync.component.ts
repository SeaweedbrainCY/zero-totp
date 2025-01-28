import { Component, OnInit, Injectable, inject } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { UserService } from '../common/User/user.service';
import { HttpClient } from '@angular/common/http';

import { faCircleNotch } from '@fortawesome/free-solid-svg-icons';
import { Crypto } from '../common/Crypto/crypto';
import { Utils } from '../common/Utils/utils';
@Component({
    selector: 'app-oauth-sync',
    templateUrl: './oauth-sync.component.html',
    styleUrls: ['./oauth-sync.component.css'],
    standalone: false
})
@Injectable({providedIn: 'root'})
export class OauthSyncComponent implements OnInit {
  errorMessage = '';
  errorDetail = "";
  faCircleNotch = faCircleNotch;
  credentials:string|null;
  encrypted_credentials:string|null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private userService: UserService,
    private http: HttpClient,
    private crypto: Crypto,
    private utils: Utils,
  ) { 
   const creds_b64 = this.utils.getCookie('credentials');
    if(creds_b64 != null){
      this.credentials = creds_b64;
    } else {
      this.credentials = null;
    }
  }

  ngOnInit(): void {
    if(this.userService.getId() == null){
      this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
  } else {
      this.backupVault();
  }
  }

  backupVault(){
    this.http.put("/api/v1/google-drive/backup", {}, {withCredentials:true, observe: 'response'}, ).subscribe((response) => {
      this.router.navigate(["/vault"], {relativeTo:this.route.root});
    }, (error) => {
      let errorMessage = "";
      if(error.error.message != null){
        errorMessage = error.error.message;
      } else if(error.error.detail != null){
        errorMessage = error.error.title;
      }
      this.errorMessage = 'oauth.error.impossible' ;
      this.errorDetail = errorMessage;
    });
  }
  

}


