import { Component } from '@angular/core';
import { faFileArrowDown } from '@fortawesome/free-solid-svg-icons'; 
import { TranslateService } from '@ngx-translate/core';

@Component({
  selector: 'app-import-vault',
  templateUrl: './import-vault.component.html',
  styleUrl: './import-vault.component.css'
})
export class ImportVaultComponent {
  faFileArrowDown = faFileArrowDown;
  constructor(
    private translate: TranslateService,
  ) { 
    
  }
}
