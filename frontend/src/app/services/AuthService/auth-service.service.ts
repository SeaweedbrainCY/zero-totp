import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ApiService } from '../API/api.service';

@Injectable({
  providedIn: 'root'
})
export class AuthServiceService {

  constructor(
    private http: HttpClient,
    private apiService: ApiService
  ) { }

  refreshToken() {
    return this.http.put(this.apiService.baseURL + '/api/v1/auth/refresh', {}, { withCredentials: true, observe: 'response' });
  }
}
