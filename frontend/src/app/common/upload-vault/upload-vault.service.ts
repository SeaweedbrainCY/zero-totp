import { Injectable, SecurityContext, Sanitizer } from '@angular/core';

@Injectable({
  providedIn: 'root'
})

enum UploadVaultErrors {
  INVALID_JSON = 1,
  INVALID_VERSION = 2,
  NO_SIGNATURE = 3,
  INVALID_SIGNATURE = 4,
  MISSING_ARGUMENT = 5,
  INVALID_ARGUMENT = 6,
  UNKNOWN = 7
}

export class UploadVaultService {

  constructor(
    private sanitizer: Sanitizer
  ) { }

  parseUploadedVault(unsecure_context:string): Map<string, string> | UploadVaultErrors {
    let vault = new Map<string, string>();
    try{
      let context = JSON.parse(unsecure_context);
      if(context == null){
        return UploadVaultErrors.INVALID_JSON;
      }
      if(context.hasOwnProperty("version")){
        if(context.version == 1){
          if(context.hasOwnProperty("signature")){
          const required_keys = ["version", "date", "derived_key_salt", "zke_key_enc", "secrets", "signature"]
          for(let key of required_keys){
            if(context.hasOwnProperty(key)){
              const sanitized = this.sanitizer.sanitize(SecurityContext.HTML, context[key])
              if(sanitized != null){
                vault.set(key, sanitized);
              }else {
                return UploadVaultErrors.INVALID_ARGUMENT;
              }
            } else {
              return UploadVaultErrors.MISSING_ARGUMENT;
            }
          }
          return vault;
        } else {
          return UploadVaultErrors.NO_SIGNATURE;
        }
        } else {
          return UploadVaultErrors.INVALID_VERSION;
        }
      } else {
        return UploadVaultErrors.INVALID_VERSION;
      }
    } 
    catch(e){
      return UploadVaultErrors.INVALID_JSON;
    }
  }
  verifySignature(context:string):boolean{
    
  }
}


