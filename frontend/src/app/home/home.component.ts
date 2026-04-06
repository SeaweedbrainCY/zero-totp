import { Component, Input, OnInit, signal, ChangeDetectionStrategy } from '@angular/core';
import {Crypto} from '../common/Crypto/crypto';
import { Utils } from '../common/Utils/utils';
import { faLock, faEyeSlash, faFingerprint, faUserLock, faHouse, faMobileScreenButton, faCode, faKitMedical, faAngleDown, faPen, faCopy } from '@fortawesome/free-solid-svg-icons';
import { faGithub } from '@fortawesome/free-brands-svg-icons';
import { ToastrService } from 'ngx-toastr';

@Component({
    selector: 'app-home',
    templateUrl: './home.component.html',
    styleUrls: ['./home.component.css'],
    standalone: false,
    changeDetection: ChangeDetectionStrategy.OnPush,
})



export class HomeComponent implements OnInit {
  faLock = faLock;
  faEyeSlash = faEyeSlash;
  faGithub = faGithub;
  faUserLock = faUserLock;
  faPen = faPen;
  faCopy = faCopy;
  faHouse = faHouse;
  faMobileScreenButton = faMobileScreenButton;
  faCode = faCode;
  faKitMedical = faKitMedical;
  faAngleDown = faAngleDown;
  is_dropdown_active = signal(false);


  example_domain = signal("");
  example_code = signal("");
  example_title = signal("");
  remainingTime = signal(0);
  example_color = signal("");
  example_ico = signal("");

  last_random_i = 0;
  current_color_index = 0;

  constructor(
    private utils: Utils,
    private toastr:ToastrService
    ){
  }

  ngOnInit(){
    const crypto = new Crypto();
    // each second :
    this.current_color_index = Math.floor(Math.random()*3);
    this.generateExample();
    setInterval(()=> { this.generateExample(); }, 5000);
    setInterval(()=> { this.generateTime() }, 20);
  }

  generateExample(){
    const icos = ["facebook.ico", "github.ico", "google.ico", "apple.ico", "google.ico", "amazon.ico", "aws.ico", "microsoft.ico", "onedrive.ico", "gitlab.ico"]
    const domains = ["facebook.com", "github.com", "google.com", "apple.com", "google.com", "amazon.com", "aws.com", "microsoft.com", "onedrive.com", "gitlab.com"]
    const titles = ["Facebook", "Github", "Gmail", "Apple", "Google", "Amazon", "AWS", "Microsoft", "OneDrive", "Gitlab"]
    const colors = [ "info", "success", "danger"]
    let random_i = Math.floor(Math.random()*(domains.length));
    if (random_i == this.last_random_i){
      this.generateExample();
      return;
    }
    this.example_domain.set(domains[random_i]);
    this.example_title.set(titles[random_i]);
    this.example_code.set((Math.floor(Math.random() * (999999 - 100000 + 1)) + 100000).toString());
    this.example_ico.set(icos[random_i]);
    this.current_color_index = (this.current_color_index+1)%colors.length;
    this.example_color.set(colors[this.current_color_index]);
  }

  generateTime(){
    const duration = 30 - Math.floor(Date.now() / 10 % 3000)/100;
    this.remainingTime.set((duration/30)*100);
    if(this.remainingTime() >= 99.99){
      this.generateExample();
    }
  }

  copy(){
    this.utils.toastSuccess(this.toastr, "Copied !", "");
  }


 scrollTo(element: HTMLElement) {
  element.scrollIntoView({behavior: "smooth", block: "start", inline: "nearest"});
 }


}