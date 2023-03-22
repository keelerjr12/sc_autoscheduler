import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { map, tap } from 'rxjs/operators';
import { ShellDuty, ShellFlyingLine } from '../models/shell_flying_line.model';
import { ConfigService } from './config.service';

@Injectable({
  providedIn: 'root'
})
export class ScheduleShellAPIService {
  private FLYING_ROUTE: string = 'flying_shell/';
  private DUTY_ROUTE: string = 'duty_shell/';

  constructor(private http: HttpClient, private config: ConfigService) { }

  getFlyingShell(date: Date) : Observable<ShellFlyingLine[]> {
    const url = this.config.getApiUrl() + this.FLYING_ROUTE;
    let params = new HttpParams();
    params = params.set('date', date.toISOString().split('T')[0]);
    console.log(params.get('date'));
    return this.http.get<ShellFlyingLine[]>(url, {params: params});
  }

  getDutyShell(date: Date) : Observable<ShellDuty[]> {
    const url = this.config.getApiUrl() + this.DUTY_ROUTE;
    let params = new HttpParams();
    params = params.set('date', date.toISOString().split('T')[0]);
    console.log(params.get('date'));
    return this.http.get<ShellDuty[]>(url, {params: params});
  }
}
