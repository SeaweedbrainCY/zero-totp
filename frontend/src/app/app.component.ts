import { Component, OnInit } from '@angular/core';
import { environment } from 'src/environments/environment';
import { ApiService } from './common/ApiService/api-service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit{
  title = 'frontend';



  ngOnInit(): void {
    if(environment.production){
      if(location.hostname == "ca.zero-totp.com"){
        ApiService.API_URL = "https://api.ca.zero-totp.com";
      }
    }
  }

}
