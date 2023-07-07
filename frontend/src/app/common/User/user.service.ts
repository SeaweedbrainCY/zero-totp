import { Injectable } from '@angular/core';
import { User } from './user';


@Injectable({
  providedIn: 'root'
})
export class UserService {
  private user:User;

  constructor() {
    this.user = new User();
   }

  setUser(user:User){
    this.user = user;
  }

  getUser():User{
    return this.user;
  }


}
