import { Injectable } from '@angular/core';
import {
  HttpEvent,
  HttpHandler,
  HttpInterceptor,
  HttpRequest,
  HttpErrorResponse
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';
import { AuthService } from '../AuthService/auth-service.service'; // AuthService that handles login/logout/refresh
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class AuthInterceptor implements HttpInterceptor {

  constructor(private authService: AuthService, private router: Router) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(req).pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 401) {
          // If the request failed due to 401, try refreshing the token
          return this.authService.refreshToken().pipe(
            switchMap((newToken: any) => {
              // Clone the original request and set the new token
              const clonedRequest = req.clone();
              // Retry the original request with the new token
              return next.handle(clonedRequest);
            }),
            catchError(refreshError => {
              return throwError(() => refreshError);  // Propagate the error
            })
          );
        } else {
          // If the error is not a 401, propagate it normally
          return throwError(() => error);
        }
      })
    );
  }
}
