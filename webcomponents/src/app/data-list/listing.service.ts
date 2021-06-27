import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { map, switchMap } from 'rxjs/operators';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ListingService {
  constructor(private readonly http: HttpClient) {}

  findModels(
    model: string,
    filters: string[] = [],
    sortOrder = 'modified asc',
    pageNumber = 0,
    fields = ['name', 'owner', 'modified', 'modified_by'],
    pageSize = 10
  ): Observable<any> {
    const url = `/api/method/erpnext_feature_board.www.improvements.get_improvements`;
    const headers = {};
    const offset = pageNumber * pageSize;
    const params = new HttpParams()
      .set('doctype', 'Improvement')
      .set('limit_start', offset.toString())
      .set('limit_page_length', pageSize.toString())
      .set('fields', JSON.stringify(fields))
      .set('filters', JSON.stringify(filters))
      .set('order_by', sortOrder);
    return this.http
      .get<{ message: { docs: any[]; length: number } }>(url, {
        params,
        headers,
      })
      .pipe(
        map((res) => {
          return {
            docs: res.message?.docs,
            offset,
            length: res.message?.length,
          };
        })
      );
  }

  findModelsById(id: string, model: string) {
    const url = `/api/resource/${model}/${id}`;
    const headers = {};
    return this.http.get<{ data: any }>(url, { headers });
  }
}
