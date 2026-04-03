import type { DailyResult } from "../api";

interface Props {
  results: DailyResult[];
}

const resultBadge = (result: string) => {
  switch (result) {
    case "win":
      return "bg-green-900/50 text-green-400";
    case "loss":
      return "bg-red-900/50 text-red-400";
    default:
      return "bg-gray-800 text-gray-500";
  }
};

const directionBadge = (dir: string | null) => {
  switch (dir) {
    case "long":
      return "text-green-400";
    case "short":
      return "text-red-400";
    default:
      return "text-gray-500";
  }
};

export default function ResultsTable({ results }: Props) {
  if (results.length === 0) {
    return <p className="text-gray-500 text-sm">No results to display.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm text-left">
        <thead>
          <tr className="text-gray-500 border-b border-gray-800/50">
            <th className="py-3 px-3 font-medium text-xs uppercase tracking-wider">Date</th>
            <th className="py-3 px-3 font-medium text-xs uppercase tracking-wider">Session H</th>
            <th className="py-3 px-3 font-medium text-xs uppercase tracking-wider">Session L</th>
            <th className="py-3 px-3 font-medium text-xs uppercase tracking-wider">Direction</th>
            <th className="py-3 px-3 font-medium text-xs uppercase tracking-wider">Entry</th>
            <th className="py-3 px-3 font-medium text-xs uppercase tracking-wider">TP</th>
            <th className="py-3 px-3 font-medium text-xs uppercase tracking-wider">SL</th>
            <th className="py-3 px-3 font-medium text-xs uppercase tracking-wider">Result</th>
          </tr>
        </thead>
        <tbody>
          {results.map((r, idx) => (
            <tr key={idx} className="border-b border-gray-800/50 hover:bg-gray-800/30">
              <td className="py-3 px-3 text-gray-300">{r.date}</td>
              <td className="py-3 px-3 text-gray-300">{r.session_high?.toFixed(1) ?? "—"}</td>
              <td className="py-3 px-3 text-gray-300">{r.session_low?.toFixed(1) ?? "—"}</td>
              <td className={`py-3 px-3 font-medium ${directionBadge(r.breakout_direction)}`}>
                {r.breakout_direction ?? "—"}
              </td>
              <td className="py-3 px-3 text-gray-300">{r.entry_price?.toFixed(1) ?? "—"}</td>
              <td className="py-3 px-3 text-gray-300">{r.tp_price?.toFixed(1) ?? "—"}</td>
              <td className="py-3 px-3 text-gray-300">{r.sl_price?.toFixed(1) ?? "—"}</td>
              <td className="py-3 px-3">
                <span className={`px-2.5 py-1 rounded-md text-xs font-semibold ${resultBadge(r.result)}`}>
                  {r.result}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
