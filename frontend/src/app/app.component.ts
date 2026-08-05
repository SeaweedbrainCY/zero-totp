import { Component, OnInit, DOCUMENT, signal } from '@angular/core';
import { environment } from 'src/environments/environment';
import { Renderer2, Inject } from '@angular/core';
import { AuthServiceService } from './services/AuthService/auth-service.service';
import { UserService } from './services/User/user.service';
import { Router, ActivatedRoute } from '@angular/router';
import { ProtectedKeychainStorageService } from './services/Capacitor/ProtectedKeychainStorage/protected-keychain-storage.service';
import { faSignal, faBriefcaseMedical } from '@fortawesome/free-solid-svg-icons';


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  standalone: false
})
export class AppComponent implements OnInit {
  title = 'frontend';
  faSignal = faSignal;
  faBriefcaseMedical = faBriefcaseMedical;
  isAppLoading = signal(true)
  displayTroubleshootingMessage = signal(false)

  constructor(
    private renderer: Renderer2,
    @Inject(DOCUMENT) private document: Document,
    private authService: AuthServiceService,
    private userService: UserService,
    private router: Router,
    private route: ActivatedRoute,
    private protectedKeychainStorageService: ProtectedKeychainStorageService
  ) {
    const theme = localStorage.getItem('theme');
    if (theme == 'dark') {
      this.renderer.setAttribute(document.documentElement, 'data-theme', 'dark');
    } else {
      this.renderer.setAttribute(document.documentElement, 'data-theme', 'light');
    }
  }

  async loadUserData(): Promise<boolean> {
    if (environment.isMobileApp) {
      await this.authService.loadTokenFromKeychain()
    }
    if (this.userService.zke_key() == null) {
      try {
        console.log("Refreshing user_id")
        await this.userService.refresh_user_id()
        if (environment.isMobileApp) {
          // Try to load the zke_key from keychain
          const zke_key = await this.protectedKeychainStorageService.getZKEKey()
          this.userService.zke_key.set(zke_key)
        }
        return true
      } catch (error) {
        console.log(error)
        return false
      }
    } else {
      return true
    }
  }



  ngOnInit(): void {
    console.log("Loading user data...")
    setTimeout(() => {
      if (this.isAppLoading()) {
        this.displayTroubleshootingMessage.set(true)
      }
    }, 5000)
    this.loadUserData().then((isSuccess) => {
      if (isSuccess) {
        this.router.navigate(['/vault'], { relativeTo: this.route.root });
      }
      if (environment.isMobileApp) {
        this.router.navigate(['/login'], { relativeTo: this.route.root });
      }
      this.isAppLoading.set(false)
    }, (error) => {
      if (environment.isMobileApp) {
        this.router.navigate(['/login'], { relativeTo: this.route.root });
      }
      this.isAppLoading.set(false)
    })
  }
}



// Inject the document object

