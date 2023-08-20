import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { UserService } from '../common/User/user.service';
@Component({
  selector: 'app-oauth-sync',
  templateUrl: './oauth-sync.component.html',
  styleUrls: ['./oauth-sync.component.css']
})
export class OauthSyncComponent implements OnInit {
  errorMessage = '';

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
}


