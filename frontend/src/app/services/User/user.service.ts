import { Injectable, WritableSignal, signal } from '@angular/core';
import { LocalVaultV1Service } from '../upload-vault/LocalVaultv1Service.service';
import { HttpClient } from '@angular/common/http';
import { ApiService } from '../API/api.service';

import { Crypto } from '../../common/Crypto/crypto';
import { TranslateService } from '@ngx-translate/core';
import { Buffer } from 'buffer';


export interface TOTPEntry {
  name: string;
  uri: string;
  secret: string;
  color: string;
  favicon: boolean;
  tags: string[];
}

export interface getZKEKeyResult {
  derivedKeySalt: string;
  zkeKey: CryptoKey;
}

const VALID_COLORS = new Set(['success', 'danger', 'info', 'warning']);

export enum CommonError {
  UserNeedToLoginAgain = "Please login again."
}

@Injectable({ providedIn: 'root' })
export class UserService {



  public id: WritableSignal<number | null> = signal(null);
  public email: WritableSignal<string | null> = signal(null);
  public zke_key: WritableSignal<CryptoKey | null> = signal(null);
  public derivedKeySalt: WritableSignal<string | null> = signal(null);
  public vault: WritableSignal<Map<string, TOTPEntry>> = signal(new Map<string, TOTPEntry>());
  public passphraseSalt: WritableSignal<string | null> = signal(null);
  public isVaultLocal: WritableSignal<boolean> = signal(false);
  public local_vault_service: WritableSignal<LocalVaultV1Service | null> = signal(null);
  public googleDriveSync: WritableSignal<boolean | null> = signal(null);
  public vault_tags: WritableSignal<string[]> = signal([]);

  public is_vault_in_memory: boolean = false;

  constructor(
    private http: HttpClient,
    private crypto: Crypto,
    private translate: TranslateService,,
    private apiService: ApiService
  ) {
  }

