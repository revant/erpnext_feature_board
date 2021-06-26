import { DataSource } from '@angular/cdk/table';
import { BehaviorSubject } from 'rxjs';
import { ListFilter } from '../interfaces/filter.interface';

export class ListFilterDataSource extends DataSource<ListFilter> {
  subject = new BehaviorSubject<ListFilter[]>([]);

  constructor() {
    super();
  }

  connect() {
    return this.subject.asObservable();
  }

  disconnect() {
    this.subject.complete();
  }

  loadItems(items: any[]) {
    this.subject.next(items);
  }

  data() {
    return this.subject.value;
  }

  update(data: any[]) {
    this.subject.next(data);
  }
}
