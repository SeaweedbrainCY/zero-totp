import { Routes } from '@angular/router';
import { RescueHomeComponent } from './home/home.component';
import { PagenotfoundComponent } from '../../shared/Views/pagenotfound/pagenotfound.component';
import { RescuePrivacyPolicyComponent } from './rescue-privacy-policy/rescue-privacy-policy.component';
import { ChangelogComponent } from 'src/shared/Views/changelog/changelog.component';
import { OpenSourceLibraryComponent } from 'src/shared/Views/open-source-library/open-source-library.component';
import { RescueOpenVaultComponent } from './rescue-open-vault/rescue-open-vault.component';
import { RescueVaultComponent } from './rescue-vault/rescue-vault.component';

export const routes: Routes = [
  { path: '', component: RescueHomeComponent },
  { path: 'privacy', component: RescuePrivacyPolicyComponent },
  { path: "changelog", component: ChangelogComponent },
  { path: 'opensource', component: OpenSourceLibraryComponent },
  { path: 'open-vault', component: RescueOpenVaultComponent },
  {path: 'vault', component:RescueVaultComponent},
  { path: '**', component: PagenotfoundComponent },
];
