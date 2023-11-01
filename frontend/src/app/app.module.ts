import { NgModule, CSP_NONCE } from '@angular/core';
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
import { EditTOTPComponent } from './edit-totp/edit-totp.component';
import { LogoutComponent } from './logout/logout.component';
import { Crypto } from './common/Crypto/crypto';
import { FooterComponent } from './footer/footer.component';
import { ClipboardModule } from '@angular/cdk/clipboard';
import { PagenotfoundComponent } from './pagenotfound/pagenotfound.component';
import { ZXingScannerModule } from '@zxing/ngx-scanner';
import { QrcodeReaderComponent } from './qrcode-reader/qrcode-reader.component';
import { QrCodeTOTP } from './common/qr-code-totp/qr-code-totp.service';
import { DevComponent } from './dev/dev.component';
import { AccountComponent } from './account/account.component';
import { LocalVaultV1Service } from './common/upload-vault/LocalVaultv1Service.service';
import { PrivacyPolicyComponent } from './privacy-policy/privacy-policy.component';
import { BnNgIdleService } from 'bn-ng-idle'; 
import { ChangelogComponent } from './changelog/changelog.component';
import { AdminPageComponent } from './admin-page/admin-page.component';
import { CallbackComponent } from './callback/callback.component';
import { OauthSyncComponent } from './oauth-sync/oauth-sync.component';
import { CookieModule, CookieService } from 'ngx-cookie';


@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    SignupComponent,
    NavbarComponent,
    LoginComponent,
    VaultComponent,
    EditTOTPComponent,
    LogoutComponent,
    FooterComponent,
    PagenotfoundComponent,
    QrcodeReaderComponent,
    DevComponent,
    AccountComponent,
    PrivacyPolicyComponent,
    ChangelogComponent,
    AdminPageComponent,
    CallbackComponent,
    OauthSyncComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    FontAwesomeModule,
    HttpClientModule, 
    ClipboardModule,
    ZXingScannerModule,
    CookieModule.withOptions()
  ],
  providers: [UserService, Utils, Crypto, QrCodeTOTP, LocalVaultV1Service, BnNgIdleService, CookieService, {
    provide: CSP_NONCE,
    useValue: 'random-nonce-placeholder'
  }],
  bootstrap: [AppComponent]
})
export class AppModule { }
