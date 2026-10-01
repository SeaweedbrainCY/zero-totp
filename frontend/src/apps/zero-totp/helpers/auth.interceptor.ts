import { Injectable } from '@angular/core';
import { HttpEvent, HttpInterceptor, HttpHandler, HttpRequest, HTTP_INTERCEPTORS, HttpErrorResponse, } from '@angular/common/http';

import { AuthServiceService, AuthToken } from '../services/AuthService/auth-service.service';
import { BehaviorSubject } from 'rxjs';

import { Observable, throwError, filter } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';
import { environment } from 'src/environments/environment';
import { ApiService } from '../services/API/api.service';

@Injectable()
export class HttpRequestInterceptor implements HttpInterceptor {
  private isRefreshing = false;
  intervalId: any;


  constructor(
    private authService: AuthServiceService,
    private apiService: ApiService
  ) { }

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    req = req.clone({
      withCredentials: true,
    });

    if (environment.isMobileApp) {
      const destinationURL = new URL(req.url)
      if (this.authService.auth_token()?.domain == destinationURL.host && destinationURL.protocol == "https:") {
        req = req.clone({
          setHeaders: { Authorization: `Bearer ${this.authService.auth_token()?.session_token}` },
        });
      }
    }


    return next.handle(req).pipe(
      catchError((error) => {
        console.log(error);

        if (error.status === 403 && error.error.detail === "Session expired") {
          if (environment.isMobileApp) {
            const configuredAPIURL = new URL(this.apiService.baseURL)
            const destinationURL = new URL(req.url)
            if (configuredAPIURL.host == destinationURL.host) {
              return this.handleExpiration(req, next) || throwError(() => error);
            }
          } else {
            // For webapp the browser won't send the cookies to a foreign domain so it's safe
            return this.handleExpiration(req, next) || throwError(() => error);
          }
        }

        return throwError(() => error);
      })
    );
  }

  private waitForTokenRefresh() {
    return new Observable((observer) => {
      const interval = setInterval(() => {
        if (!this.isRefreshing) {
          clearInterval(interval);
          observer.next(null)
          observer.complete();
        }
      }, 100);
    });
  }



  private handleExpiration(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    if (!this.isRefreshing) {
      this.isRefreshing = true;
      return this.authService.refreshToken().pipe(
        switchMap((response) => {
          if (environment.isMobileApp) {
            const apiURL = new URL(this.apiService.baseURL)
            const tokens: AuthToken = {
              refresh_token: response.body!.refresh_token ?? "",
              session_token: response.body!.session_token ?? "",
              domain: apiURL.host
            }
            this.authService.setToken(tokens)
            const destinationURL = new URL(request.url)
            if (tokens.domain == destinationURL.host && destinationURL.protocol == "https:") {
              request = request.clone({
                setHeaders: { Authorization: `Bearer ${tokens.session_token}` },
              });
            }
          }
          this.isRefreshing = false;
          return next.handle(request);
        }),
        catchError((error) => {
          console.log(error);
          this.isRefreshing = false;
          return throwError(() => error);
        })
      );
    } else {
      return this.waitForTokenRefresh().pipe(
        switchMap(() => {
          const destinationURL = new URL(request.url)
          if (this.authService.auth_token()?.domain == destinationURL.host && destinationURL.protocol == "https:") {
            request = request.clone({
              setHeaders: { Authorization: `Bearer ${this.authService.auth_token()?.session_token}` },
            });
          }
          return next.handle(request);
        }), catchError((error) => {
          console.log(error);
          return throwError(() => error);
        })
      );
    }
  }
}

export const httpInterceptorProviders = [
  { provide: HTTP_INTERCEPTORS, useClass: HttpRequestInterceptor, multi: true },
];