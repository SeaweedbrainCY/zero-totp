import { TestBed } from '@angular/core/testing';

import { LocalVaultV1Service } from './LocalVaultv1Service.service';

describe('LocalVaultV1Service', () => {
  let service: LocalVaultV1Service;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(LocalVaultV1Service);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
