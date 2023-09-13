import { Injectable } from '@angular/core';
import { Utils }  from '../Utils/utils';
import { LocalVaultV1Service } from '../upload-vault/LocalVaultv1Service.service';
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
<<<<<<< HEAD
  private isVaultLocal:boolean = false;
  private local_vault_service:LocalVaultV1Service | null = null;
=======
>>>>>>> 78f553f023155a4bfb6c29e2a781091694a9dc0f
  private googleDriveSync:boolean | null = null;;

  constructor(private utils: Utils) {
   }

   getId() : number | null {
    return this.id;
   }

   setId(id:number){
    this.id = id;
   }

   getEmail() : string | null{
    if(this.email == null){
      this.email = localStorage.getItem("email") || null;
    }
    return this.utils.sanitize(this.email);;
   }

   setEmail(email:string){
    this.email = this.utils.sanitize(email);
    if(this.email != null){
      localStorage.setItem("email", this.email)
    }
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

<<<<<<< HEAD
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



=======
>>>>>>> 78f553f023155a4bfb6c29e2a781091694a9dc0f
    getGoogleDriveSync(): boolean | null {
    return this.googleDriveSync;
    }

    setGoogleDriveSync(sync:boolean){
    this.googleDriveSync = sync;
    }

   clear(){
    this.id = null;
    this.email = null;
    this.zke_key = null;
    this.derivedKeySalt = null;
    this.vault = null;
    this.passphraseSalt = null;
    localStorage.clear();
   }

}
