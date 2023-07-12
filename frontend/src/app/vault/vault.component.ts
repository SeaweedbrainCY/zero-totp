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

  constructor(
    private userService: UserService,
    private router: Router,
    private route: ActivatedRoute,
    ) { }

  ngOnInit() {
    if(this.userService.getId() == null){
      //this.router.navigate(["/login/sessionKilled"], {relativeTo:this.route.root});
    }

  }

  addNew(){
    this.router.navigate(["/vault/add"], {relativeTo:this.route.root});
  }

}
