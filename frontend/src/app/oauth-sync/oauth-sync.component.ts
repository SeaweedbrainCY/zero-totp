import { Component, OnInit, Injectable, inject } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { UserService } from '../common/User/user.service';
import { HttpClient } from '@angular/common/http';
import { ApiService } from '../common/ApiService/api-service';
import { faCircleNotch } from '@fortawesome/free-solid-svg-icons';
import { Crypto } from '../common/Crypto/crypto';
import { Utils } from '../common/Utils/utils';
@Component({
  selector: 'app-oauth-sync',
  templateUrl: './oauth-sync.component.html',
  styleUrls: ['./oauth-sync.component.css'],

})
@Injectable({providedIn: 'root'})
export class OauthSyncComponent implements OnInit {
  errorMessage = '';
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
      this.credentials = atob(creds_b64);
    } else {
      this.credentials = null;
    }
  }

  ngOnInit(): void {
    if(this.userService.getId() == null){
      this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
  } else {
      this.encryptCredentials().then(() => {
        this.uploadEncryptedTokens();
      }, (_) => {
       return;
      });
  }
  }

  encryptCredentials(): Promise<Boolean>{
    return new Promise((resolve, reject) => {
      if(this.credentials == '' || this.credentials == undefined){
        this.errorMessage = 'Authentication with Google Drive impossible. Verify that you have allowed Zero-TOTP to access your Google Drive account.';
        reject(false);
      } else {
        const zke_key = this.userService.get_zke_key();
        if (zke_key == null){
          this.errorMessage = 'Encryption key not found. Please log out and log in again.';
          reject(false);
        } else {
          this.crypto.encrypt(this.credentials, zke_key).then((encrypted_credentials) => {
              this.encrypted_credentials = encrypted_credentials;
              resolve(true);
          }, (error) => {
            this.errorMessage = "An error occured while encrypted token." + error;
            reject(false);
          });
        }
      }
    });
  }

  uploadEncryptedTokens(){
    this.errorMessage = '';
    const data = {
      "enc_credentials" : this.encrypted_credentials,
    }
    this.http.post(ApiService.API_URL+"/google-drive/oauth/enc-credentials",  data, {withCredentials: true, observe: 'response'}).subscribe((response) => {
        this.userService.setGoogleDriveSync(true);
        this.router.navigate(["/vault"], {relativeTo:this.route.root});
        sessionStorage.removeItem('credentials');
      }, (error) => {
        this.errorMessage = "An error occured while storing your encrypted access tokens." + error.error.message;
      });
  }
}


