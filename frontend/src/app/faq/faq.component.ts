import { Component, AfterViewInit } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';
import { ToastrService } from 'ngx-toastr';
import {faChevronUp, faChevronDown, faMagnifyingGlass, faStopwatch, faShieldHalved, faVault} from '@fortawesome/free-solid-svg-icons';
import { faGoogle } from '@fortawesome/free-brands-svg-icons';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-faq',
  templateUrl: './faq.component.html',
  styleUrl: './faq.component.css',
  standalone: false
})
export class FaqComponent  implements AfterViewInit {
  faChevronUp = faChevronUp;
  faChevronDown = faChevronDown;
  faMagnifyingGlass = faMagnifyingGlass;
  faVault = faVault;
  faGoogle = faGoogle;
  faShieldHalved = faShieldHalved;
  faStopwatch=faStopwatch;
  theme: string | null = "light";
  toggled_q_id : string[] = [];

  constructor(
    private translate: TranslateService, 
    private toastr: ToastrService,
    private route: ActivatedRoute,

  ) {
    this.theme = window.document.documentElement.getAttribute('data-theme');
    console.log(this.theme);
    
  }

  ngAfterViewInit(): void {
    setTimeout(() => {
      const section_id = this.route.snapshot.paramMap.get('id');
    if (section_id){
      const element = document.getElementById(section_id);
      if (element) {
        this.scrollTo(element);
      }
    }}, 500);
  }


  toggle(id:string){
    if(this.toggled_q_id.includes(id)){
      this.toggled_q_id = this.toggled_q_id.filter((value) => value !== id);
    }else{
      this.toggled_q_id.push(id);
    }
    console.log(this.toggled_q_id);
  }

  scrollTo(element: HTMLElement) {
    element.scrollIntoView({behavior: "smooth", block: "start", inline: "nearest"});
  }

}
