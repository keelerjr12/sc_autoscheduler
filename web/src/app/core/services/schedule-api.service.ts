import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { Schedule } from '../models/schedule.model';
import { ShellFlyingLine } from '../models/shell_flying_line.model';
import { ConfigService } from './config.service';

@Injectable({
  providedIn: 'root'
})
export class ScheduleAPIService {

  ROUTE = 'schedules/';

  constructor(private http: HttpClient, private config: ConfigService) { }

  getSchedules() : Observable<Schedule[]> {
    const url = this.config.getApiUrl() + this.ROUTE;

    return this.http.get<Schedule[]>(url);
  }

}
