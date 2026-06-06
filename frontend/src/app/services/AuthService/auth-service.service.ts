import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ApiService } from '../API/api.service';
import { signal } from '@angular/core';
import { iOSSecureStorage } from 'src/capacitor/plugins/ios-secure-storage.plugin';
import { Buffer } from 'buffer';

export interface AuthToken {
  domain: string,
  session_token: string,
  refresh_token: string,
}

const AUTH_TOKEN_STORAGE_KEY = "app.zero-totp.auth-token"
@Injectable({
  providedIn: 'root'
})



export class AuthServiceService {


  private readonly _auth_token = signal<AuthToken | null>(null);
  readonly auth_token = this._auth_token.asReadonly();

  constructor(
    private http: HttpClient,
    private apiService: ApiService
  ) { }

  refreshToken() {
    return this.http.put(this.apiService.baseURL + '/api/v1/auth/refresh', {}, { withCredentials: true, observe: 'response' });
  }

  // Called once at app init (e.g. APP_INITIALIZER)
  async loadTokenFromKeychain(): Promise<void> {
    const { value } = await iOSSecureStorage.get({ key: AUTH_TOKEN_STORAGE_KEY })
    if (value == null) {
      return;
    }
    try {
      this._auth_token.set(JSON.parse(value) as AuthToken)
    } catch {
      console.log("An error occured while parsing auth token stored in keychain. The error is not logged to avoid leaking authentication tokens.")
    }
  }

  async setToken(authToken: AuthToken): Promise<void> {
    this._auth_token.set(authToken)
    try {
      const authTokenStr = JSON.stringify(authToken)
      await iOSSecureStorage.set({
        key: AUTH_TOKEN_STORAGE_KEY,
        value: authTokenStr
      })
    } catch {
      console.log("An error occured while stringifying auth token stored in keychain. The error is not logged to avoid leaking authentication tokens.")
      return
    }
  }

  async clearToken(): Promise<void> {
    this._auth_token.set(null);
    await iOSSecureStorage.remove({ key: AUTH_TOKEN_STORAGE_KEY })
  }
}
