import { Component, OnInit } from '@angular/core';
import { ZXingScannerComponent } from '@zxing/ngx-scanner';
import { toast as superToast } from 'bulma-toast'
import { Router, ActivatedRoute, NavigationEnd } from '@angular/router';
import { UserService } from '../common/User/user.service';
import { QrCodeTOTP } from '../common/qr-code-totp/qr-code-totp.service';
import { BnNgIdleService } from 'bn-ng-idle';

@Component({
  selector: 'app-qrcode-reader',
  templateUrl: './qrcode-reader.component.html',
  styleUrls: ['./qrcode-reader.component.css']
})
export class QrcodeReaderComponent implements OnInit {
  scannerEnabled = true ;
  availableDevices: MediaDeviceInfo[] | undefined = undefined;
  currentDevice: MediaDeviceInfo | undefined = undefined;
  qrResultString: string | undefined = undefined;;
  scanner = new ZXingScannerComponent();
  hasPermission: undefined | boolean= undefined;
  hasDevices : undefined | boolean = undefined;
  scannerStarted = false;
  totp = require('totp-generator');
  currentUrl:string = "";

  constructor(
    private router: Router,
    private route : ActivatedRoute,
    private userService : UserService,
    private qrCode: QrCodeTOTP,
    private bnIdle: BnNgIdleService,
  ){
    router.events.subscribe((url:any) => {
      if (url instanceof NavigationEnd){
          this.currentUrl = url.url;
      }});
  }


  
  ngOnInit(): void {
    if(this.userService.getId() == null){
      this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
    }
    this.scanner.camerasFound.subscribe((devices: MediaDeviceInfo[]) => {
      this.hasDevices = true;
    });
    this.scanner.askForPermission().then((hasPermission: boolean) => {
      this.hasPermission = hasPermission;
    });
    this.bnIdle.startWatching(600).subscribe((isTimedOut: boolean) => {
      if(isTimedOut){
        this.bnIdle.stopTimer();
        this.userService.clear();
        this.router.navigate(['/login/sessionTimeout'], {relativeTo:this.route.root});
      }
    });
  }

  onCamerasFound(devices: MediaDeviceInfo[]): void {
    this.availableDevices = devices;
    this.hasDevices = Boolean(devices && devices.length);
    if(devices.length > 0) {
      this.scannerStarted = true;
    }
  }

  onCodeResult(resultString: string) {
    console.log("resultString", resultString);
    if(this.scannerEnabled){ // false positive
      this.scannerEnabled = false;
    
    this.qrResultString = resultString;
    superToast({
      message: "Got it!",
      type: "is-success",
      dismissible: true,
    animate: { in: 'fadeIn', out: 'fadeOut' }
    });
    this.qrResultString = decodeURIComponent(this.qrResultString);
    const substring = ['otpauth://totp/', '?', 'secret=']
    let patternOK = true;
    for (let sub of substring){
      if(!this.qrResultString.includes(sub)){
        patternOK = false;
      }
    }
    if(!patternOK){
      superToast({
        message: "This is not a TOTP QR code or it contains error.",
        type: "is-warning",
        duration: 20000,
        dismissible: false,
      animate: { in: 'fadeIn', out: 'fadeOut' }
      });
    } else {
      const radical = this.qrResultString.split('otpauth://totp/')[1]
      
      const label = radical.split("?")[0].replace(' ', '')
      const parameters = radical.split("?")[1].replace(' ','')
      try{
        let secret = parameters.split("secret=")[1]
        if(secret.indexOf('&')>-1){
          secret = secret.split('&')[0]
        } 
        this.qrCode.setLabel(label)
        this.qrCode.setSecret(secret)
        this.navigate("/vault/add")
      } catch {
        superToast({
          message: "An error occured while reading the QR code information",
          type: "is-warning",
          duration: 20000,
          dismissible: false,
        animate: { in: 'fadeIn', out: 'fadeOut' }
        });
      }

    }
  }
  }

  onDeviceSelectChange(selected: string) {
    if(!this.availableDevices) return;
    const device = this.availableDevices.find(x => x.deviceId === selected);
    this.currentDevice = device || undefined;
  }


  onHasPermission(has: boolean) {
    this.hasPermission = has;
  }

  changeDevice(deviceName: string) {
    const device = this.availableDevices!.find(x => x.deviceId === deviceName);
    this.currentDevice = device || undefined;
  }

  navigate(route:string){
    this.router.navigate([route], {relativeTo:this.route.root});
  }
}
