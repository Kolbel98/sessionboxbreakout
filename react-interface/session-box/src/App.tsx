import { useState } from "react";
import BacktestForm from "./components/BacktestForm";
import SummaryPanel from "./components/SummaryPanel";
import ResultsTable from "./components/ResultsTable";
import { fetchBacktest } from "./api";
import type { BacktestParams, BacktestResponse } from "./api";

function App() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<BacktestResponse | null>(null);

  const handleSubmit = async (params: BacktestParams) => {
    setLoading(true);
    setError(null);
    setData(null);

    try {
      const response = await fetchBacktest(params);
      setData(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen text-white overflow-hidden">
      {/* Radial gradient background */}
      <div className="fixed inset-0 bg-gray-950" />
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_center,_rgba(99,102,241,0.15)_0%,_transparent_60%)]" />

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center px-6 py-16">
        {/* Hero */}
        <h1 className="text-6xl font-extrabold tracking-tight text-center mb-2">
          Session<span className="text-indigo-400">Box</span>
        </h1>
        <p className="text-lg text-gray-500 mb-12">Breakout Strategy Backtester</p>

        {/* Form */}
        <div className="w-full max-w-xl bg-gray-900/70 backdrop-blur-sm border border-gray-800/50 rounded-2xl p-8 mb-8">
          <BacktestForm onSubmit={handleSubmit} loading={loading} />
        </div>

        {/* Error */}
        {error && (
          <div className="w-full max-w-3xl bg-red-900/30 border border-red-800 text-red-400 px-5 py-4 rounded-xl text-sm mb-8">
            {error}
          </div>
        )}

        {/* Results */}
        {data && data.summary && data.summary.total_days > 0 && (
          <div className="w-full max-w-3xl space-y-8">
            <SummaryPanel
              summary={data.summary}
              slDistance={data.sl_distance}
              tpDistance={data.tp_distance}
            />
            <div className="bg-gray-900/70 backdrop-blur-sm border border-gray-800/50 rounded-2xl p-6">
              <h2 className="text-xl font-semibold mb-5">Daily Results</h2>
              <ResultsTable results={data.results} />
            </div>
          </div>
        )}

        {data && data.message && (
          <div className="w-full max-w-3xl bg-gray-900/70 backdrop-blur-sm border border-gray-800/50 rounded-2xl p-8 text-gray-500 text-sm text-center">
            {data.message}
          </div>
        )}

        {!data && !error && !loading && (
          <div className="w-full max-w-3xl bg-gray-900/40 border border-gray-800/30 rounded-2xl p-16 text-center">
            <p className="text-gray-600 text-lg">Configure parameters and run backtest</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
