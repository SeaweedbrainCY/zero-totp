import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MobileZeroTotpInstanceSelectorComponent } from './mobile-zero-totp-tenant-selector.component';

describe('MobileZeroTotpInstanceSelectorComponent', () => {
  let component: MobileZeroTotpInstanceSelectorComponent;
  let fixture: ComponentFixture<MobileZeroTotpInstanceSelectorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MobileZeroTotpInstanceSelectorComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MobileZeroTotpInstanceSelectorComponent);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
