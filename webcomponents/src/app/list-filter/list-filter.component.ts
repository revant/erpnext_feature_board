import { Component, Inject, OnInit, ViewChild } from '@angular/core';
import { FormArray, FormBuilder, FormGroup } from '@angular/forms';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatTable } from '@angular/material/table';
import { FilterOperator, ListFilter } from '../interfaces/filter.interface';
import { ListFilterDataSource } from './list-filter.datasource';

@Component({
  selector: 'app-list-filter',
  templateUrl: './list-filter.component.html',
  styleUrls: ['./list-filter.component.scss'],
})
export class ListFilterComponent implements OnInit {
  @ViewChild('table', { static: true }) table?: MatTable<any>;

  displayedColumns: string[] = ['field', 'operator', 'value', 'clear'];
  dataSource: ListFilterDataSource = new ListFilterDataSource();

  local_data: any;
  fields: any;
  filters: any[] = [];
  operators = [
    FilterOperator.Equals,
    FilterOperator.NotEquals,
    FilterOperator.Like,
    FilterOperator.NotLike,
  ];

  rows: FormArray = this.fb.array([]);
  filtersForm: FormGroup = new FormGroup({});

  constructor(
    @Inject(MAT_DIALOG_DATA) public data: string[],
    public dialogRef: MatDialogRef<ListFilterComponent>,
    private fb: FormBuilder
  ) {}

  ngOnInit() {
    this.local_data = this.data;
    this.dataSource = new ListFilterDataSource();
    this.fields = this.local_data.field;
    if (this.local_data.filter?.length !== 0) {
      this.filters = this.local_data.filter?.map(
        ([field, operator, value]: string[]) => ({
          field,
          operator,
          value,
        })
      );
    }
    this.filtersForm = this.fb.group({ filters: this.rows });
    this.patch();
    this.dataSource = new ListFilterDataSource();
    this.updateDataSource();
  }

  patch() {
    const control = this.filtersForm?.get('filters') as FormArray;
    this.filters?.forEach((element: { [key: string]: string }) => {
      control.push(
        this.patchValues(element.field, element.operator, element.value)
      );
    });
  }

  patchValues(field: string, operator: string, value: string) {
    return this.fb.group({
      field: [field],
      operator: [operator],
      value: [value],
    });
  }

  clearFilters(event?: number) {
    if (event) {
      this.rows.removeAt(event);
    } else {
      while (this.rows.length !== 0) {
        this.rows.removeAt(0);
      }
    }
    this.filters = [];
    this.table?.renderRows();
  }

  addFilter(d?: ListFilter) {
    const row = this.fb.group({
      field: [d && d.field ? d.field : null, []],
      operator: [d && d.operator ? d.operator : null, []],
      value: [d && d.operator ? d.operator : null, []],
    });
    this.rows.push(row);
    this.updateDataSource();
  }

  updateDataSource() {
    this.dataSource.update(this.rows.controls);
  }

  applyFilter() {
    const filterObject = this.dataSource.subject.value;
    for (let i = 0; i < filterObject.length; i++) {
      const filtered = Object.values(filterObject[i].value as string).filter(
        (f) => f !== null
      );
      if (filtered.length === 3) {
        this.filters[i] = filtered;
      }
    }
    this.dialogRef.close({ data: this.filters });
  }

  snakeToTitleCase(str: string) {
    if (!str) return;

    return str
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }
}
