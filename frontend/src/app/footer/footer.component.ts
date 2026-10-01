import { Component, signal } from '@angular/core';
import { faGithub, faLinkedin } from '@fortawesome/free-brands-svg-icons';
import { faGlobe, faEnvelope } from '@fortawesome/free-solid-svg-icons';
import { environment } from 'src/environments/environment';
import { RouterLink } from '@angular/router';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';
import { TranslatePipe } from '@ngx-translate/core';

@Component({
    selector: 'app-footer',
    templateUrl: './footer.component.html',
    styleUrls: ['./footer.component.css'],
    imports: [RouterLink, FaIconComponent, TranslatePipe]
})
export class FooterComponent {
  
  faGithub = faGithub;
  faLinkedin = faLinkedin;
  faGlobe = faGlobe;
  faEnvelope = faEnvelope;
  imageHash = environment.imageHash;
  today_year = new Date().getFullYear();
  current_domain = signal("")

  
      constructor() { 
        this.current_domain.set(window.location.host);
      }

}
