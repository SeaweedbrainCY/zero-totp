import { Component } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { ToastrService } from 'ngx-toastr';
import {faChevronUp, faChevronDown, faMagnifyingGlass, faStopwatch, faShieldHalved} from '@fortawesome/free-solid-svg-icons';


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
  faShieldHalved = faShieldHalved;
  faStopwatch=faStopwatch;
  theme: string | null = "light";
  toggled_q_id : string[] = [];

  constructor(
    private translate: TranslateService, 
    private toastr: ToastrService) {
    this.theme = window.document.documentElement.getAttribute('data-theme');
    console.log(this.theme);
  }


  toggle(id:string){
    if(this.toggled_q_id.includes(id)){
      this.toggled_q_id = this.toggled_q_id.filter((value) => value !== id);
    }else{
      this.toggled_q_id.push(id);
    }
    console.log(this.toggled_q_id);
  }

}
