import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { ShellFlyingLine } from '../models/shell_flying_line.model';
import { ConfigService } from './config.service';

@Injectable({
  providedIn: 'root'
})
export class ScheduleShellAPIService {
  private ROUTE: string = 'shell/';

  constructor(private http: HttpClient, private config: ConfigService) { }

  getFlyingShell() : Observable<ShellFlyingLine[]> {
    const url = this.config.getApiUrl() + this.ROUTE;
    return this.http.get<ShellFlyingLine[]>(url);
  }
}
