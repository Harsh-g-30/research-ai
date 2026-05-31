"use client";

import { ExternalLink, RotateCcw, Zap, Star } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ResearchResponse } from "@/lib/api";

interface Props {
  query: string;
  results: ResearchResponse | null;
  loading: boolean;
  loadingMsg: string;
  onReset: () => void;
}

export default function ResultsPanel({
  query,
  results,
  loading,
  loadingMsg,
  onReset,
}: Props) {
  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-24 text-center">
        <div className="w-16 h-16 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto mb-6" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          Researching for you...
        </h2>
        <p className="text-gray-500 animate-pulse">{loadingMsg}</p>
      </div>
    );
  }

  if (!results) return null;

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <h2 className="text-2xl font-bold text-gray-900">
              Results for &quot;{query}&quot;
            </h2>
            {results.cached && (
              <Badge variant="secondary" className="text-xs">
                <Zap className="w-3 h-3 mr-1" />
                Cached
              </Badge>
            )}
          </div>
          <p className="text-gray-500 text-sm">
            {results.results.length} products found · {results.category}
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={onReset}>
          <RotateCcw className="w-4 h-4 mr-1" />
          New Search
        </Button>
      </div>

      {/* AI Summary */}
      {results.summary && (
        <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-4 mb-6">
          <p className="text-sm font-medium text-indigo-800 mb-1">
            🧠 AI Summary
          </p>
          <p className="text-indigo-700 text-sm leading-relaxed">
            {results.summary}
          </p>
        </div>
      )}

      {/* Product Cards */}
      <div className="space-y-4">
        {results.results.map((product, idx) => (
          <div
            key={idx}
            className="bg-white rounded-2xl border border-gray-200 p-6 shadow-sm card-hover"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 bg-indigo-100 rounded-lg flex items-center justify-center text-indigo-700 font-bold text-sm flex-shrink-0">
                  {idx + 1}
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900 text-lg leading-tight">
                    {product.name}
                  </h3>
                  {product.brand && (
                    <p className="text-sm text-gray-500">{product.brand}</p>
                  )}
                </div>
              </div>
              <div className="text-right flex-shrink-0 ml-4">
                {product.price && (
                  <p className="text-xl font-bold text-gray-900">
                    {product.price}
                  </p>
                )}
                {product.score && (
                  <div className="flex items-center gap-1 justify-end mt-1">
                    <Star className="w-3.5 h-3.5 text-yellow-500 fill-yellow-500" />
                    <span className="text-sm font-medium text-gray-700">
                      {product.score}/10
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Specs */}
            {product.specs && Object.keys(product.specs).length > 0 && (
              <div className="flex flex-wrap gap-2 mb-3">
                {Object.entries(product.specs).map(([k, v]) => (
                  <span
                    key={k}
                    className="text-xs bg-gray-100 text-gray-600 px-2.5 py-1 rounded-full"
                  >
                    {k}: {v}
                  </span>
                ))}
              </div>
            )}

            {/* Reason */}
            {product.reason && (
              <p className="text-sm text-gray-600 mb-3 leading-relaxed">
                {product.reason}
              </p>
            )}

            {/* Pros & Cons */}
            <div className="grid grid-cols-2 gap-3 mb-3">
              {product.pros && product.pros.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-green-700 mb-1">
                    ✅ Pros
                  </p>
                  <ul className="space-y-0.5">
                    {product.pros.map((pro, i) => (
                      <li key={i} className="text-xs text-gray-600">
                        • {pro}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {product.cons && product.cons.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-red-600 mb-1">
                    ❌ Cons
                  </p>
                  <ul className="space-y-0.5">
                    {product.cons.map((con, i) => (
                      <li key={i} className="text-xs text-gray-600">
                        • {con}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Sources */}
            {product.source_urls && product.source_urls.length > 0 && (
              <div className="flex flex-wrap gap-2 pt-3 border-t border-gray-100">
                {product.source_urls.slice(0, 2).map((url, i) => {
                  try {
                    return (
                      <a
                        key={i}
                        href={url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-800"
                      >
                        <ExternalLink className="w-3 h-3" />
                        {new URL(url).hostname.replace("www.", "")}
                      </a>
                    );
                  } catch {
                    return null;
                  }
                })}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}