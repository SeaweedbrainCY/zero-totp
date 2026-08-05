import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { UserService } from '../services/User/user.service';
import { HttpClient } from '@angular/common/http';
import { faCircleNotch } from '@fortawesome/free-solid-svg-icons';
import { ApiService } from '../services/API/api.service';
import { environment } from 'src/environments/environment';
import { AuthServiceService } from '../services/AuthService/auth-service.service';
import { ProtectedKeychainStorageService } from '../services/Capacitor/ProtectedKeychainStorage/protected-keychain-storage.service';

@Component({
  selector: 'app-logout',
  templateUrl: './logout.component.html',
  styleUrls: ['./logout.component.css'],
  standalone: false
})
export class LogoutComponent implements OnInit {
  faCircleNotch = faCircleNotch;

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private userService: UserService,
    private http: HttpClient,
    private apiService: ApiService,
    private authService: AuthServiceService,
    private protectedKeychainStorage: ProtectedKeychainStorageService
  ) { }

  ngOnInit(): void {
    this.loggout().then(() => {
      this.router.navigate(["/login"], { relativeTo: this.route.root });
    })
  }

  async loggout(): Promise<void> {
    if (environment.isMobileApp) {
      await this.authService.clearToken()
      await this.protectedKeychainStorage.deleteZKEKey()
    }
    this.http.put(this.apiService.baseURL + '/api/v1/logout', {}, { withCredentials: true, observe: 'response' }).subscribe({
      next: () => {
        this.userService.clear();
      },
      error: () => {
        this.userService.clear();
      }
    });
  }
}
