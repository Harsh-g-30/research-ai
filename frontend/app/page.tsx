"use client";

import { useState } from "react";
import { Search, Zap, Brain, Filter } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { researchAPI, ResearchResponse, FiltersResponse } from "@/lib/api";
import FilterPanel from "@/components/FilterPanel";
import ResultsPanel from "@/components/ResultsPanel";

export default function Home() {
  const [query, setQuery] = useState("");
  const [step, setStep] = useState<"home" | "filters" | "results">("home");
  const [filters, setFilters] = useState<FiltersResponse | null>(null);
  const [appliedFilters, setAppliedFilters] = useState<Record<string, unknown>>({});
  const [results, setResults] = useState<ResearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState("");

  const handleSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setLoadingMsg("Analyzing your query...");
    try {
      const f = await researchAPI.getFilters(query);
      setFilters(f);
      setStep("filters");
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

const handleResearch = async () => {
  setLoading(true);
  setStep("results");
  const messages = [
    "🧠 Extracting intent...",
    "🔍 Generating search queries...",
    "🌐 Searching the web...",
    "📦 Extracting product data...",
    "🏆 Ranking and explaining...",
  ];
  let i = 0;
  setLoadingMsg(messages[0]);
  const interval = setInterval(() => {
    i = (i + 1) % messages.length;
    setLoadingMsg(messages[i]);
  }, 4000);

  try {
    const res = await researchAPI.research(query, appliedFilters);
    setResults(res);
  } catch (e) {
    console.error(e);
    setStep("filters"); // go back to filters on error
  } finally {
    clearInterval(interval);
    setLoading(false);
    setLoadingMsg("");
  }
};

  const handleReset = () => {
    setQuery("");
    setStep("home");
    setFilters(null);
    setResults(null);
    setAppliedFilters({});
  };

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div
            className="flex items-center gap-2 cursor-pointer"
            onClick={handleReset}
          >
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-xl text-gray-900">ResearchAI</span>
          </div>
          <nav className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={handleReset}>
              New Search
            </Button>
          </nav>
        </div>
      </header>

      {/* Home Step */}
      {step === "home" && (
        <div className="max-w-3xl mx-auto px-6 pt-24 pb-12">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 bg-indigo-50 text-indigo-700 px-4 py-2 rounded-full text-sm font-medium mb-6">
              <Zap className="w-4 h-4" />
              AI-Powered Product Research
            </div>
            <h1 className="text-5xl font-bold text-gray-900 mb-4 leading-tight">
              Find the perfect product,{" "}
              <span className="text-indigo-600">instantly</span>
            </h1>
            <p className="text-xl text-gray-500 max-w-2xl mx-auto">
              Describe what you need. Our AI researches the web, compares
              options, and explains exactly what to buy — and why.
            </p>
          </div>

          <div className="flex gap-3">
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              placeholder="e.g. best laptop for video editing under ₹80,000"
              className="h-14 text-base px-5 rounded-xl border-gray-200 shadow-sm"
              disabled={loading}
            />
            <Button
              onClick={handleSearch}
              disabled={loading || !query.trim()}
              className="h-14 px-6 bg-indigo-600 hover:bg-indigo-700 rounded-xl"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Search className="w-5 h-5" />
              )}
            </Button>
          </div>

          {/* Example queries */}
          <div className="mt-6 flex flex-wrap gap-2 justify-center">
            {[
              "Gaming laptop under ₹70,000",
              "Wireless headphones for commuting",
              "DSLR camera for beginners",
              "Standing desk for home office",
            ].map((example) => (
              <button
                key={example}
                onClick={() => setQuery(example)}
                className="text-sm text-gray-500 bg-white border border-gray-200 px-3 py-1.5 rounded-full hover:border-indigo-300 hover:text-indigo-600 transition-colors"
              >
                {example}
              </button>
            ))}
          </div>

          {/* Features */}
          <div className="mt-20 grid grid-cols-3 gap-6">
            {[
              {
                icon: "🧠",
                title: "AI Research Agent",
                desc: "LangGraph agent searches the web and extracts real product data",
              },
              {
                icon: "🎛️",
                title: "Smart Filters",
                desc: "Dynamic filters auto-generated based on product category",
              },
              {
                icon: "📊",
                title: "Compare & Decide",
                desc: "Side-by-side comparison with explainable AI recommendations",
              },
            ].map((f) => (
              <div
                key={f.title}
                className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm text-center"
              >
                <div className="text-3xl mb-3">{f.icon}</div>
                <h3 className="font-semibold text-gray-900 mb-1">{f.title}</h3>
                <p className="text-sm text-gray-500">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filter Step */}
      {step === "filters" && filters && (
        <FilterPanel
          query={query}
          filters={filters}
          appliedFilters={appliedFilters}
          setAppliedFilters={setAppliedFilters}
          onResearch={handleResearch}
          loading={loading}
        />
      )}

      {/* Results Step */}
      {step === "results" && (
        <ResultsPanel
          query={query}
          results={results}
          loading={loading}
          loadingMsg={loadingMsg}
          onReset={handleReset}
        />
      )}
    </main>
  );
}