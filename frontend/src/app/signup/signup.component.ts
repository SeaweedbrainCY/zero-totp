import { Component } from '@angular/core';
import { faEnvelope, faLock,  faCheck, faUser, faXmark, faFlagCheckered } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-signup',
  templateUrl: './signup.component.html',
  styleUrls: ['./signup.component.css']
})
export class SignupComponent {
  faEnvelope=faEnvelope;
  faLock=faLock;
  faCheck=faCheck;
  faUser=faUser;
  faXmark=faXmark;
  faFlagCheckered=faFlagCheckered;

}
