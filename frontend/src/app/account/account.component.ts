import { Component, OnInit } from '@angular/core';
import { faEnvelope, faLock,  faCheck, faUser} from '@fortawesome/free-solid-svg-icons';
import { UserService } from '../common/User/user.service';
import { ActivatedRoute, Router } from '@angular/router';

@Component({
  selector: 'app-account',
  templateUrl: './account.component.html',
  styleUrls: ['./account.component.css']
})
export class AccountComponent implements OnInit {
  faUser=faUser;
  faEnvelope=faEnvelope;
  faLock=faLock;
  faCheck=faCheck;
  isDestroying = false;
  isModalActive = false;
  constructor(
    private userService: UserService,
    private router: Router,
    private route: ActivatedRoute,
    ){}

  
  ngOnInit(): void {
    if(this.userService.getId() == null){
      this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
    } else {
    }
  }

  deleteAccount(){
    this.isDestroying = true;
  }

  modal(){
    if(!this.isDestroying){
      this.isModalActive = !this.isModalActive;
    }
  }

}
