import { DataSource, CollectionViewer } from '@angular/cdk/collections';
import { ListingService } from './listing.service';
import { map, catchError, finalize } from 'rxjs/operators';
import { BehaviorSubject, Observable, of } from 'rxjs';
import { ListingData } from '../interfaces/listing-data.interface';
import { ListResponse } from '../interfaces/listing-response.interface';
import { MatPaginator } from '@angular/material/paginator';

export class ListingDataSource extends DataSource<ListingData> {
  data: ListingData[] = [];
  length: number = 0;
  offset: number = 0;
  itemSubject = new BehaviorSubject<ListingData[]>([]);
  loadingSubject = new BehaviorSubject<boolean>(false);
  paginator?: MatPaginator;

  loading$ = this.loadingSubject.asObservable();

  constructor(
    private readonly model: string,
    private readonly fields: string[],
    private readonly listingService: ListingService
  ) {
    super();
  }

  connect(collectionViewer: CollectionViewer): Observable<ListingData[]> {
    return this.itemSubject.asObservable();
  }

  disconnect(collectionViewer: CollectionViewer): void {
    this.itemSubject.complete();
    this.loadingSubject.complete();
  }

  loadItems(
    filter: string[] = [],
    sortOrder = 'modified asc',
    pageIndex = 0,
    pageSize = 10
  ) {
    this.loadingSubject.next(true);
    this.listingService
      .findModels(
        this.model,
        filter,
        sortOrder,
        pageIndex,
        this.fields,
        pageSize
      )
      .pipe(
        map((res: ListResponse) => {
          this.data = res.docs;
          this.offset = res.offset;
          this.length = res.length;
          return res.docs;
        }),
        catchError(() => of([])),
        finalize(() => this.loadingSubject.next(false))
      )
      .subscribe((items) => this.itemSubject.next(items));
  }
}
