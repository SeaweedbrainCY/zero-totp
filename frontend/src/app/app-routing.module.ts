import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { SignupComponent } from './signup/signup.component';
import { LoginComponent } from './login/login.component';
import {VaultComponent} from './vault/vault.component';
import { EditTOTPComponent } from './edit-totp/edit-totp.component';
import { LogoutComponent } from './logout/logout.component';
import { AccountComponent } from './account/account.component';
import { PagenotfoundComponent } from './pagenotfound/pagenotfound.component';
import { QrcodeReaderComponent } from './qrcode-reader/qrcode-reader.component';
import { DevComponent } from './dev/dev.component';
import { PrivacyPolicyComponent } from './privacy-policy/privacy-policy.component';
import { ChangelogComponent } from './changelog/changelog.component';
import { CallbackComponent } from './callback/callback.component';
import { OauthSyncComponent } from './oauth-sync/oauth-sync.component';
import { PreferencesComponent } from './preferences/preferences.component';
import { OpenSourceLibraryComponent } from './open-source-library/open-source-library.component';
import { EmailVerificationComponent } from './email-verification/email-verification.component';
import { ImportVaultComponent } from './import-vault/import-vault.component';
import { FaqComponent } from './faq/faq.component';

export const routes: Routes = [
  {path:'', component: HomeComponent},
  {path:'signup', component: SignupComponent},
  {path:'login', component: LoginComponent},
  {path: 'login/:error_param', component: LoginComponent},
  {path:'vault', component: VaultComponent},
  {path:'vault/locked', component: VaultComponent},
  {path:'vault/edit/:id', component: EditTOTPComponent},
  {path:'vault/add', component: EditTOTPComponent},
  {path:'qrcode', component: QrcodeReaderComponent},
  {path:"logout", component: LogoutComponent},
  {path:'dev', component: DevComponent},
  {path:"account", component: AccountComponent},
  {path:"privacy", component: PrivacyPolicyComponent},
  {path:"changelog", component: ChangelogComponent},
  {path:"oauth/callback", component: CallbackComponent},
  {path:"oauth/synchronize", component: OauthSyncComponent},
  {path: "preferences", component: PreferencesComponent},
  {path: "opensource", component: OpenSourceLibraryComponent},
  {path:"emailVerification", component: EmailVerificationComponent},
  {path: "import/vault", component: ImportVaultComponent},
  {path: "import/vault/:type/:step", component: ImportVaultComponent},
  {path: "faq", component: FaqComponent},
  {path:'**', component: PagenotfoundComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes, {enableViewTransitions: true})],
  exports: [RouterModule]
})
export class AppRoutingModule { }
