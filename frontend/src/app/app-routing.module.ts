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

const routes: Routes = [
  {path:'', component: HomeComponent},
  {path:'signup', component: SignupComponent},
  {path:'login', component: LoginComponent},
  {path: 'login/:error_param', component: LoginComponent},
  {path:'vault', component: VaultComponent},
  {path:'vault/edit/:id', component: EditTOTPComponent},
  {path:'vault/add', component: EditTOTPComponent},
  {path:'qrcode', component: QrcodeReaderComponent},
  {path:"logout", component: LogoutComponent},
  {path:'dev', component: DevComponent},
  {path:"account", component: AccountComponent},
  {path:"privacy", component: PrivacyPolicyComponent},
  {path:'**', component: PagenotfoundComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
