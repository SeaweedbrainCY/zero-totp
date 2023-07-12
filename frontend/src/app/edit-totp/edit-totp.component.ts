import { Component } from '@angular/core';
import { Router, ActivatedRoute, NavigationEnd } from '@angular/router';
import { UserService } from '../common/User/user.service';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-edit-totp',
  templateUrl: './edit-totp.component.html',
  styleUrls: ['./edit-totp.component.css']
})
export class EditTOTPComponent {

  constructor(
    private router: Router,
    private route : ActivatedRoute,
    private userServer : UserService,
    private http: HttpClient
  ){}

}
