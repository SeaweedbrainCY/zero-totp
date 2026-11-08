import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ZeroTotpInstanceSelectorComponent } from './zero-totp-instance-selector.component';

describe('ZeroTotpInstanceSelectorComponent', () => {
  let component: ZeroTotpInstanceSelectorComponent;
  let fixture: ComponentFixture<ZeroTotpInstanceSelectorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ZeroTotpInstanceSelectorComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ZeroTotpInstanceSelectorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
