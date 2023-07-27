import { Component, OnInit } from '@angular/core';
import { ZXingScannerComponent } from '@zxing/ngx-scanner';

@Component({
  selector: 'app-qrcode-reader',
  templateUrl: './qrcode-reader.component.html',
  styleUrls: ['./qrcode-reader.component.css']
})
export class QrcodeReaderComponent implements OnInit {
  scannerEnabled = true ;
  desiredDevice: MediaDeviceInfo | undefined = undefined;
  scanner = new ZXingScannerComponent();
  hasPermission = undefined;


  camerasFoundHandler(event: any) {
    //this.desiredDevice = event[0];
    //console.log(event);
  }

  ngOnInit(): void {
    this.hasPermission = this.scanner.askForPermission();
  }

  scanSuccessHandler(event: any) {
    console.log("duucess" ,event);
  }

  scanErrorHandler(event: any) {
    console.log("error", event);
  }

  scanFailureHandler(event: any) {
    console.log("dailureEvent" , event);
  }

  scanCompleteHandler(event: any) {
  //  console.log("complete =",  event);
  }

  camerasNotFoundHandler(event: any) {
    console.log("camero not found ", event);
  }
}
