import { Injectable } from '@angular/core';
import { Preferences } from '@capacitor/preferences';


enum PersistentStorageKey {
  API_BASE_URL_KEY = "api_base_url",
  BIOMETRICS_PROTECTION_ENABLED = "biometrics_protection_enabled"
}

@Injectable({
  providedIn: 'root',
})
export class CapacitorPersistentStorageService {

  // ***************
  // Base URL 
  // ***************
  async setAPIBaseURL(url: string) {
    const withProtocol = /^https?:\/\//i.test(url)
      ? url
      : `https://${url}`;


    const host = new URL(withProtocol).host;
    await Preferences.set({
      key: PersistentStorageKey.API_BASE_URL_KEY,
      value: host,
    });
  }

  async getAPIBaseURL(): Promise<string> {
    return (await Preferences.get({ key: PersistentStorageKey.API_BASE_URL_KEY })).value ?? ""
  }

  // ***************
  // Biometrics protection preference
  // ***************

  async isBiometricsProtectionEnabled(user_id: number): Promise<boolean | null> {
    const setting_key = user_id.toString() + "_" + PersistentStorageKey.BIOMETRICS_PROTECTION_ENABLED
    const setting = (await Preferences.get({ key: setting_key })).value
    if (setting == null) {
      return null
    }

    return setting == "true"
  }

  async setBriometricProtection(user_id: number, enabled: boolean) {
    let setting = "true"
    if (!enabled) {
      setting = "false"
    }

    const setting_key = user_id.toString() + "_" + PersistentStorageKey.BIOMETRICS_PROTECTION_ENABLED
    await Preferences.set({
      key: setting_key,
      value: setting,
    });
  }

  async deleteBiometricProtectionPreference(user_id: number) {
    const setting_key = user_id.toString() + "_" + PersistentStorageKey.BIOMETRICS_PROTECTION_ENABLED
    await Preferences.remove({ key: setting_key })
  }

}
