import { Routes } from '@angular/router';
import { MobileHomeComponent } from './mobile-home/mobile-home.component';
import { PagenotfoundComponent } from 'src/shared/Views/pagenotfound/pagenotfound.component';


export const routes: Routes = [
  { path: '', component: MobileHomeComponent },
  //{ path: 'signup', component: SignupComponent },
  //{ path: 'login', component: LoginComponent },
  //{ path: 'login/:error_param', component: LoginComponent },
  //{ path: 'vault', component: VaultComponent },
  //{ path: 'vault/locked', component: VaultComponent },
  //{ path: 'vault/edit/:id', component: EditTOTPComponent },
  //{ path: 'vault/add', component: EditTOTPComponent },
  //{ path: 'qrcode', component: QrcodeReaderComponent },
  //{ path: "logout", component: LogoutComponent },
  //{ path: "lock", component: LogoutComponent },
  //{ path: "account", component: AccountComponent },
  //{ path: "privacy", component: PrivacyPolicyComponent },
  //{ path: "changelog", component: ChangelogComponent },
  //{ path: "oauth/callback", component: CallbackComponent },
  //{ path: "oauth/synchronize", component: OauthSyncComponent },
  //{ path: "preferences", component: PreferencesComponent },
  //{ path: "opensource", component: OpenSourceLibraryComponent },
  //{ path: "emailVerification", component: EmailVerificationComponent },
  //{ path: "import/vault", component: ImportVaultComponent },
  //{ path: "import/vault/:type/:step", component: ImportVaultComponent },
  //{ path: "faq", component: FaqComponent },
  //{ path: "faq/:id", component: FaqComponent },
  { path: '**', component: PagenotfoundComponent }
];
