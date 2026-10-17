import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VaultViewComponent } from './vault-view.component';

describe('VaultViewComponent', () => {
  let component: VaultViewComponent;
  let fixture: ComponentFixture<VaultViewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VaultViewComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(VaultViewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
