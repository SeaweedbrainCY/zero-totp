import { Injectable } from '@angular/core';
import { iOSSecureStorage } from 'src/capacitor/plugins/ios-secure-storage.plugin';
import { Buffer } from 'buffer';

enum ProtectedKeychainStorageKey {
  USER_ZKE_KEY_BASE_STORAGE_KEY = "user_zke_key"
}

@Injectable({
  providedIn: 'root',
})
export class ProtectedKeychainStorageService {
  public async storeZKEKey(zkeKey: CryptoKey) {
    try {
      const zkeKeyRaw = await window.crypto.subtle.exportKey("raw", zkeKey)
      const zkeKeyB64 = Buffer.from(zkeKeyRaw).toString('base64');
      await iOSSecureStorage.setProtected({
        key: ProtectedKeychainStorageKey.USER_ZKE_KEY_BASE_STORAGE_KEY,
        value: zkeKeyB64
      })
    } catch {
      console.log("An error occured while storing ZKE key in keychain. The error is not logged to avoid leaking authentication tokens.")
      return
    }
  }

  public async getZKEKey(): Promise<CryptoKey | null> {
    try {
      const { value } = await iOSSecureStorage.getProtected({ key: ProtectedKeychainStorageKey.USER_ZKE_KEY_BASE_STORAGE_KEY, prompt: "Unlock your vault" })
      if (value == null) {
        console.log("Tried to retrieve zke key but value was null")
        return null
      }
      const zkeKeyRaw = Buffer.from(value, 'base64');
      const zkeKey = await window.crypto.subtle.importKey(
        "raw",
        zkeKeyRaw,
        "AES-GCM",
        true,
        ["encrypt", "decrypt"]
      )
      return zkeKey
    } catch (e) {
      console.log("An error occured while retrieving ZKE key in keychain." + e)
      return null
    }
  }

  public async deleteZKEKey(): Promise<void> {
    await iOSSecureStorage.remove({ key: ProtectedKeychainStorageKey.USER_ZKE_KEY_BASE_STORAGE_KEY })
  }
}