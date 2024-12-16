import { Component, OnInit } from '@angular/core';
import { faFileArrowDown, faArrowRight, faCloudArrowUp, faCheck, faUnlockKeyhole } from '@fortawesome/free-solid-svg-icons'; 
import { TranslateService } from '@ngx-translate/core';
import { Router, ActivatedRoute } from '@angular/router';



@Component({
  selector: 'app-import-vault',
  templateUrl: './import-vault.component.html',
  styleUrl: './import-vault.component.css'
})
export class ImportVaultComponent implements OnInit {
  faFileArrowDown = faFileArrowDown;
  faArrowRight = faArrowRight;
  faCloudArrowUp=faCloudArrowUp
  vault_steps: Map<string,String[]> = new Map<string,String[]>();
  step: string | null = null
  vault_type: string | null = null
  faCheck=faCheck;
  faUnlockKeyhole=faUnlockKeyhole;
  vault_password="";
  
  constructor(
    private translate: TranslateService,
    private router: Router,
    private route: ActivatedRoute
  ) { 
    this.vault_steps.set("zero-totp", ["import", "decrypt", "select", "encrypt"])

    
  }

  ngOnInit(): void {

    this.init_component()

    this.router.events.subscribe((url:any) => {
      this.init_component()
    });

    
    
   
  }

  init_component(){
    this.vault_type = this.route.snapshot.paramMap.get('type')
    this.step = this.route.snapshot.paramMap.get('step')
    console.log(this.vault_type)
    console.log(this.step)
    if(this.vault_type != null){
      if(!(this.vault_steps.has(this.vault_type))){
        this.router.navigate(['/import/vault'])
      }
      if(this.vault_type == "zero-totp"){
        if(this.step == null){
          this.redirectToFirstStep()
        } else {
          console.log(this.vault_steps.get(this.vault_type)!.indexOf(this.step!))
          if(!(this.vault_steps.get(this.vault_type)!.includes(this.step))){
            this.redirectToFirstStep()
          }
        }
      }
    }
    
  }

  redirectToFirstStep(){
    this.router.navigate(['/import/vault/'+ this.vault_type + '/' + this.vault_steps.get(this.vault_type!)![0]])
  }

  openFile(event: any): void {
    //TODO
  }


  continue(){
    if(this.vault_type == "zero-totp"){
      const current_step_index = this.vault_steps.get(this.vault_type)!.indexOf(this.step!)
      if(this.step == "import"){
        //TODO 
        this.router.navigate(['/import/vault/'+ this.vault_type + '/' + this.vault_steps.get(this.vault_type)![current_step_index + 1]])
      } else if(this.step == "decrypt"){
        //TODO 
        this.router.navigate(['/import/vault/'+ this.vault_type + '/' + this.vault_steps.get(this.vault_type)![current_step_index + 1]])
      } else if(this.step == "select"){
        //TODO 
        this.router.navigate(['/import/vault/'+ this.vault_type + '/' + this.vault_steps.get(this.vault_type)![current_step_index + 1]])
      } else if(this.step == "encrypt"){
        //TODO 
        console.log("done")
      }
    }
  }

  cancel(){
    const current_step_index = this.vault_steps.get(this.vault_type!)!.indexOf(this.step!)
    if(current_step_index == 0){
      this.router.navigate(['/import/vault'])
    } else {
      this.router.navigate(['/import/vault/'+ this.vault_type + '/' + this.vault_steps.get(this.vault_type!)![current_step_index - 1]])
    }
  }

  giveUp(){
    this.router.navigate(['/import/vault'])
  }
}
