import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';



@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private refreshTokenUrl = '/auth/refresh'; // URL de l'API pour rafraîchir le token

  constructor(
    private http: HttpClient
  ) { }

  refreshToken(): Observable<any> {
    return this.http.post(this.refreshTokenUrl, {},  {withCredentials: true, observe: 'response'});
  }
 

}
