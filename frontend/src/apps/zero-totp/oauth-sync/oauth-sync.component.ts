import { Component, OnInit, Injectable, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { UserService } from '../services/User/user.service';
import { HttpClient } from '@angular/common/http';

import { faCircleNotch } from '@fortawesome/free-solid-svg-icons';
import { Crypto } from '../../../shared/Crypto/crypto';
import { getCookie } from '../../../shared/Utils/utils';
import { ApiService } from '../services/API/api.service';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';
import { TranslatePipe } from '@ngx-translate/core';
@Component({
    selector: 'app-oauth-sync',
    templateUrl: './oauth-sync.component.html',
    styleUrls: ['./oauth-sync.component.css'],
    imports: [FaIconComponent, TranslatePipe]
})
@Injectable({ providedIn: 'root' })
export class OauthSyncComponent implements OnInit {
  errorMessage = signal('');
  errorDetail = signal("");
  faCircleNotch = faCircleNotch;
  credentials: string | null;
  encrypted_credentials: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private userService: UserService,
    private http: HttpClient,
    private crypto: Crypto,
    private apiService: ApiService
  ) {
    const creds_b64 = getCookie('credentials');
    if (creds_b64 != null) {
      this.credentials = creds_b64;
    } else {
      this.credentials = null;
    }
  }

  ngOnInit(): void {
    if (this.userService.id() == null) {
      this.router.navigate(["/login/sessionKilled"], { relativeTo: this.route.root });
    } else {
      this.backupVault();
    }
  }

  backupVault() {
    this.http.put(this.apiService.baseURL + "/api/v1/google-drive/backup", {}, { withCredentials: true, observe: 'response' },).subscribe({
      next: () => {
        this.router.navigate(["/vault"], { relativeTo: this.route.root });
      },
      error: (error) => {
        let errorMessage = "";
        if (error.error.message != null) {
          errorMessage = error.error.message;
        } else if (error.error.detail != null) {
          errorMessage = error.error.title;
        }
        this.errorMessage.set('oauth.error.impossible');
        this.errorDetail.set(errorMessage);
      }
    });
  }


}
