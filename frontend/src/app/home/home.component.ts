import { Component, Input, OnInit } from '@angular/core';
import {Crypto} from '../common/Crypto/crypto';
import {UserService} from '../common/User/user.service';
import { DomSanitizer } from '@angular/platform-browser';
import { SecurityContext } from '@angular/core';
import { Utils } from '../common/Utils/utils';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})



export class HomeComponent implements OnInit {


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
   
    console.log(crypto.generateRandomSalt())
    // each second :
    setInterval(()=> { this.generateCode() }, 500);

   console.log(this.userService.getId())
  }

  generateCode(){
       this.duration = 30 - Math.floor(Date.now() / 1000 % 30);
      this.code=this.totp("JBSWY3DPEHPK3PXP");
  }

  

 login(){
    const crypto = new Crypto();
    const salt = crypto.generateRandomSalt();
    console.log(Buffer.from(salt).toString('base64'))
    crypto.deriveKey(salt, this.password).then(key=>{
      crypto.encrypt(this.plaintext, key, salt).then(encrypted=>{
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

