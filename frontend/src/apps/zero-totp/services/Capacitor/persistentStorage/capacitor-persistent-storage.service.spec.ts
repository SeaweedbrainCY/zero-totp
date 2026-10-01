import { TestBed } from '@angular/core/testing';

import { CapacitorPersistentStorageService } from './capacitor-persistent-storage.service';

describe('CapacitorPersistentStorageService', () => {
  let service: CapacitorPersistentStorageService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(CapacitorPersistentStorageService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
