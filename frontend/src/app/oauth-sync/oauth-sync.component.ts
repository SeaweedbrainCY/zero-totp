import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { UserService } from '../common/User/user.service';
import { HttpClient } from '@angular/common/http';
import { ApiService } from '../common/ApiService/api-service';
import { faCircleNotch } from '@fortawesome/free-solid-svg-icons';
@Component({
  selector: 'app-oauth-sync',
  templateUrl: './oauth-sync.component.html',
  styleUrls: ['./oauth-sync.component.css']
})
export class OauthSyncComponent implements OnInit {
  errorMessage = '';
  faCircleNotch = faCircleNotch;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private userService: UserService,
  ) { }

  ngOnInit(): void {
    if(this.userService.getId() == null){
      this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
  }

  }

  uploadEncryptedTokens(){

  }
}


