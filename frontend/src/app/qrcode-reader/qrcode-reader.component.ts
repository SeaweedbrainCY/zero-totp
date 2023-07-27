import { Component, OnInit } from '@angular/core';
import { ZXingScannerComponent } from '@zxing/ngx-scanner';

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
    this.qrResultString = resultString;
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
