import { TestBed } from '@angular/core/testing';

import { ProtectedKeychainStorageService } from './protected-keychain-storage.service';

describe('ProtectedKeychainStorageService', () => {
  let service: ProtectedKeychainStorageService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ProtectedKeychainStorageService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
