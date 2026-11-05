import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import {  TranslatePipe } from '@ngx-translate/core';


@Component({
  selector: 'app-mobile-home',
  imports: [
    RouterLink,
    TranslatePipe,
  ],
  templateUrl: './mobile-home.component.html',
  styleUrl: './mobile-home.component.css',
})
export class MobileHomeComponent {


}
