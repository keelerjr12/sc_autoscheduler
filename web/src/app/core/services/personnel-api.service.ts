import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { Person } from '../models/person.model';
import { ConfigService } from './config.service';

@Injectable({
  providedIn: 'root'
})
export class PersonnelAPIService {

  ROUTE = 'personnel/';

  constructor(private http: HttpClient, private config: ConfigService) { }

  getPersonnel() : Observable<Person[]> {
    const url = this.config.getApiUrl() + this.ROUTE;
    return this.http.get<Person[]>(url);
  }

  update(person: Person) : Observable<any> {
    const httpOptions = {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' })
    };

    const url = this.config.getApiUrl() + this.ROUTE + person.id;

    return this.http.put(url, person, httpOptions);
  }
}
