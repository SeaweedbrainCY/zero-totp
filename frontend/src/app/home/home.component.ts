import { Component, Input, OnInit } from '@angular/core';
import {Crypto} from '../common/Crypto/crypto';
import {UserService} from '../common/User/user.service';
import { DomSanitizer } from '@angular/platform-browser';
import { SecurityContext } from '@angular/core';
import { Utils } from '../common/Utils/utils';
import { faLock, faEyeSlash, faFingerprint, faUserLock, faHouse, faMobileScreenButton, faCode, faKitMedical, faAngleDown } from '@fortawesome/free-solid-svg-icons';
import { faGithub } from '@fortawesome/free-brands-svg-icons';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})



export class HomeComponent implements OnInit {
  faLock = faLock;
  faEyeSlash = faEyeSlash;
  faGithub = faGithub;
  faUserLock = faUserLock;
  faHouse = faHouse;
  faMobileScreenButton = faMobileScreenButton;
  faCode = faCode;
  faKitMedical = faKitMedical;
  faAngleDown = faAngleDown;
  is_dropdown_active=false;


  password: string = "";
  encrypted = "";
  plaintext = "";
  decrypted="";
  totp = require('totp-generator');
  code = "";
  duration=0;
  xss = "<script>alert('xss');</script>https://"

  constructor(
    private userService:UserService, 
    private _sanitizer: DomSanitizer,
    private utils: Utils){
    this.xss = utils.sanitize(this.xss)!
  }

  ngOnInit(){
    const crypto = new Crypto();
    // each second :
    setInterval(()=> { this.generateCode() }, 500);
  }

  generateCode(){
       this.duration = 30 - Math.floor(Date.now() / 1000 % 30);
      this.code=this.totp("JBSWY3DPEHPK3PXP");
  }

  

 login(){
    const crypto = new Crypto();
    const salt = crypto.generateRandomSalt();
    crypto.deriveKey(salt, this.password).then(key=>{
      crypto.encrypt(this.plaintext, key).then(encrypted=>{
        this.encrypted = encrypted;
        crypto.decrypt(this.encrypted, key).then(decrypted=>{
          if(decrypted == null){
            this.decrypted = "Wrong key"
          } else {
            this.decrypted = decrypted;
          }
        
        })
      });
    });
    
 }


}

