import { Component, inject, OnInit, signal } from '@angular/core';
import { UserService } from 'src/shared/Services/User/user.service';
import { formatDate } from '@angular/common';
import { LocalVaultV1Service } from 'src/shared/Services/upload-vault/LocalVaultv1Service.service';
import { VaultService } from 'src/shared/Services/VaultService/vault.service';
import { TranslateService, TranslatePipe } from '@ngx-translate/core';
import { ToastService } from '../../../shared/Services/Toast/toast.service';
import { VaultViewComponent } from 'src/shared/Views/vault-view/vault-view.component';
import { Router } from '@angular/router';

@Component({
  selector: 'app-rescue-vault',
  imports: [TranslatePipe, VaultViewComponent],
  templateUrl: './rescue-vault.component.html',
  styleUrl: './rescue-vault.component.css',
})
export class RescueVaultComponent implements OnInit {
  // DI
  userService = inject(UserService);
  vaultService = inject(VaultService);
  translate = inject(TranslateService);
  toast = inject(ToastService);
  router = inject(Router)

  local_vault_service: LocalVaultV1Service | null = null;

  // signals
  vault_date = signal('');
  isVaultLoading = signal(false);

  constructor() {}

  ngOnInit(): void {
    if (this.userService.zke_key() == null) {
      console.log("her")
      this.router.navigate(["/open-vault"]);
    } else {
     this.loadVault()
    }
  }


  loadVault(){
    this.local_vault_service = this.userService.local_vault_service();
    let vaultDate = 'unknown';
    try {
      const vaultDateStr = this.local_vault_service!.get_date()!.split('.')[0];
      vaultDate = String(
        formatDate(new Date(vaultDateStr), 'dd/MM/yyyy HH:mm:ss O', 'en'),
      );
    } catch {
      vaultDate = 'error';
    }

    this.vault_date.set(vaultDate);
    this.isVaultLoading.set(true);
    this.vaultService
      .decryptVault(
        this.local_vault_service!.get_enc_secrets()!,
        this.userService.zke_key()!,
      )
      .then(
        (result) => {
          this.isVaultLoading.set(false);
          if (result.errors.length != 0) {
            this.translate
              .get('vault.error.decryption')
              .subscribe((translation: string) => {
                this.toast.error(translation, result.errors.join('. '));
              });
          }
          this.userService.vault.set(result.vault);
          this.userService.is_vault_in_memory = true;
        },
        (error) => {
          this.isVaultLoading.set(false);
          this.translate
            .get('vault.error.decryption')
            .subscribe((translation: string) => {
              this.toast.error(translation, error);
            });
        },
      );
    }
}
