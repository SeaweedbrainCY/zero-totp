import { Component } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { ToastrService } from 'ngx-toastr';
import {faChevronUp, faChevronDown, faMagnifyingGlass, faStopwatch} from '@fortawesome/free-solid-svg-icons';


@Component({
  selector: 'app-faq',
  templateUrl: './faq.component.html',
  styleUrl: './faq.component.css',
  standalone: false
})
export class FaqComponent {
  faChevronUp = faChevronUp;
  faChevronDown = faChevronDown;
  faMagnifyingGlass = faMagnifyingGlass;
  faStopwatch=faStopwatch;
  theme: string | null = "light";

  constructor(
    private translate: TranslateService, 
    private toastr: ToastrService) {
    this.theme = window.document.documentElement.getAttribute('data-theme');
    console.log(this.theme);
  }

}
