import { HttpClient, HttpHeaders } from '@angular/common/http';
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

  update(person: Person) : Observable<any> {
    console.log(person);
    const httpOptions = {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' })
    };
    return this.http.put(this.apiUrl + '/' + person.id, person, httpOptions);
  }
}
