import { Injectable } from '@angular/core';
import { Preferences } from '@capacitor/preferences';


enum PersistentStorageKey {
  API_BASE_URL_KEY = "api_base_url"
}

@Injectable({
  providedIn: 'root',
})
export class CapacitorPersistentStorageService {
  async setAPIBaseURL(url: string) {
    const withProtocol = /^https?:\/\//i.test(url)
      ? url
      : `https://${url}`;


    const host = new URL(withProtocol).host;
    console.log("storing " + host)
    await Preferences.set({
      key: PersistentStorageKey.API_BASE_URL_KEY,
      value: host,
    });
  }

  async getAPIBaseURL(): Promise<string> {
    return (await Preferences.get({ key: PersistentStorageKey.API_BASE_URL_KEY })).value ?? ""
  }
}
