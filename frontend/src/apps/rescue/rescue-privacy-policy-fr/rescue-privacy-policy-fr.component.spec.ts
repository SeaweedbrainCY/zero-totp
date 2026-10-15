import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RescuePrivacyPolicyFrComponent } from './rescue-privacy-policy-fr.component';

describe('RescuePrivacyPolicyFrComponent', () => {
  let component: RescuePrivacyPolicyFrComponent;
  let fixture: ComponentFixture<RescuePrivacyPolicyFrComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RescuePrivacyPolicyFrComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RescuePrivacyPolicyFrComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
