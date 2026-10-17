import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { RescueNavbarComponent } from './rescue-navbar/rescue-navbar.component';
import { FooterComponent } from 'src/shared/Views/footer/footer.component';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  imports: [RouterOutlet, RescueNavbarComponent, FooterComponent],
})
export class AppComponent {}
