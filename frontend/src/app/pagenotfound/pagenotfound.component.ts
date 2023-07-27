import { Component } from '@angular/core';
import { ActivatedRoute, Router, NavigationEnd } from '@angular/router';

@Component({
  selector: 'app-pagenotfound',
  templateUrl: './pagenotfound.component.html',
  styleUrls: ['./pagenotfound.component.css']
})
export class PagenotfoundComponent {
  currentUrl: string = "";
  constructor(
    private router: Router,
    private route: ActivatedRoute
  ) {

    router.events.subscribe((url: any) => {
      if (url instanceof NavigationEnd) {
        this.currentUrl = url.url;
      }
    }
    );
  }

  ngOnInit(): void {

  }
  navigateToRoute(route: string) {
    window.document.getElementById('menuButton')?.click();
    this.router.navigate([route], { relativeTo: this.route.root });
  }
}




