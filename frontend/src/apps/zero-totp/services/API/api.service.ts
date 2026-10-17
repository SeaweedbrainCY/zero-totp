import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';
import { CapacitorPersistentStorageService } from '../Capacitor/persistentStorage/capacitor-persistent-storage.service';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  public baseURL: string;

  constructor(
    private persistentStorage: CapacitorPersistentStorageService
  ) {
    this.baseURL = ""
    this.updateBaseURL()
  }

  public async updateBaseURL(): Promise<boolean> {
    if (environment.isMobileApp) {
      this.baseURL = "https://zero-totp.com"
      let apiBaseURL = await this.persistentStorage.getAPIBaseURL()
      if (apiBaseURL != "") {
        this.baseURL = "https://" + apiBaseURL
        return true
      }
      return false
    } else {
      this.baseURL = "" // Use the global base URL for the webapp
      return true
    }
  }
}