  refresh_user_id(): Promise<Boolean> {
    return new Promise((resolve, reject) => {
      this.http.get(this.apiService.baseURL + '/api/v1/whoami', { withCredentials: true, observe: 'response' }).subscribe({
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
  isVaultLoadedAndDecryptable(): boolean {
    return this.isVaultLocal() && this.zke_key != null
  }

  isUserLoggedIn(): boolean {
    if (this.id() != null) {
      return true
    }
    this.refresh_user_id().then(() => {
      return true
    }, (error) => {
      return false
    })
    return false
  }

  clear() {
    this.id.set(null);
    this.email.set(null);
    this.zke_key.set(null);
    this.derivedKeySalt.set(null);
    this.vault.set(new Map<string, TOTPEntry>());
    this.passphraseSalt.set(null);
    this.isVaultLocal.set(false);
    this.local_vault_service.set(null);
    this.googleDriveSync.set(null);
    this.vault_tags.set([]);
    localStorage.removeItem("email");
  }

  clearVault() {
    this.vault.set(new Map<string, TOTPEntry>());
    this.zke_key.set(null);
    this.derivedKeySalt.set(null);
    this.passphraseSalt.set(null);
    this.isVaultLocal.set(false);

  }

  TOTPEntryToJSON(entry: TOTPEntry): string {
    return JSON.stringify(entry)
  }

  TOTPEntryFromJSON(jsonEntry: string): TOTPEntry {
    const totpEntryDefault: TOTPEntry = {
      name: 'Error',
      uri: '',
      secret: '',
      color: 'info',
      favicon: false,
      tags: [],
    };

    let raw: unknown;

    try {
      raw = JSON.parse(jsonEntry);
    } catch {
      return totpEntryDefault;
    }

    if (typeof raw !== 'object' || raw === null || Array.isArray(raw)) {
      return totpEntryDefault
    }

    const r = raw as Record<string, unknown>;

    return {
      name: typeof r['name'] === 'string' ? r['name'] : totpEntryDefault.name,
      uri: typeof r['uri'] === 'string' ? r['uri'] : totpEntryDefault.uri,
      secret: typeof r['secret'] === 'string' ? r['secret'] : totpEntryDefault.secret,
      color: VALID_COLORS.has(r['color'] as string)
        ? r['color'] as TOTPEntry['color']
        : totpEntryDefault.color,
      favicon: typeof r['favicon'] === 'boolean' ? r['favicon'] : totpEntryDefault.favicon,
      tags: Array.isArray(r['tags']) && r['tags'].every(t => typeof t === 'string')
        ? r['tags']
        : totpEntryDefault.tags,
    };
  }

  getUserEncryptedVault(): Promise<Array<Map<string, string>>> {
    return new Promise<Array<Map<string, string>>>((resolve, reject) => {
      this.http.get("/api/v1/all_secrets", { withCredentials: true, observe: 'response' }).subscribe({
        next: (response) => {
          const data = JSON.parse(JSON.stringify(response.body))
          let encrypted_secret_vault = new Array<Map<string, string>>();
          for (let secret of data.enc_secrets) {
            let secret_map = new Map<string, string>();
            secret_map.set("uuid", secret.uuid);
            secret_map.set("enc_secret", secret.enc_secret);
            encrypted_secret_vault.push(secret_map);
          }
          resolve(encrypted_secret_vault)
        },
        error: (error) => {
          if (error.status == 404) {
            resolve(new Array<Map<string, string>>());
          } else {
            let errorMessage = "";
            if (error.error.message != null) {
              errorMessage = error.error.message;
            } else if (error.error.detail != null) {
              errorMessage = error.error.detail;
            }
            if (error.status == 0) {
              errorMessage = "vault.error.server_unreachable"
            }
            reject(errorMessage)
          }
          reject(error)
        }
      });
    });
  }

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


  // Returns derivedKeySalt and decrypted zke key
  getUserZKEKey(passphrase: string): Promise<getZKEKeyResult> {
    return new Promise<getZKEKeyResult>((resolve, reject) => {
      this.http.get("/api/v1/user/derived-key-salt", { withCredentials: true, observe: 'response' }).subscribe({
        next: (response) => {
          if (response.status === 200) {
            const derived_key_salt_req_data = response.body as { derived_key_salt: string };
            const derived_key_salt = derived_key_salt_req_data.derived_key_salt
            this.http.get("/api/v1/zke_encrypted_key", { withCredentials: true, observe: 'response' }).subscribe({
              next: (response) => {
                if (response.status === 200) {
                  const zke_req_data = response.body as { zke_encrypted_key: string };
                  const zke_encrypted_key = zke_req_data.zke_encrypted_key;
                  this.derivePassphrase(derived_key_salt, passphrase).then((derivedKey) => {
                    this.decryptZKEKey(zke_encrypted_key, derivedKey).then((zke_key) => {
                      resolve({
                        derivedKeySalt: derived_key_salt,
                        zkeKey: zke_key
                      })
                    }, (error) => {
                      reject("generic_errors.invalid_creds");
                    });
                  }, (error) => {
                    this.translate.get("vault.error.unlock").subscribe((translation: string) => {
                      reject(translation + " " + "U5");
                    });
                  });

                } else {
                  this.translate.get("vault.error.unlock").subscribe((translation: string) => {
                    reject(translation + " " + "U3-" + response.status);
                  });
                }

              }, error: (error) => {
                this.translate.get("vault.error.unlock").subscribe((translation: string) => {
                  reject(translation + " " + "U4");
                });

              }
            });
          } else {
            this.translate.get("vault.error.unlock").subscribe((translation: string) => {
              reject(translation + " " + "U1-" + response.status);
            });
          }
        }, error: (error) => {
          this.translate.get("vault.error.unlock").subscribe((translation: string) => {
            reject(translation + " " + "U2");
          });
        }
      })
    });
  }

  // Triggered to update the vault_tags list
  updateVaultTagsList() {
    let tags: string[] = []
    for (const properties of this.vault().values()) {
      for (const tag of properties.tags) {
        if (!tags.includes(tag)) {
          tags.push(tag)
        }
      }
    }
    this.vault_tags.set(tags)
  }

  // During login phase, the user's password is pre-hashed before being sent in the login request. 
  // This pre-hash rely on a salt returned by the API. 
  // Promise the user's hashed passphrase or reject with an error. Error can be a CommonError or a generic textual error.
  getUserPreHashedPassphrase(passphrase: string): Promise<string> {
    return new Promise<string>((resolve, reject) => {
      if (this.email() == null) {
        reject(CommonError.UserNeedToLoginAgain)
      }
      this.http.get("/api/v1/login/specs?username=" + encodeURIComponent(this.email()!), { withCredentials: true, observe: 'response' }).subscribe({
        next: (response) => {
          try {
            const data = JSON.parse(JSON.stringify(response.body))
            const salt = data.passphrase_salt as string
            this.crypto.hashPassphrase(passphrase, salt).then(hashed => {
              if (hashed != null) {
                resolve(hashed)
              } else {
                this.translate.get("login.errors.no_connection").subscribe((translation) => {
                  reject(translation)
                })
              }
            });
          } catch {
            this.translate.get("login.errors.hashing").subscribe((translation) => {
              reject(translation)
            })
          }
        }, error: error => {
          if (error.status == 429) {
            reject()
            const ban_time = error.error.ban_time || "few";
            this.translate.get("login.errors.rate_limited", { time: String(ban_time) }).subscribe((translation) => {
              reject(translation)
            });
          } else {
            this.translate.get("login.errors.no_connection").subscribe((translation) => {
              reject(error)
            });
          }
        }
      });
    })
  }
}
