import { Component, OnInit } from '@angular/core';
import { UserService } from '../common/User/user.service';

@Component({
  selector: 'app-vault',
  templateUrl: './vault.component.html',
  styleUrls: ['./vault.component.css']
})
export class VaultComponent implements OnInit {

  constructor(private userService: UserService) { 
  
  }

  ngOnInit() {
    console.log(this.userService);
  }

}
