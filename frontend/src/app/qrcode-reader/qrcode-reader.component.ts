import { Component, OnInit, signal, ChangeDetectionStrategy } from '@angular/core';
import { Router, ActivatedRoute, NavigationEnd } from '@angular/router';
import { UserService } from '../services/User/user.service';
import { QrCodeTOTP } from '../services/qr-code-totp/qr-code-totp.service';
import { TranslateService } from '@ngx-translate/core';
import { Utils } from '../common/Utils/utils';
import { ToastrService } from 'ngx-toastr';

@Component({
    selector: 'app-qrcode-reader',
    templateUrl: './qrcode-reader.component.html',
    styleUrls: ['./qrcode-reader.component.css'],
    standalone: false,
    changeDetection: ChangeDetectionStrategy.OnPush,
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

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private userService: UserService,
    private qrCode: QrCodeTOTP,
    public translate: TranslateService,
    private utils: Utils,
    private toastr: ToastrService,
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
      this.utils.toastSuccess(this.toastr, 'Got it!', '');

      const substring = ['otpauth://totp/', '?', 'secret='];
      let patternOK = true;
      for (let sub of substring) {
        if (!decoded.includes(sub)) {
          patternOK = false;
        }
      }

      if (!patternOK) {
        this.translate.get('qrcode.error.pattern_invalid').subscribe((translation: string) => {
          this.utils.toastWarning(this.toastr, translation, '');
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
            this.utils.toastWarning(this.toastr, translation, '');
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