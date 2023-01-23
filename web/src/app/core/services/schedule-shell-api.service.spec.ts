import { TestBed } from '@angular/core/testing';

import { ScheduleShellAPIService } from './schedule-shell-api.service';

describe('ScheduleShellAPIService', () => {
  let service: ScheduleShellAPIService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ScheduleShellAPIService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
