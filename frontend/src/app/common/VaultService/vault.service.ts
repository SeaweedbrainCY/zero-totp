import { Injectable } from '@angular/core';
import { Crypto } from '../Crypto/crypto';
import { TranslateService } from '@ngx-translate/core';
import { Utils } from '../Utils/utils';
import { Buffer } from 'buffer';



export enum VaultDecryptionStatus {
  SUCCESS = 0,
  
}


@Injectable({
providedIn: 'root'
})
export class VaultService {

  vault: Map<string, Map<string, string>> | null = null;

  constructor(
    private crypto: Crypto,
    private translate: TranslateService,
    private utils: Utils
  ) { }

  decryptZKEKey(zke_key_encrypted: string, derivedKey: CryptoKey, isVaultLocal:Boolean=false): Promise<CryptoKey> {
    return new Promise((resolve, reject) => {
      this.crypto.decrypt(zke_key_encrypted, derivedKey).then(zke_key_b64=>{
        if (zke_key_b64 != null) {
          const zke_key_raw = Buffer.from(zke_key_b64!, 'base64');

          window.crypto.subtle.importKey(
            "raw",
            zke_key_raw,
            "AES-GCM",
            true,
            ["encrypt", "decrypt"]
          ).then((zke_key)=>{
            resolve(zke_key);
          }, (error)=>{
            this.translate.get("login.errors.import_vault.key_dec").subscribe((translation)=>{
            reject(translation + " " + error);
            });
          });;
        } else {
          if(isVaultLocal){
            this.translate.get("login.errors.import_vault.wrong_passphrase").subscribe((translation)=>{
              reject(translation);
            });
          } else {
            this.translate.get("login.errors.import_vault.key_dec").subscribe((translation)=>{
            reject(translation);
            });
          }
          
        }
        
      });
  });
  }

  derivePassphrase(derivedKeySalt:string, passphrase:string) : Promise<CryptoKey>{
    return new Promise((resolve, reject) => {
      if(derivedKeySalt != null){
        this.crypto.deriveKey(derivedKeySalt, passphrase).then(key=>{
          resolve(key);
        });
      } else {
        reject("Impossible to retrieve enough data to decrypt your vault");
      }
    });
  }

  decryptVault(encrypted_vault:Array<Map<string, string>>, zke_key: CryptoKey): Promise<Map<string, Map<string, string>>> {
    return new Promise((resolve, reject) => {
      
      let decrypted_vault = new Map<string, Map<string, string>>();
      for (let secret of encrypted_vault){
        const uuid = secret.get("uuid");
        const enc_secret = secret.get("enc_secret");
        if(uuid != null){
          if (enc_secret != null){
            this.crypto.decrypt(enc_secret, zke_key).then((dec_secret)=>{
              if(dec_secret != null){
                decrypted_vault.set(uuid, this.utils.mapFromJson(dec_secret));
              } else {
                let fakeProperty = new Map<string, string>();
                fakeProperty.set("color","info");
                fakeProperty.set("name", "An error occured while decrypting this secret. Decrypted secret null" );
                fakeProperty.set("secret", "");
                decrypted_vault.set(uuid, fakeProperty);
              }

            }, (error)=>{
              let fakeProperty = new Map<string, string>();
              fakeProperty.set("color","info");
              fakeProperty.set("name", "An error occured while decrypting this secret." );
              fakeProperty.set("secret", "");
              decrypted_vault.set(uuid, fakeProperty);
            });
          } else {
            let fakeProperty = new Map<string, string>();
              fakeProperty.set("color","info");
              fakeProperty.set("name", "An error occured while decrypting this secret. No secret found.");
              fakeProperty.set("secret", "");
              decrypted_vault.set(uuid, fakeProperty);
          }
        }
      }
      resolve(decrypted_vault);
    });
  }


}
