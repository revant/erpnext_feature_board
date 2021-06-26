import { ListingData } from "./listing-data.interface";

export interface ListResponse {
  docs: ListingData[];
  length: number;
  offset: number;
}
