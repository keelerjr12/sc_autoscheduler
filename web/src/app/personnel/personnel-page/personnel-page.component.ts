import { Component } from '@angular/core';
import { PersonnelAPIService } from 'src/app/core/services/personnel-api.service';
import { PersonView } from '../shared/personview.model';

@Component({
  selector: 'sc-personnel-page',
  templateUrl: './personnel-page.component.html',
  styleUrls: ['./personnel-page.component.css']
})
export class PersonnelPageComponent {
  persons: PersonView[] = [];
  assigned_orgs: string[];
  quals: string[];
  qual_options: string[];
  isEditable: boolean[] = [];

  constructor(private personAPI: PersonnelAPIService) {

    this.quals = [
      'Operations Supervisor', 'SOF', 'RSU Controller', 'RSU Observer', 'IPC Pilot', 'FPC Pilot', 'FCF Pilot', 'PIT IP', 'SEFE'
    ];

    this.qual_options = ['', 'X']

    this.assigned_orgs = [
      ' ', 'M', 'N', 'O', 'P', 'X'
    ];
  }

  ngOnInit() {
    this.personAPI.getPersonnel().subscribe(persons => {
      this.persons = persons.map(person_dto => {

        const mapped_quals = new Map(this.quals.map(qual => {
          let val = '';

          person_dto.quals.forEach(dto_qual => {
            if (dto_qual.name == qual)
              val = 'X';
              return;
          });

          return [qual, val] 
        }));

        const person_view: PersonView = {
          id: person_dto.id,
          name: person_dto.last_name + ', ' + person_dto.first_name,
          assigned_org: person_dto.assigned_org ? person_dto.assigned_org.name : null,
          quals: mapped_quals
        };

        console.log(person_view.quals);
        return person_view;
      });

      this.isEditable = this.persons.map(() => {
        return false;
      });
    });
  }

  onEdit(row: number) {
    this.isEditable[row] = true;
  }

  onSave(row: number) {
    this.isEditable[row] = false;
    console.log('Updating: ' + this.persons[row].name);
    console.log(this.persons[row]);
  }
}
