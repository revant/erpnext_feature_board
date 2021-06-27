import { Component, Input, OnInit, ViewChild } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { MatPaginator } from '@angular/material/paginator';
import { MatSort } from '@angular/material/sort';
import { ListFilterComponent } from '../list-filter/list-filter.component';
import { ListingDataSource } from './data-list.datasource';
import { ListingService } from './listing.service';
@Component({
  selector: 'app-data-list',
  templateUrl: './data-list.component.html',
  styleUrls: ['./data-list.component.scss'],
})
export class DataListComponent implements OnInit {
  @Input() filterFields = ['name'];
  @Input() doctype = 'Activity Log';
  @Input() fields = ['name', 'modified', 'owner', 'modified_by'];
  @ViewChild(MatPaginator, { static: true }) paginator?: MatPaginator;
  @ViewChild(MatSort, { static: true }) sort?: MatSort;
  dataSource = new ListingDataSource(
    this.doctype,
    this.fields,
    this.listingService
  );
  filters: string[] = [];

  constructor(
    private readonly listingService: ListingService,
    private readonly dialog: MatDialog
  ) {}

  ngOnInit() {
    this.dataSource = new ListingDataSource(
      this.doctype,
      this.fields,
      this.listingService
    );
    this.dataSource.loadItems();
  }

  getUpdate(event?: { pageIndex: number; pageSize: number }) {
    this.dataSource?.loadItems(
      this.filters,
      `${this.sort?.active || 'modified'} ${this.sort?.direction || 'asc'}`,
      event?.pageIndex || this.paginator?.pageIndex,
      event?.pageSize || this.paginator?.pageSize
    );
  }

  setFilter() {
    const data = {
      field: this.filterFields,
      filter: this.filters,
    };
    const dialogRef = this.dialog.open(ListFilterComponent, {
      data,
      minWidth: '80%',
      height: '75%',
    });

    dialogRef.afterClosed().subscribe((filter) => {
      this.filters = filter?.data;
      this.dataSource?.loadItems(this.filters);
      this.paginator?.firstPage();
    });
  }

  snakeToTitleCase(str: string) {
    if (!str) return;

    return str
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  kebabCase(str: string) {
    if (!str) return;

    return str
      .replace(/([a-z])([A-Z])/g, '$1-$2')
      .replace(/\s+/g, '-')
      .toLowerCase();
  }
}
