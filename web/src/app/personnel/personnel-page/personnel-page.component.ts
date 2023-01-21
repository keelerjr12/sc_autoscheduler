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
  personModels: Map<number, Person> = new Map<number, Person>();
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
      this.personModels = new Map(persons.map(person => [person.id, person]));

      this.personViewModels = persons.map(person_dto => {
        const mapped_quals = new Map(this.quals.map(qual => {
          const qualified = person_dto.quals.filter(dto_qual => dto_qual == qual).length > 0 ? 'X' : ''
          return [qual, qualified] 
        }));

        const person_view: PersonView = {
          id: person_dto.id,
          name: person_dto.last_name + ', ' + person_dto.first_name,
          assigned_org: person_dto.assigned_org,
          quals: mapped_quals
        };

        return person_view;
      });

      this.personViewModels.sort((a, b) => a.name.localeCompare(b.name))

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

    const personVM = this.personViewModels[row];
    const updatedQuals = [...personVM.quals].filter(([_, value]) => value == 'X').map((key, _) => key[0]);

    let personModel = this.personModels.get(personVM.id);
    if (personModel) {
      personModel.assigned_org = personVM.assigned_org;
      personModel.quals = updatedQuals;
      this.personAPI.update(personModel).subscribe();
    }
  }
}
