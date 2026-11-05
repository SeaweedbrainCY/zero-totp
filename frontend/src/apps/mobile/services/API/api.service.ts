import { Injectable } from '@angular/core';
import { ApiService } from 'src/shared/Services/API/api.service';
import { CapacitorPersistentStorageService } from '../Capacitor/persistentStorage/capacitor-persistent-storage.service';

@Injectable({ providedIn: 'root' })
export class MobileApiService extends ApiService {
  public override baseURL = "";

  constructor(private persistentStorage: CapacitorPersistentStorageService) {
    super();
    this.updateBaseURL();
  }

  public async updateBaseURL(): Promise<boolean> {
    this.baseURL = "https://zero-totp.com";
    const apiBaseURL = await this.persistentStorage.getAPIBaseURL();
    if (apiBaseURL != "") {
      this.baseURL = "https://" + apiBaseURL;
      return true;
    }
    return false;
  }
}
