import { Component, Input, OnInit } from '@angular/core';
import {Crypto} from '../common/Crypto/crypto';
import {User} from '../common/User/user';
import {UserService} from '../common/User/user.service';


@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})



export class HomeComponent implements OnInit {

  user:User;

  password: string = "";
  encrypted = "";
  plaintext = "";
  decrypted="";
  totp = require('totp-generator');
  code = "";
  duration=0;

  constructor(private userService:UserService){
    this.user = userService.getUser();
  }

  ngOnInit(){
    // each second :
    setInterval(()=> { this.generateCode() }, 500);
    if (this.user == null) {
      this.user = new User();
      console.log("user is null")
    }
   console.log(this.user.id)
  }

  generateCode(){
       this.duration = 30 - Math.floor(Date.now() / 1000 % 30);
      this.code=this.totp("JBSWY3DPEHPK3PXP");
  }

  

 login(){
    const crypto = new Crypto();
    const salt = crypto.generateRandomSalt();
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

