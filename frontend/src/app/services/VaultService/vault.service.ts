import { Injectable } from '@angular/core';
import { Crypto } from '../../common/Crypto/crypto';
import { TranslateService } from '@ngx-translate/core';
import { Utils } from '../../common/Utils/utils';
import { Buffer } from 'buffer';
import { TOTPEntry, UserService } from '../User/user.service';



export interface DecryptedVaultResult {
  vault: Map<string, TOTPEntry>;
  errors: string[];
}


@Injectable({
  providedIn: 'root'
})
export class VaultService {

  vault: Map<string, Map<string, string>> | null = null;

  constructor(
    private crypto: Crypto,
    private translate: TranslateService,
    private utils: Utils,
    private userServive: UserService,
  ) { }

  decryptZKEKey(zke_key_encrypted: string, derivedKey: CryptoKey, isVaultLocal: Boolean = false): Promise<CryptoKey> {
    return new Promise((resolve, reject) => {
      this.crypto.decrypt(zke_key_encrypted, derivedKey).then(zke_key_b64 => {
        if (zke_key_b64 != null) {
          const zke_key_raw = Buffer.from(zke_key_b64!, 'base64');

          window.crypto.subtle.importKey(
            "raw",
            zke_key_raw,
            "AES-GCM",
            true,
            ["encrypt", "decrypt"]
          ).then((zke_key) => {
            resolve(zke_key);
          }, (error) => {
            this.translate.get("login.errors.import_vault.key_dec").subscribe((translation) => {
              reject(translation + " " + error);
            });
          });;
        } else {
          if (isVaultLocal) {
            this.translate.get("login.errors.import_vault.wrong_passphrase").subscribe((translation) => {
              reject(translation);
            });
          } else {
            this.translate.get("login.errors.import_vault.key_dec").subscribe((translation) => {
              reject(translation);
            });
          }

        }

      });
    });
  }

  derivePassphrase(derivedKeySalt: string, passphrase: string): Promise<CryptoKey> {
    return new Promise((resolve, reject) => {
      if (derivedKeySalt != null) {
        this.crypto.deriveKey(derivedKeySalt, passphrase).then(key => {
          resolve(key);
        });
      } else {
        reject("Impossible to retrieve enough data to decrypt your vault");
      }
    });
  }

  decryptVault(encrypted_vault: Array<Map<string, string>>, zke_key: CryptoKey): Promise<DecryptedVaultResult> {
    return new Promise((resolve, reject) => {
      let decrypted_vault = new Map<string, TOTPEntry>();

      let errors: string[] = []
      const fakeProperty: TOTPEntry = {
        color: "info",
        name: "Error",
        secret: "",
        favicon: false,
        uri: "",
        tags: []
      }

      const promises = encrypted_vault.map((secret) => {
        const uuid = secret.get("uuid");
        const enc_secret = secret.get("enc_secret");
        if (uuid != null) {
          if (enc_secret != null) {
            this.crypto.decrypt(enc_secret, zke_key).then((dec_secret) => {
              if (dec_secret != null) {
                decrypted_vault.set(uuid, this.userServive.TOTPEntryFromJSON(dec_secret))
              } else {
                decrypted_vault.set(uuid, fakeProperty);
                errors.push("Decrypted secret null.")
              }
            }, (error) => {
              decrypted_vault.set(uuid, fakeProperty);
              errors.push(error)
            });
          } else {
            decrypted_vault.set(uuid, fakeProperty);
          }
        }
      })

      Promise.all(promises)
        .then(() => {
          resolve({
            vault: decrypted_vault,
            errors: errors
          })
        })
        .catch((error) => reject(error));
    });
  }



}
