import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RescueOpenVaultComponent } from './rescue-open-vault.component';

describe('RescueOpenVaultComponent', () => {
  let component: RescueOpenVaultComponent;
  let fixture: ComponentFixture<RescueOpenVaultComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RescueOpenVaultComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RescueOpenVaultComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
