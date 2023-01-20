import { Component } from '@angular/core';
import { Person } from 'src/app/core/models/person.model';
import { PersonnelAPIService } from 'src/app/core/services/personnel-api.service';
import { PersonView } from '../shared/personview.model';

@Component({
  selector: 'sc-personnel-page',
  templateUrl: './personnel-page.component.html',
  styleUrls: ['./personnel-page.component.css']
})
export class PersonnelPageComponent {
  personViewModels: PersonView[] = [];
  personModels: Person[] = [];
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
      this.personModels = persons;
      console.log(this.personModels)
      this.personViewModels = persons.map(person_dto => {

        const mapped_quals = new Map(this.quals.map(qual => {
          let val = '';

          person_dto.quals.forEach(dto_qual => {
            if (dto_qual == qual)
              val = 'X';
              return;
          });

          return [qual, val] 
        }));

        const person_view: PersonView = {
          id: person_dto.id,
          name: person_dto.last_name + ', ' + person_dto.first_name,
          assigned_org: person_dto.assigned_org,
          quals: mapped_quals
        };

        console.log(person_view.quals);
        return person_view;
      });

      this.isEditable = this.personViewModels.map(() => {
        return false;
      });
    });
  }

  onEdit(row: number) {
    this.isEditable[row] = true;
  }

  onSave(row: number) {
    this.isEditable[row] = false;

    const personViewModel = this.personViewModels[row];
    this.personModels[row].assigned_org = personViewModel.assigned_org;

    const updatedQuals: string[] = [];
    personViewModel.quals.forEach((key, value) => {
      if (key === 'X')
        updatedQuals.push(value);
    });

    this.personModels[row].quals = updatedQuals;

    this.personAPI.update(this.personModels[row]).subscribe();
  }
}
