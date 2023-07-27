import { Component, OnInit } from '@angular/core';
import { ZXingScannerComponent } from '@zxing/ngx-scanner';
import { toast as superToast } from 'bulma-toast'

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


  
  ngOnInit(): void {
    this.scanner.camerasFound.subscribe((devices: MediaDeviceInfo[]) => {
      this.hasDevices = true;
      console.log("devices", devices);
      //this.desiredDevice = devices[0];
    });
    this.scanner.askForPermission().then((hasPermission: boolean) => {
      this.hasPermission = hasPermission;
      console.log("hasPermission", hasPermission);
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
    console.log("resultString", resultString);
    const pattern= /^otpauth:\/\/totp\/[A-zÀ-ž0-9@:.\-_]+\?[a-zA-Z0-9]+=[a-zA-Z0-9]+(&[a-zA-Z0-9]+=[a-zA-Z0-9]+)*$/;
    if(!pattern.test(this.qrResultString)){
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
        console.log("label= ", label)
        console.log("secret= ", secret)
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
}
