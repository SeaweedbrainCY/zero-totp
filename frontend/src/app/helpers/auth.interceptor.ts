import { Injectable } from '@angular/core';
import { HttpEvent, HttpInterceptor, HttpHandler, HttpRequest, HTTP_INTERCEPTORS, HttpErrorResponse,  } from '@angular/common/http';

import { AuthServiceService } from '../services/auth-service.service';
import { BehaviorSubject } from 'rxjs';

import { Observable, throwError, filter } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';

@Injectable()
export class HttpRequestInterceptor implements HttpInterceptor {
  private isRefreshing = false;
  intervalId: any;


  constructor(
    private authService: AuthServiceService
  ) {}

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    req = req.clone({
      withCredentials: true,
    });

    return next.handle(req).pipe(
      catchError((error) => {
        console.log(error);
        if (error.status === 403 && error.error.detail === "API key expired") {
          return this.handleExpiration(req, next) || throwError(() => error);
        }
        return throwError(() => error);
      })
    );
  }

  private waitForTokenRefresh(){
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

  

  private handleExpiration(request: HttpRequest<any>, next: HttpHandler) : Observable<HttpEvent<any>> {
    if (!this.isRefreshing) {
      this.isRefreshing = true;
      return this.authService.refreshToken().pipe(
          switchMap(() => {
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