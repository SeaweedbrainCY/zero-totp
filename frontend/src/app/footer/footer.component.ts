import { Component } from '@angular/core';
import { faGithub, faLinkedin } from '@fortawesome/free-brands-svg-icons';
import { faGlobe, faEnvelope } from '@fortawesome/free-solid-svg-icons';
import { environment } from 'src/environments/environment';

@Component({
  selector: 'app-footer',
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.css']
})
export class FooterComponent {
  
  faGithub = faGithub;
  faLinkedin = faLinkedin;
  faGlobe = faGlobe;
  faEnvelope = faEnvelope;
  imageHash = environment.imageHash;
  
      constructor() { }

}
