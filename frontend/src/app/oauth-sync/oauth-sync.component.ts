import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { UserService } from '../common/User/user.service';
import { HttpClient } from '@angular/common/http';
import { ApiService } from '../common/ApiService/api-service';
import { faCircleNotch } from '@fortawesome/free-solid-svg-icons';
import { CookieService } from 'ngx-cookie';
import { Crypto } from '../common/Crypto/crypto';

@Component({
  selector: 'app-oauth-sync',
  templateUrl: './oauth-sync.component.html',
  styleUrls: ['./oauth-sync.component.css']
})
export class OauthSyncComponent implements OnInit {
  errorMessage = '';
  faCircleNotch = faCircleNotch;
  encrypted_access_token = '';
  encrypted_refresh_token = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private userService: UserService,
    private http: HttpClient,
    private cookieService: CookieService,
    private crypto: Crypto,
  ) { }

  ngOnInit(): void {
    if(this.userService.getId() == null){
      this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
  } else {
      this.encryptTokens().then(() => {
        this.uploadEncryptedTokens();
      }, (_) => {
       return;
      });
  }
  }

  encryptTokens(): Promise<Boolean>{
    return new Promise((resolve, reject) => {
      const access_token = this.cookieService.get('google_drive_token_id');
      const refresh_token = this.cookieService.get('google_drive_refresh_token');
      if(access_token == '' || refresh_token == '' || access_token == undefined || refresh_token == undefined){
        this.errorMessage = 'Authentication with Google Drive impossible. Verify that you have allowed Zero-TOTP to access your Google Drive account.';
        reject(false);
      } else {
        const zke_key = this.userService.get_zke_key();
        if (zke_key == null){
          this.errorMessage = 'Encryption key not found. Please log out and log in again.';
          reject(false);
        } else {
          this.crypto.encrypt(access_token, zke_key).then((encrypted_access_token) => {
            this.crypto.encrypt(refresh_token, zke_key).then((encrypted_refresh_token) => {
              this.encrypted_access_token = encrypted_access_token;
              this.encrypted_refresh_token = encrypted_refresh_token;
              resolve(true);
            }, (error) => {
              this.errorMessage = "An error occured while encrypted token." +error;
              reject(false);
            });
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
      "enc_access_token" : this.encrypted_access_token,
      "enc_refresh_token" : this.encrypted_refresh_token
    }
    this.http.post(ApiService.API_URL+"/google-drive/oauth/enc-tokens",  data, {withCredentials: true, observe: 'response'}).subscribe((response) => {
        this.router.navigate(["/vault"], {relativeTo:this.route.root});
      }, (error) => {
        this.errorMessage = "An error occured while storing your encrypted access tokens." + error.error.message;
      });
  }
}


