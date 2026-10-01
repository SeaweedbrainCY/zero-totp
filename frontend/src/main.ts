import { bootstrapApplication } from '@angular/platform-browser';

import { AppComponent } from './apps/zero-totp/app.component';
import { appConfig } from './apps/zero-totp/app.config';

bootstrapApplication(AppComponent, appConfig)
  .catch(err => console.error(err));
