import { Component } from '@angular/core';
import { faFileArrowDown, faArrowRight } from '@fortawesome/free-solid-svg-icons'; 
import { TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-import-vault',
  templateUrl: './import-vault.component.html',
  styleUrl: './import-vault.component.css'
})
export class ImportVaultComponent {
  faFileArrowDown = faFileArrowDown;
  faArrowRight = faArrowRight;
  constructor(
    private translate: TranslateService,
  ) { 
    
  }
}
