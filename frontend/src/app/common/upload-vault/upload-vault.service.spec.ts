import { TestBed } from '@angular/core/testing';

import { UploadVaultService } from './upload-vault.service';

describe('UploadVaultService', () => {
  let service: UploadVaultService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(UploadVaultService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
