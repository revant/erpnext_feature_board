import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { map, switchMap } from 'rxjs/operators';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ListingService {
  constructor(
    private readonly http: HttpClient,
  ) { }

  findModels(
    model: string,
    filters: string[] = [],
    sortOrder = 'modified asc',
    pageNumber = 0,
    fields = ['name', 'owner', 'modified', 'modified_by'],
    pageSize = 10,
  ): Observable<any> {
    const blankFilters: any[] = [];
    const url = `/api/resource/${model}`;
    const headers = {};
    const offset = pageNumber * pageSize;
    const params = new HttpParams()
      .set('limit_start', offset.toString())
      .set('limit_page_length', pageSize.toString())
      .set('fields', JSON.stringify(fields))
      .set('filters', JSON.stringify(filters))
      .set('order_by', sortOrder);
    return this.http.get<{ data: unknown }>(url, { params, headers }).pipe(
      switchMap(listRes => {
        const countUrl = '/api/method/frappe.client.get_count';
        const countParams = new HttpParams()
          .set('doctype', model)
          .set('filters', JSON.stringify(blankFilters));

        return this.http
          .get<any>(countUrl, {
            headers,
            params: countParams,
          })
          .pipe(
            map(countRes => {
              return {
                docs: listRes.data,
                offset,
                length: countRes.message,
              };
            }),
          );
      }),
    );
  }

  findModelsById(id: string, model: string) {
    const url = `/api/resource/${model}/${id}`;
    const headers = {};
    return this.http.get<{ data: any }>(url, { headers });
  }
}
