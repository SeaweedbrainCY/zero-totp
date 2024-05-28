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
export class LocalVaultV1Service {

  version = 1;
  date: string | null = null;
  derived_key_salt: string | null = null;
  zke_key_enc: string | null = null;
  enc_secrets: Map<string, string> | null = null;
  is_signature_valid: boolean = false;



  constructor(
    private sanitizer: DomSanitizer,
    private crypto: Crypto
  ) { }

  extract_version_from_vault(unsecure_context_b64:string): number | null {
    unsecure_context_b64 = unsecure_context_b64.replace('"', '')// nosemgrep
    const unsecure_vault_b64 = unsecure_context_b64.split(",")[0];
    let unsecure_vault = atob(unsecure_vault_b64);
    let context = JSON.parse(unsecure_vault);
    if(context.hasOwnProperty("version")){
      return context.version;
    } else {
      return null 
    }
    
  }

  parseUploadedVault(unsecure_context_b64:string): Promise< UploadVaultStatus> {
    return new Promise< UploadVaultStatus>((resolve) => {
      try{
      if(unsecure_context_b64.split(",").length != 2){
        resolve( UploadVaultStatus.NO_SIGNATURE);
      }
      unsecure_context_b64 = unsecure_context_b64.replace('"', '') // nosemgrep
      const unsecure_vault_b64 = unsecure_context_b64.split(",")[0];
      const signature = unsecure_context_b64.split(",")[1];
      let unsecure_vault = atob(unsecure_vault_b64);
      let context = JSON.parse(unsecure_vault);
      if(context == null){
        resolve( UploadVaultStatus.INVALID_JSON);
      }
      if(context.hasOwnProperty("version")){
        if(context.version == 1){
          const required_keys = ["version", "date", "derived_key_salt", "zke_key_enc", "secrets"]
          let enc_secrets = Array();
          for(let key of required_keys){
            if(context.hasOwnProperty(key)){
              if(key == "secrets"){
                for(let secret of context[key]){
                  if(secret.hasOwnProperty("uuid") && secret.hasOwnProperty("enc_secret")){
                    const sanitized_uuid = this.sanitizer.sanitize(SecurityContext.HTML, secret.uuid)
                    const sanitized_enc_secret = this.sanitizer.sanitize(SecurityContext.HTML, secret.enc_secret)
                    if(sanitized_uuid != null && sanitized_enc_secret != null){
                      secret.uuid = sanitized_uuid;
                      secret.enc_secret = sanitized_enc_secret;
                      enc_secrets.push(secret)
                  } else {
                    resolve(UploadVaultStatus.INVALID_ARGUMENT);
                  }
                }
              }
            } else {
              const sanitized = this.sanitizer.sanitize(SecurityContext.HTML, context[key])
              if(sanitized != null){
                 context[key]= sanitized;
              }else {
                resolve(UploadVaultStatus.INVALID_ARGUMENT);
              }
            }
            } else {
              resolve(UploadVaultStatus.MISSING_ARGUMENT);
          }
          }
          this.version = context.version;
          this.date = context.date;
          this.derived_key_salt = context.derived_key_salt;
          this.zke_key_enc = context.zke_key_enc;
          this.enc_secrets = context.secrets;
           this.crypto.verifySignature(unsecure_vault_b64, signature).then(result => {
            if(result){
              this.is_signature_valid = true;
             resolve(UploadVaultStatus.SUCCESS);
             } else {
                resolve(UploadVaultStatus.INVALID_SIGNATURE);
              }
            });
        } else {
          resolve(UploadVaultStatus.INVALID_VERSION);
        }
      } else {
        resolve(UploadVaultStatus.INVALID_VERSION);
      }
    } 
    catch(e){
      console.log(e)
      resolve(UploadVaultStatus.INVALID_JSON);
    }
  });
}

  get_version(): number {
    return this.version;
  }

  get_date(): string | null {
    return this.date;
  }

  get_derived_key_salt(): string | null {
    return this.derived_key_salt;
  }

  get_zke_key_enc(): string | null {
    return this.zke_key_enc;
  }

  get_enc_secrets(): Map<string, string> | null {
    return this.enc_secrets;
  }

  get_is_signature_valid(): boolean {
    return this.is_signature_valid;
  }

  set_is_signature_valid(is_valid: boolean) {
    this.is_signature_valid = is_valid;
  }
}


