import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { UserService } from '../common/User/user.service';


@Component({
  selector: 'app-logout',
  templateUrl: './logout.component.html',
  styleUrls: ['./logout.component.css']
})
export class LogoutComponent implements OnInit{

  constructor(
    private router: Router,
    private route: ActivatedRoute,
    private userService: UserService,
    ) { }

  ngOnInit(): void {
    this.userService.clear();
    this.router.navigate(["/login"], {relativeTo:this.route.root});
  }
}
