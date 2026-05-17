import { Injectable } from '@angular/core';
import { environment } from 'src/environments/environment';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  public baseURL: string;

  constructor() {
    if (environment.mobile) {
      this.baseURL = "https://zero-totp.com"
    } else {
      this.baseURL = "https://" + window.location.hostname
    }
  }
}
