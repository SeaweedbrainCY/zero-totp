import { Component, OnInit } from '@angular/core';
import { UserService } from '../common/User/user.service';
import { ActivatedRoute, Router } from '@angular/router';
import { faPen, faSquarePlus } from '@fortawesome/free-solid-svg-icons';

@Component({
  selector: 'app-vault',
  templateUrl: './vault.component.html',
  styleUrls: ['./vault.component.css']
})
export class VaultComponent implements OnInit {
  faPen = faPen;
  faSquarePlus = faSquarePlus;
  vault: Map<string, Map<string,string>> | undefined;
  vaultDomain : string[] = [];
  remainingTime = 0;
  totp = require('totp-generator');

  constructor(
    private userService: UserService,
    private router: Router,
    private route: ActivatedRoute,
    ) { let property = new Map<string, string>();
      property.set("secret", "GEZDGNBSGEZDGMZR");
      property.set("color","info");
      let vault = this.userService.getVault();
      if(vault == null){
        vault = new Map<string, Map<string,string>>();
      }
      vault.set("fake@github.com", property);
      property = new Map<string, string>();
      property.set("secret", "GEZDGNBSGEZDGMZS");
      property.set("color","primary");
      vault.set("fake@google.com", property);
      this.userService.setVault(vault); 
      this.userService.setId(1);
    }

  ngOnInit() {
    if(this.userService.getId() == null){
      //this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
      console.log("")
    } else {
      if(this.userService.getVault() == null){
       this.vault = new Map<string, Map<string,string>>();
      } else {
        this.vault = this.userService.getVault()!;
      }
      this.vaultDomain = Array.from(this.vault!.keys()) as string[];
      console.log(this.vaultDomain)
      setInterval(()=> { this.generateTime() }, 20);
      setInterval(()=> { this.generateCode() }, 100);
    }    
  }

  addNew(){
    this.router.navigate(["/vault/add"], {relativeTo:this.route.root});
   
  }

  generateTime(){
    const duration = 30 - Math.floor(Date.now() / 10 % 3000)/100;
    this.remainingTime = (duration/30)*100
  }

  generateCode(){
    for(let domain of this.vaultDomain){
      const secret = this.vault!.get(domain)!.get("secret")!;
      try{
        let code=this.totp(secret);
        code = code[0]+code[1]+code[2] + " " + code[3]+code[4]+code[5] 
        this.vault!.get(domain)!.set("code", code);
      } catch (e){
        let code = "Error"
        this.vault!.get(domain)!.set("code", code);
      }
   
    }


  }



}
