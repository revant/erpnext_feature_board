import { Component } from '@angular/core';

@Component({
  selector: 'app-improvement-list',
  templateUrl: './improvement-list.component.html',
  styleUrls: ['./improvement-list.component.css'],
})
export class ImprovementListComponent {
  fields = [
    'name',
    'number',
    'title',
    'deployment_status',
    'status',
    'repository',
  ];
  filterFields = [
    'name',
    'number',
    'title',
    'deployment_status',
    'status',
    'repository',
  ];
}
