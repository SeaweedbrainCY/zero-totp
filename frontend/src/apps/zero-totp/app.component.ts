import { Component, OnInit, DOCUMENT, signal } from '@angular/core';
import { environment } from 'src/environments/environment';
import { Renderer2, Inject } from '@angular/core';
import { AuthServiceService } from './services/AuthService/auth-service.service';
import { UserService } from '../../shared/Services/User/user.service';
import { Router, ActivatedRoute, RouterOutlet, NavigationEnd } from '@angular/router';
import { ProtectedKeychainStorageService } from './services/Capacitor/ProtectedKeychainStorage/protected-keychain-storage.service';
import { faSignal, faBriefcaseMedical } from '@fortawesome/free-solid-svg-icons';
import { Keyboard } from '@capacitor/keyboard';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';
import { NavbarComponent } from './navbar/navbar.component';
import { FooterComponent } from '../../shared/Views/footer/footer.component';
import { TranslatePipe } from '@ngx-translate/core';
import { filter, firstValueFrom } from 'rxjs';



@Component({
    selector: 'app-root',
    templateUrl: './app.component.html',
    styleUrls: ['./app.component.css'],
    imports: [FaIconComponent, NavbarComponent, RouterOutlet, FooterComponent, TranslatePipe]
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

  private async currentRouteRequiresDecryptedVault(): Promise<boolean> {
    // On a page refresh, AppComponent can init before the first navigation has resolved
    if (!this.router.navigated) {
      await firstValueFrom(this.router.events.pipe(filter(e => e instanceof NavigationEnd)));
    }
    let snap = this.router.routerState.snapshot.root;
    while (snap.firstChild) snap = snap.firstChild;
    return !!snap.data['requiresDecryptedVault'];
  }



  ngOnInit(): void {
    console.log("Loading user data...")
    setTimeout(() => {
      if (this.isAppLoading()) {
        this.displayTroubleshootingMessage.set(true)
      }
    }, 5000)
    this.loadUserData().then(async (isSuccess) => {
      if (isSuccess  && await this.currentRouteRequiresDecryptedVault()) {
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

    if (environment.isMobileApp) {
      document.addEventListener('click', (e) => {
        const target = e.target as HTMLElement;
        const isFormControl = target.matches('input, textarea, select, [contenteditable]');
        if (!isFormControl) {
          Keyboard.hide();
        }
      });
    }
  }
}



// Inject the document object
