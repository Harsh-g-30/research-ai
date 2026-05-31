"use client";

import { Filter, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { FiltersResponse } from "@/lib/api";

interface Props {
  query: string;
  filters: FiltersResponse;
  appliedFilters: Record<string, unknown>;
  setAppliedFilters: (f: Record<string, unknown>) => void;
  onResearch: () => void;
  loading: boolean;
}

export default function FilterPanel({
  query,
  filters,
  appliedFilters,
  setAppliedFilters,
  onResearch,
  loading,
}: Props) {
  const updateFilter = (key: string, value: unknown) => {
    setAppliedFilters({ ...appliedFilters, [key]: value });
  };

  return (
    <div className="max-w-3xl mx-auto px-6 py-12">
      <div className="mb-8">
        <Badge variant="secondary" className="mb-3">
          <Filter className="w-3 h-3 mr-1" />
          {filters.category}
        </Badge>
        <h2 className="text-2xl font-bold text-gray-900 mb-1">
          Refine your search
        </h2>
        <p className="text-gray-500 text-sm">
          &quot;{query}&quot; — adjust filters or search directly
        </p>
      </div>

      <div className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm mb-6">
        <div className="grid grid-cols-1 gap-5">
          {filters.filters.map((filter) => (
            <div key={filter.key}>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {filter.label}
                {filter.unit && (
                  <span className="text-gray-400 font-normal ml-1">
                    ({filter.unit})
                  </span>
                )}
              </label>

              {filter.type === "range" && (
                <div className="flex items-center gap-3">
                  <input
                    type="number"
                    placeholder={`Min ${filter.min ?? ""}`}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                    onChange={(e) =>
                      updateFilter(`${filter.key}_min`, e.target.value)
                    }
                  />
                  <span className="text-gray-400">—</span>
                  <input
                    type="number"
                    placeholder={`Max ${filter.max ?? ""}`}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                    onChange={(e) =>
                      updateFilter(`${filter.key}_max`, e.target.value)
                    }
                  />
                </div>
              )}

              {filter.type === "select" && filter.options && (
                <select
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm bg-white"
                  onChange={(e) => updateFilter(filter.key, e.target.value)}
                  defaultValue=""
                >
                  <option value="">Any</option>
                  {filter.options.map((opt) => (
                    <option key={opt} value={opt}>
                      {opt}
                    </option>
                  ))}
                </select>
              )}

              {filter.type === "multiselect" && filter.options && (
                <div className="flex flex-wrap gap-2">
                  {filter.options.map((opt) => (
                    <button
                      key={opt}
                      onClick={() => {
                        const current =
                          (appliedFilters[filter.key] as string[]) || [];
                        const updated = current.includes(opt)
                          ? current.filter((v) => v !== opt)
                          : [...current, opt];
                        updateFilter(filter.key, updated);
                      }}
                      className={`text-sm px-3 py-1.5 rounded-full border transition-colors ${
                        ((appliedFilters[filter.key] as string[]) || []).includes(opt)
                          ? "bg-indigo-600 text-white border-indigo-600"
                          : "bg-white text-gray-600 border-gray-200 hover:border-indigo-300"
                      }`}
                    >
                      {opt}
                    </button>
                  ))}
                </div>
              )}

              {filter.type === "boolean" && (
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    className="w-4 h-4 accent-indigo-600"
                    onChange={(e) =>
                      updateFilter(filter.key, e.target.checked)
                    }
                  />
                  <span className="text-sm text-gray-600">
                    Yes, required
                  </span>
                </label>
              )}
            </div>
          ))}
        </div>
      </div>

      <Button
        onClick={onResearch}
        disabled={loading}
        className="w-full h-12 bg-indigo-600 hover:bg-indigo-700 rounded-xl text-base"
      >
        {loading ? (
          <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
        ) : (
          <>
            Find Best Matches
            <ArrowRight className="w-4 h-4 ml-2" />
          </>
        )}
      </Button>
    </div>
  );
}