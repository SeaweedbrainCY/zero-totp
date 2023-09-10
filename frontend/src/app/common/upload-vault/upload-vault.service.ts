import { SecurityContext,Injectable } from '@angular/core';
import { Crypto } from '../Crypto/crypto';
import { DomSanitizer } from '@angular/platform-browser';





export enum UploadVaultStatus {
  SUCCESS = 0,
  INVALID_JSON = 1,
  INVALID_VERSION = 2,
  NO_SIGNATURE = 3,
  INVALID_SIGNATURE = 4,
  MISSING_ARGUMENT = 5,
  INVALID_ARGUMENT = 6,
  UNKNOWN = 7
}

@Injectable({
  providedIn: 'root'
})
export class UploadVaultService {

  constructor(
    private sanitizer: DomSanitizer,
    private crypto: Crypto
  ) { }

  parseUploadedVault(unsecure_context_b64:string): Promise<[(Map<string, string> | null), UploadVaultStatus]> {
    return new Promise<[(Map<string, string> | null), UploadVaultStatus]>((resolve) => {
    let vault = new Map<string, string>();
    try{
      if(unsecure_context_b64.split(",").length != 2){
        resolve([null, UploadVaultStatus.NO_SIGNATURE]);
      }
      unsecure_context_b64 = unsecure_context_b64.replace('"', '')
      const unsecure_vault_b64 = unsecure_context_b64.split(",")[0];
      const signature = unsecure_context_b64.split(",")[1];
      let unsecure_vault = atob(unsecure_vault_b64);
      let context = JSON.parse(unsecure_vault);
      if(context == null){
        resolve([null, UploadVaultStatus.INVALID_JSON]);
      }
      if(context.hasOwnProperty("version")){
        if(context.version == 1){
          const required_keys = ["version", "date", "derived_key_salt", "zke_key_enc", "secrets"]
          for(let key of required_keys){
            if(context.hasOwnProperty(key)){

              const sanitized = this.sanitizer.sanitize(SecurityContext.HTML, context[key])
              if(sanitized != null){
                      vault.set(key, sanitized);
              }else {
                resolve([null,UploadVaultStatus.INVALID_ARGUMENT]);
              }
            } else {
              resolve([null,UploadVaultStatus.MISSING_ARGUMENT]);
            }
          }
           this.crypto.verifySignature(unsecure_vault_b64, signature).then(result => {
            if(result){
             resolve([vault, UploadVaultStatus.SUCCESS]);
             } else {
                resolve([null,UploadVaultStatus.INVALID_SIGNATURE]);
              }
            });
        } else {
          resolve([null,UploadVaultStatus.INVALID_VERSION]);
        }
      } else {
        resolve([null,UploadVaultStatus.INVALID_VERSION]);
      }
    } 
    catch(e){
      console.log(e)
      resolve([null,UploadVaultStatus.INVALID_JSON]);
    }
  });
}
}


