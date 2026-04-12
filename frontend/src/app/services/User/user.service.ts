import { Injectable, WritableSignal, signal } from '@angular/core';
import { LocalVaultV1Service } from '../upload-vault/LocalVaultv1Service.service';
import { HttpClient } from '@angular/common/http';
@Injectable({providedIn: 'root'})

@Injectable({
  providedIn: 'root'
})
export class UserService {
  public id:  WritableSignal<number| null> = signal(null);
  public email: WritableSignal<string| null> = signal(null);
  public zke_key: WritableSignal<CryptoKey| null> = signal(null);
  public derivedKeySalt: WritableSignal<string| null> = signal(null);
  public vault: WritableSignal<Map<string, Map<string,string>> | null> = signal(null);
  public passphraseSalt: WritableSignal<string| null> = signal(null);
  public isVaultLocal: WritableSignal<boolean> = signal(false);
  public local_vault_service: WritableSignal<LocalVaultV1Service | null> = signal(null);
  public googleDriveSync: WritableSignal<boolean | null> = signal(null);
  public vault_tags: WritableSignal<string[]> = signal([]);

  constructor(
    private http: HttpClient
  ) {
   }

   refresh_user_id(): Promise<Boolean> {
    return new Promise((resolve, reject) => {
      this.http.get('/api/v1/whoami', {withCredentials:true, observe: 'response'}).subscribe({
        next: (response) => {
          if (response.status === 200) {
            const userData = response.body as { id: number, email: string, username: string };
            this.id.set(userData.id);
            this.email.set(userData.email);
            localStorage.setItem("email", userData.email);
            resolve(true);
          } else {
            console.error('Failed to fetch user data:', response.statusText);
            resolve(false);
          }
        },
        error: (error) => {
          console.error('Error fetching user data:', error);
          reject(false);
        }
      });
    });
   }

   // Check if the vault is loaded and can be decrypted. If not, the user will have to import a local one or provide their passphrase to decrypt it
   isVaultLoadedAndDecryptable() : boolean {
    return this.isVaultLocal() && this.zke_key != null
   }

   isUserLoggedIn():boolean {
    if (this.id() != null) {
      return true
    }
    this.refresh_user_id().then(()=>{
        return true
      }, (error)=>{
        return false
      })
      return false
   }

   clear(){
    this.id.set(null);
    this.email.set(null);
    this.zke_key .set(null);
    this.derivedKeySalt.set(null);
    this.vault.set(null);
    this.passphraseSalt.set(null);
    this.isVaultLocal.set(false);
    this.local_vault_service.set(null);
    this.googleDriveSync.set(null);
    this.vault_tags.set([]);
    localStorage.removeItem("email");
   }

   clearVault(){
    this.vault.set(null);
    this.zke_key.set(null);
    this.derivedKeySalt.set(null);
    this.passphraseSalt.set(null);
    this.isVaultLocal.set(false);
    
   }

}
