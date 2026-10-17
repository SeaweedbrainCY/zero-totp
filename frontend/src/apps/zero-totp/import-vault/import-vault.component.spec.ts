import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ImportVaultComponent } from './import-vault.component';

describe('ImportVaultComponent', () => {
  let component: ImportVaultComponent;
  let fixture: ComponentFixture<ImportVaultComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ImportVaultComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ImportVaultComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
