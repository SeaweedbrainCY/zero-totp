import { Injectable } from '@angular/core';
import { Utils }  from '../Utils/utils';
import { LocalVaultV1Service } from '../upload-vault/LocalVaultv1Service.service';
import { HttpClient } from '@angular/common/http';
@Injectable({providedIn: 'root'}) //Note that you will need to declare it as `@Injectable`. 

@Injectable({
  providedIn: 'root'
})
export class UserService {
  private id:number| null =null;;
  private email:string| null =null;;
  private zke_key:CryptoKey| null =null;;
  private derivedKeySalt: string| null =null;;
  private vault:Map<string, Map<string,string>> | null =null;
  private passphraseSalt: string| null =null;;
  private isVaultLocal:boolean = false;
  private local_vault_service:LocalVaultV1Service | null = null;
  private googleDriveSync:boolean | null = null;
  private vault_tags:string[] = [];

  constructor(
    private utils: Utils,
    private http: HttpClient
  ) {
   }

   refresh_user_id(): Promise<Boolean> {
    return new Promise((resolve, reject) => {
      this.http.get('/api/v1/whoami', {withCredentials:true, observe: 'response'}).subscribe({
        next: (response) => {
          if (response.status === 200) {
            const userData = response.body as { id: number, email: string, username: string };
            this.setId(userData.id);
            this.setEmail(userData.email);
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

   getId() : number | null {
    return this.id;
   }

   setId(id:number){
    this.id = id;
   }

   getEmail() : string | null{
    return this.utils.sanitize(this.email);
   }

   setEmail(email:string){
    this.email = this.utils.sanitize(email);
   }

   get_zke_key() : CryptoKey | null{
    return this.zke_key;
   }

   set_zke_key(zke_key:CryptoKey){
    this.zke_key = zke_key;
   }

   getDerivedKeySalt(): string | null {
    return this.derivedKeySalt;
   }

   setDerivedKeySalt(salt:string){
    this.derivedKeySalt = salt;
   }

   getVault(): Map<string, Map<string,string>>| null {
    return this.vault;
   }

   setVault(vault:Map<string, Map<string,string>>){
    this.vault = vault;
   }

    getPassphraseSalt(): string | null {
    return this.passphraseSalt;
    }

    setPassphraseSalt(salt:string){
    this.passphraseSalt = salt;
    }

    getIsVaultLocal(): boolean {
      return this.isVaultLocal;
    }

    setVaultLocal(isLocal:boolean){
      this.isVaultLocal = isLocal;
    }

    getLocalVaultService(): LocalVaultV1Service | null {
      return this.local_vault_service;
    }

    setLocalVaultService(service:LocalVaultV1Service){
      this.local_vault_service = service;
    }



    getGoogleDriveSync(): boolean | null {
    return this.googleDriveSync;
    }

    setGoogleDriveSync(sync:boolean){
    this.googleDriveSync = sync;
    }

    getVaultTags(): string[]  {
      return this.vault_tags;
    }

    setVaultTags(tags:string[]){
      this.vault_tags = tags;
    }


   clear(){
    this.id = null;
    this.email = null;
    this.zke_key = null;
    this.derivedKeySalt = null;
    this.vault = null;
    this.passphraseSalt = null;
    this.isVaultLocal = false;
    this.local_vault_service = null;
    this.googleDriveSync = null;
    this.vault_tags = [];
    localStorage.removeItem("email");
   }

   clearVault(){
    this.vault = null;
    this.zke_key = null;
    this.derivedKeySalt = null;
    this.passphraseSalt = null;
    this.isVaultLocal = false;
    
   }

}
