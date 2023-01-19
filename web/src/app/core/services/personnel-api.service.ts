import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { Person } from '../models/person.model';

@Injectable({
  providedIn: 'root'
})
export class PersonnelAPIService {

  apiUrl = 'http://localhost:8000/api/personnel'

  constructor(private http: HttpClient) { }

  getPersonnel() : Observable<Person[]> {
    return this.http.get<Person[]>(this.apiUrl);
  }
}
