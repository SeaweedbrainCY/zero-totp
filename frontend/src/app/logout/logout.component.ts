import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { UserService } from '../services/User/user.service';
import { HttpClient } from '@angular/common/http';
import { faCircleNotch } from '@fortawesome/free-solid-svg-icons';
import { ApiService } from '../services/API/api.service';
import { environment } from 'src/environments/environment';
import { AuthServiceService } from '../services/AuthService/auth-service.service';
import { ProtectedKeychainStorageService } from '../services/Capacitor/ProtectedKeychainStorage/protected-keychain-storage.service';
import { CapacitorPersistentStorageService } from '../services/Capacitor/persistentStorage/capacitor-persistent-storage.service';
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
    private protectedKeychainStorage: ProtectedKeychainStorageService,
    private persistentStorage: CapacitorPersistentStorageService
  ) { }

  ngOnInit(): void {
    // If user visits /logout/lock we don't really logout but just lock the application
    const route = this.route.snapshot.url
    if (route.length == 1 && route[0].path == "lock") {
      this.lockApplication().then(() => {
        this.router.navigate(["/vault"], { relativeTo: this.route.root });
      })
    } else {
      this.loggout().then(() => {
        this.router.navigate(["/login"], { relativeTo: this.route.root });
      })
    }
  }

  async loggout(): Promise<void> {
    await this.http.put(this.apiService.baseURL + '/api/v1/logout', {}, { withCredentials: true, observe: 'response' })
    if (environment.isMobileApp) {
      await this.persistentStorage.deleteBiometricProtectionPreference(this.userService.id()!)
      await this.authService.clearToken()
      await this.protectedKeychainStorage.deleteZKEKey()
    }
    this.userService.clear();
  }

  async lockApplication(): Promise<void> {
    this.userService.clear();
  }
}
