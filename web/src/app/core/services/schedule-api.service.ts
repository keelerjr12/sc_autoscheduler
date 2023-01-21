import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { Schedule } from '../models/schedule.model';

@Injectable({
  providedIn: 'root'
})
export class ScheduleAPIService {

  apiUrl = 'http://localhost:8000/api/schedules'

  constructor(private http: HttpClient) { }

  getSchedules() : Observable<Schedule[]> {

    return this.http.get<Schedule[]>(this.apiUrl);
  }
}
