import { Component, signal } from '@angular/core';
import { Router, RouterLink, NavigationEnd } from '@angular/router';
import { NgClass } from '@angular/common';
import { TranslatePipe } from '@ngx-translate/core';
import { NavbarLangSelectorComponent } from 'src/shared/Views/navbar-lang-selector/navbar-lang-selector.component';

@Component({
  selector: 'app-rescue-navbar',
  imports: [
    RouterLink,
    NgClass,
    TranslatePipe,
    NavbarLangSelectorComponent
  ],
  templateUrl: './rescue-navbar.component.html',
  styleUrl: './rescue-navbar.component.css',
})
export class RescueNavbarComponent {
  isNavbarExpanded = signal(false)
  currentUrl = signal("")



  constructor(
    private router: Router,
  ) {
    router.events.subscribe((url: any) => {
      if (url instanceof NavigationEnd) {
        this.currentUrl.set(url.url);
      }
    });
  }

}
