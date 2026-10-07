import { Component, ChangeDetectionStrategy, OnInit } from '@angular/core';
import { faBugSlash, faWifi, faCircleUp, faHouse, faMobileScreenButton, faCode, faKitMedical, faAngleDown } from '@fortawesome/free-solid-svg-icons';
import { faGithub } from '@fortawesome/free-brands-svg-icons';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';
import { TranslateDirective, TranslatePipe } from '@ngx-translate/core';


@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [
    FaIconComponent,
    TranslatePipe,
  ],
})



export class RescueHomeComponent implements OnInit {
  faBugSlash = faBugSlash;
  faWifi = faWifi;
  faGithub = faGithub;
  faCircleUp = faCircleUp;
  faHouse = faHouse;
  faMobileScreenButton = faMobileScreenButton;
  faCode = faCode;
  faKitMedical = faKitMedical;
  faAngleDown = faAngleDown;

  constructor(){
  }

  ngOnInit(){
  }




}
