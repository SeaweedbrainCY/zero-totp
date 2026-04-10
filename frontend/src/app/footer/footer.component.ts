import { Component, signal } from '@angular/core';
import { faGithub, faLinkedin } from '@fortawesome/free-brands-svg-icons';
import { faGlobe, faEnvelope } from '@fortawesome/free-solid-svg-icons';
import { environment } from 'src/environments/environment';

@Component({
    selector: 'app-footer',
    templateUrl: './footer.component.html',
    styleUrls: ['./footer.component.css'],
    standalone: false
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
