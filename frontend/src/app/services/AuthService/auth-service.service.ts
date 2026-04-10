import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class AuthServiceService {

  constructor(
    private http: HttpClient
  ) { }

  refreshToken() {
    return this.http.put('/api/v1/auth/refresh', {},{withCredentials: true, observe: 'response'});
  }
}
