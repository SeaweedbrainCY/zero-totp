import { SecurityContext, Sanitizer,Injectable } from '@angular/core';
import { Crypto } from '../Crypto/crypto';




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
    private sanitizer: Sanitizer,
    private crypto: Crypto
  ) { }

  parseUploadedVault(unsecure_context_b64:string): [(Map<string, string> | null), UploadVaultStatus] {
    let vault = new Map<string, string>();
    try{
      if(unsecure_context_b64.split(",").length != 2){
        return [null, UploadVaultStatus.NO_SIGNATURE];
      }
      const unsecure_vault_b64 = unsecure_context_b64.split(",")[0];
      const signature = unsecure_context_b64.split(",")[1];
      let unsecure_vault = atob(unsecure_vault_b64);
      let context = JSON.parse(unsecure_vault);
      if(context == null){
        return [null, UploadVaultStatus.INVALID_JSON];
      }
      if(context.hasOwnProperty("version")){
        if(context.version == 1){
          const required_keys = ["version", "date", "derived_key_salt", "zke_key_enc", "secrets"]
          for(let key of required_keys){
            if(context.hasOwnProperty(key)){
              const sanitized = this.sanitizer.sanitize(SecurityContext.HTML, context[key])
              if(sanitized != null){
                this.crypto.verifySignature(unsecure_vault_b64, signature).then((result) => {
                  if(result){
                      vault.set(key, sanitized);
                      return vault;
                  } else {
                    return [null,UploadVaultStatus.INVALID_SIGNATURE];
                  }
                });
              }else {
                return [null,UploadVaultStatus.INVALID_ARGUMENT];
              }
            } else {
              return [null,UploadVaultStatus.MISSING_ARGUMENT];
            }
          }
          return [vault, UploadVaultStatus.SUCCESS];
        } else {
          return [null,UploadVaultStatus.INVALID_VERSION];
        }
      } else {
        return [null,UploadVaultStatus.INVALID_VERSION];
      }
    } 
    catch(e){
      return [null,UploadVaultStatus.INVALID_JSON];
    }
  }
  
}


