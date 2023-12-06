import { Component } from '@angular/core';
import { faPaperPlane, faArrowRotateLeft } from '@fortawesome/free-solid-svg-icons';
@Component({
  selector: 'app-email-verification',
  templateUrl: './email-verification.component.html',
  styleUrls: ['./email-verification.component.css']
})
export class EmailVerificationComponent {
  faPaperPlane = faPaperPlane;
  faArrowRotateLeft = faArrowRotateLeft;
  constructor() { }

}
