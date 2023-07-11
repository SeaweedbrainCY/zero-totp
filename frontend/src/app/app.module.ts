import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';


import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './home/home.component';
import { SignupComponent } from './signup/signup.component';
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome';
import { HttpClientModule } from '@angular/common/http';
import { NavbarComponent } from './navbar/navbar.component';
import { LoginComponent } from './login/login.component';
import { VaultComponent } from './vault/vault.component';
import { UserService } from './common/User/user.service';
import { Utils } from './common/Utils/utils';


@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    SignupComponent,
    NavbarComponent,
    LoginComponent,
    VaultComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    FontAwesomeModule,
    HttpClientModule
  ],
  providers: [UserService, Utils],
  bootstrap: [AppComponent]
})
export class AppModule { }
