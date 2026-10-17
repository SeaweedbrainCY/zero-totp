import { Component, OnInit, signal, ChangeDetectionStrategy } from '@angular/core';
import { Router, ActivatedRoute, NavigationEnd } from '@angular/router';
import { UserService } from '../../../shared/Services/User/user.service';
import { QrCodeTOTP } from '../services/qr-code-totp/qr-code-totp.service';
import { TranslateService, TranslatePipe } from '@ngx-translate/core';
import { ToastService } from '../../../shared/Services/Toast/toast.service';
import { environment } from 'src/environments/environment';
import { CapacitorBarcodeScanner, CapacitorBarcodeScannerTypeHint } from '@capacitor/barcode-scanner'
import { FormsModule } from '@angular/forms';
import { NgClass } from '@angular/common';
import { ZXingScannerModule } from '@zxing/ngx-scanner';
@Component({
    selector: 'app-qrcode-reader',
    templateUrl: './qrcode-reader.component.html',
    styleUrls: ['./qrcode-reader.component.css'],
    changeDetection: ChangeDetectionStrategy.OnPush,
    imports: [
        FormsModule,
        NgClass,
        ZXingScannerModule,
        TranslatePipe,
    ],
})
export class QrcodeReaderComponent implements OnInit {
  scannerEnabled = signal(true);
  availableDevices = signal<MediaDeviceInfo[] | undefined>(undefined);
  currentDevice = signal<MediaDeviceInfo | undefined>(undefined);
  qrResultString = signal<string | undefined>(undefined);
  hasPermission = signal<boolean | undefined>(undefined);
  hasDevices = signal<boolean | undefined>(undefined);
  scannerStarted = signal(false);
  currentUrl = signal('');
  isBuiltForMobileApp = signal(false)

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private userService: UserService,
    private qrCode: QrCodeTOTP,
    public translate: TranslateService,
    private toast: ToastService,
  ) {
    router.events.subscribe((url: any) => {
      if (url instanceof NavigationEnd) {
        this.currentUrl.set(url.url);
      }
    });
  }

  ngOnInit(): void {
    if (this.userService.id() == null) {
      this.userService.refresh_user_id().then(
        () => {
          this.router.navigate(['/vault'], { relativeTo: this.route.root });
        },
        () => {
          this.router.navigate(['/login/sessionKilled'], { relativeTo: this.route.root });
        },
      );
    }

    if (environment.isMobileApp) {
      this.isBuiltForMobileApp.set(true)
      this.mobileScanQRCode()
    }
  }

  async mobileScanQRCode() {
    const result = await CapacitorBarcodeScanner.scanBarcode({
      hint: CapacitorBarcodeScannerTypeHint.QR_CODE
    });
    this.onCodeResult(result.ScanResult)
  }

  onCamerasFound(devices: MediaDeviceInfo[]): void {
    this.availableDevices.set(devices);
    this.hasDevices.set(Boolean(devices && devices.length));
    if (devices.length > 0) {
      this.scannerStarted.set(true);
    }
  }

  onCodeResult(resultString: string) {
    if (this.scannerEnabled()) {
      this.scannerEnabled.set(false);

      let decoded = decodeURIComponent(resultString);
      this.qrResultString.set(decoded);
      this.toast.success('Got it!');

      const substring = ['otpauth://totp/', '?', 'secret='];
      let patternOK = true;
      for (let sub of substring) {
        if (!decoded.includes(sub)) {
          patternOK = false;
        }
      }

      if (!patternOK) {
        this.translate.get('qrcode.error.pattern_invalid').subscribe((translation: string) => {
          this.toast.warning(translation);
        });
      } else {
        const radical = decoded.split('otpauth://totp/')[1];
        const label = radical.split('?')[0].replace(' ', '');
        const parameters = radical.split('?')[1].replace(' ', '');
        try {
          let secret = parameters.split('secret=')[1];
          if (secret.indexOf('&') > -1) {
            secret = secret.split('&')[0];
          }
          this.qrCode.setLabel(label);
          this.qrCode.setSecret(secret);
          this.navigate('/vault/add');
        } catch {
          this.translate.get('qrcode.error.read_error').subscribe((translation: string) => {
            this.toast.warning(translation);
          });
        }
      }
    }
  }

  onDeviceSelectChange(selected: string) {
    const devices = this.availableDevices();
    if (!devices) return;
    const device = devices.find(x => x.deviceId === selected);
    this.currentDevice.set(device ?? undefined);
  }

  onHasPermission(has: boolean) {
    this.hasPermission.set(has);
  }

  changeDevice(deviceName: string) {
    const device = this.availableDevices()!.find(x => x.deviceId === deviceName);
    this.currentDevice.set(device ?? undefined);
  }

  navigate(route: string) {
    this.router.navigate([route], { relativeTo: this.route.root });
  }
}
