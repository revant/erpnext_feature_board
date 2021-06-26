import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-improvement-list',
  templateUrl: './improvement-list.component.html',
  styleUrls: ['./improvement-list.component.css']
})
export class ImprovementListComponent implements OnInit {
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
    'repository',
    'number',
  ];

  constructor() { }

  ngOnInit(): void {
  }

}
