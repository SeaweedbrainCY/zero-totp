import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { SignupComponent } from './signup/signup.component';
import { LoginComponent } from './login/login.component';
import {VaultComponent} from './vault/vault.component';
import { EditTOTPComponent } from './edit-totp/edit-totp.component';
import { LogoutComponent } from './logout/logout.component';

const routes: Routes = [
  {path:'', component: HomeComponent},
  {path:'signup', component: SignupComponent},
  {path:'login', component: LoginComponent},
  {path: 'login/:error_param', component: LoginComponent},
  {path:'vault', component: VaultComponent},
  {path:'vault/edit/:id', component: EditTOTPComponent},
  {path:'vault/add', component: EditTOTPComponent},
  {path:"logout", component: LogoutComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
