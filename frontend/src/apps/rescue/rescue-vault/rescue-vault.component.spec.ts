import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RescueVaultComponent } from './rescue-vault.component';

describe('RescueVaultComponent', () => {
  let component: RescueVaultComponent;
  let fixture: ComponentFixture<RescueVaultComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RescueVaultComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RescueVaultComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
