
import { Component, inject, OnInit, signal } from '@angular/core';
import { ApiService } from 'src/shared/Services/API/api.service';
import { CapacitorPersistentStorageService } from '../services/Capacitor/persistentStorage/capacitor-persistent-storage.service';
import { TranslateService, TranslatePipe } from '@ngx-translate/core';
import { MobileApiService } from '../services/API/api.service';
import { faArrowRight, faCircleInfo, faGlobe, faLink, faPen, faShieldHalved } from '@fortawesome/free-solid-svg-icons';
import { FaIconComponent } from '@fortawesome/angular-fontawesome';
import { NgClass } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-mobile-zero-totp-tenant-selector',
  imports: [TranslatePipe, FaIconComponent, NgClass, FormsModule],
  templateUrl: './mobile-zero-totp-tenant-selector.component.html',
  styleUrl: './mobile-zero-totp-tenant-selector.component.css',
})
export class MobileZeroTotpTenantSelectorComponent implements OnInit{
  //DI
  apiService = inject(MobileApiService)
  persistentStorage = inject(CapacitorPersistentStorageService)
  translate = inject(TranslateService)

  // icons
  faArrowRight = faArrowRight
  faCircleInfo = faCircleInfo
  faLink = faLink
  faShieldHalved = faShieldHalved
  faGlobe = faGlobe
  faPen = faPen


  //signals
  current_domain = signal('');
  tenant_modal_active = signal(false)
  tenant_modal_error = signal("")
  tenant_modal_loading = signal(false)
  tenant_modal_apiBaseURL_input = signal("")

  ngOnInit(): void {
    const baseURL = new URL(this.apiService.baseURL)
    this.current_domain.set(baseURL.host)
  }


  zero_totp_tenant_button_click() {
      this.tenant_modal_active.update(v => !v);
  }

  validateNewAPIBaseURL() {
    this.tenant_modal_error.set("")
    this.tenant_modal_loading.set(true)
    this.persistentStorage.setAPIBaseURL(this.tenant_modal_apiBaseURL_input()).then(_ => {
      this.apiService.updateBaseURL().then(success => {
        this.tenant_modal_loading.set(false)
        if (success) {
          this.tenant_modal_active.set(false)
          const baseURL = new URL(this.apiService.baseURL)
          this.current_domain.set(baseURL.host)
        } else {
          this.translate.get("general_error").subscribe(t => {
            this.tenant_modal_error.set(t)
          })
        }
      })
    }).catch(error => {
      console.log(error)
      this.translate.get("invalid_url").subscribe(t => {
        this.tenant_modal_error.set(t)
      })
    })
  }

}
