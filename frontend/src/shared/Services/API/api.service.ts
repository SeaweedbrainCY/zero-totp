import { Injectable } from '@angular/core';

/**
 * Default (web): relative URLs, i.e. baseURL = "".
 * Apps that need something else (mobile) override it in their app.config.ts.
 */
@Injectable({ providedIn: 'root', useFactory: () => new RelativeApiService() })
export abstract class ApiService {
  abstract readonly baseURL: string;
}

export class RelativeApiService extends ApiService {
  override readonly baseURL = '';
}
