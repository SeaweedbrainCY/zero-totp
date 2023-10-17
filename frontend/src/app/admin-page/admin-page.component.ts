import { Component } from '@angular/core';

@Component({
  selector: 'app-admin-page',
  templateUrl: './admin-page.component.html',
  styleUrls: ['./admin-page.component.css']
})
export class AdminPageComponent {
  users: any = []
  
    constructor() { 
      this.users = [
        {"username": "foo", "email": "foo@gmail", "createdAt":"10-10-2023", "isDisabled":false},
        {"username": "barr", "email": "bar@gmail", "createdAt":"10-10-2023", "isDisabled":true},
      ]
    }

}
