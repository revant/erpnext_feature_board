export interface ListFilter {
  field?: string;
  operator?: string;
  value?: string;
}

export enum FilterOperator {
  Equals = '=',
  NotEquals = '!=',
  Like = 'like',
  NotLike = 'not like',
}
