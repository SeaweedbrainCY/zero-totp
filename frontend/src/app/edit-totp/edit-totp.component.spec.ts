import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditTOTPComponent } from './edit-totp.component';

describe('EditTOTPComponent', () => {
  let component: EditTOTPComponent;
  let fixture: ComponentFixture<EditTOTPComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [EditTOTPComponent]
    });
    fixture = TestBed.createComponent(EditTOTPComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
