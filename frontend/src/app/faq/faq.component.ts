import { Component } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { ToastrService } from 'ngx-toastr';
import {faChevronUp, faChevronDown} from '@fortawesome/free-solid-svg-icons';


@Component({
  selector: 'app-faq',
  templateUrl: './faq.component.html',
  styleUrl: './faq.component.css',
  standalone: false
})
export class FaqComponent {
  faChevronUp = faChevronUp;
  faChevronDown = faChevronDown;

  constructor(
    private translate: TranslateService, 
    private toastr: ToastrService) {
    
  }

}
