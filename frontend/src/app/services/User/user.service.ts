import { Injectable, WritableSignal, signal } from '@angular/core';
import { LocalVaultV1Service } from '../upload-vault/LocalVaultv1Service.service';
import { HttpClient } from '@angular/common/http';

export interface TOTPEntry {
  name: string;
  uri: string;
  secret: string;
  color: string;
  favicon: boolean;
  tags: string[];
}
const VALID_COLORS = new Set(['success', 'danger', 'info', 'warning']);


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

  constructor(
    private http: HttpClient
  ) {
  }

  refresh_user_id(): Promise<Boolean> {
    return new Promise((resolve, reject) => {
      this.http.get('/api/v1/whoami', { withCredentials: true, observe: 'response' }).subscribe({
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
}
