import { Component, signal, inject, OnInit } from '@angular/core';
import { TranslatePipe, TranslateService } from '@ngx-translate/core';
import { isDeviceMobile } from 'src/shared/Utils/utils';
@Component({
  selector: 'app-zero-totp-instance-selector',
  imports: [TranslatePipe],
  templateUrl: './zero-totp-instance-selector.component.html',
  styleUrl: './zero-totp-instance-selector.component.css',
})
export class ZeroTotpInstanceSelectorComponent  implements OnInit {
  //DI
  translate = inject(TranslateService)

  //signal
  instance_dropdown_active = signal(false)



  //signals
  current_domain = signal('');


  ngOnInit(): void {
    this.current_domain.set(window.location.host);
  }

  zero_totp_instance_button_click() {
      if (isDeviceMobile()) {
        // On nonMobileDevice, it's just hoverable
        this.instance_dropdown_active.update(v => !v);
    }
  }

}
