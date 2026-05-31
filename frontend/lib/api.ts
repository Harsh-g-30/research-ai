import axios from "axios";

const API = axios.create({
  baseURL: "",  // empty — rewrites handle it
});

export interface ProductResult {
  name: string;
  brand?: string;
  price?: string;
  specs?: Record<string, string>;
  pros?: string[];
  cons?: string[];
  score?: number;
  reason?: string;
  source_urls?: string[];
}

export interface ResearchResponse {
  id: string;
  query: string;
  category: string;
  filters_applied: Record<string, unknown>;
  results: ProductResult[];
  summary: string;
  cached: boolean;
}

export interface FilterOption {
  key: string;
  label: string;
  type: string;
  options?: string[];
  min?: number;
  max?: number;
  unit?: string;
}

export interface FiltersResponse {
  category: string;
  filters: FilterOption[];
}

export const researchAPI = {
  getFilters: async (query: string): Promise<FiltersResponse> => {
    const res = await API.post("/api/research/filters", { query });
    return res.data;
  },

  research: async (
    query: string,
    filters: Record<string, unknown>
  ): Promise<ResearchResponse> => {
    const res = await API.post("/api/research/", { query, filters });
    return res.data;
  },

  getHistory: async () => {
    const res = await API.get("/api/research/history");
    return res.data;
  },
};