import { Component, signal } from '@angular/core';
import { Router, RouterLink, NavigationEnd } from '@angular/router';
import { NgClass } from '@angular/common';

@Component({
  selector: 'app-rescue-navbar',
  imports: [
    RouterLink,
    NgClass,
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
