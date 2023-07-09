import { Injectable } from '@angular/core';
@Injectable({providedIn: 'root'}) //Note that you will need to declare it as `@Injectable`. 

@Injectable({
  providedIn: 'root'
})
export class UserService {
  id:number| null =null;;
  username:string| null =null;;
  key:CryptoKey| null =null;;
  derivedKeySalt:string| null =null;;
  vault:[string:string] | null =null;

  constructor() {
   }



}
