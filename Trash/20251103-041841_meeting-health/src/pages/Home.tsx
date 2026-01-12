import { useEffect, useState } from "react";

interface Issue {
  type: string;
  severity: string;
  message: string;
}

interface Meeting {
  meeting_id: string;
  status: string;
  issues: Issue[];
  block_count: number;
  expected_blocks: number;
  processing_status: string;
}

interface HealthReport {
  generated_at: string;
  summary: {
    total_scanned: number;
    critical_issues: number;
    high_issues: number;
    medium_issues: number;
    healthy: number;
  };
  critical: Meeting[];
  high: Meeting[];
  medium: Meeting[];
}

export default function Home() {
  const [report, setReport] = useState<HealthReport | null>(null);

  useEffect(() => {
    fetch("/api/health")
      .then(res => res.json())
      .then(setReport);
  }, []);

  if (!report) return <div className="p-8">Loading...</div>;

  const getSeverityBadge = (severity: string) => {
    const colors = {
      CRITICAL: "bg-red-100 text-red-800 border-red-300",
      HIGH: "bg-orange-100 text-orange-800 border-orange-300",
      MEDIUM: "bg-yellow-100 text-yellow-800 border-yellow-300"
    };
    return colors[severity as keyof typeof colors] || "bg-gray-100 text-gray-800";
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-2">Meeting System Health Dashboard</h1>
        <p className="text-gray-600 mb-8">
          Last updated: {new Date(report.generated_at).toLocaleString()}
        </p>

        {/* Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border">
            <div className="text-3xl font-bold text-gray-700">{report.summary.total_scanned}</div>
            <div className="text-sm text-gray-600 mt-1">Total Scanned</div>
          </div>
          <div className="bg-red-50 p-6 rounded-lg shadow-sm border-2 border-red-200">
            <div className="text-3xl font-bold text-red-600">{report.summary.critical_issues}</div>
            <div className="text-sm text-red-700 mt-1">Critical</div>
          </div>
          <div className="bg-orange-50 p-6 rounded-lg shadow-sm border-2 border-orange-200">
            <div className="text-3xl font-bold text-orange-600">{report.summary.high_issues}</div>
            <div className="text-sm text-orange-700 mt-1">High</div>
          </div>
          <div className="bg-yellow-50 p-6 rounded-lg shadow-sm border-2 border-yellow-200">
            <div className="text-3xl font-bold text-yellow-600">{report.summary.medium_issues}</div>
            <div className="text-sm text-yellow-700 mt-1">Medium</div>
          </div>
          <div className="bg-green-50 p-6 rounded-lg shadow-sm border-2 border-green-200">
            <div className="text-3xl font-bold text-green-600">{report.summary.healthy}</div>
            <div className="text-sm text-green-700 mt-1">Healthy</div>
          </div>
        </div>

        {/* Critical Issues Table */}
        {report.critical.length > 0 && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-red-600 mb-4">🚨 Critical Issues</h2>
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <table className="w-full">
                <thead className="bg-red-50 border-b-2 border-red-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-bold text-red-700 uppercase">Meeting ID</th>
                    <th className="px-6 py-3 text-left text-xs font-bold text-red-700 uppercase">Blocks</th>
                    <th className="px-6 py-3 text-left text-xs font-bold text-red-700 uppercase">Issues</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {report.critical.slice(0, 10).map((meeting, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="font-mono text-sm font-semibold text-gray-900">{meeting.meeting_id}</div>
                        <div className="text-xs text-gray-500 mt-1">
                          Processed: {meeting.processed_at || 'Unknown'}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm">
                          <span className={meeting.block_count === 0 ? "text-red-600 font-bold" : "text-gray-700"}>
                            {meeting.block_count}
                          </span>
                          <span className="text-gray-500"> / {meeting.expected_blocks}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="space-y-1">
                          {meeting.issues.map((issue, i) => (
                            <div key={i} className="flex items-start gap-2">
                              <span className={getSeverityBadge(issue.severity)}>
                                {issue.severity}
                              </span>
                              <span className="text-sm text-gray-700">{issue.message}</span>
                            </div>
                          ))}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {report.critical.length > 10 && (
                <div className="px-6 py-3 bg-gray-50 text-sm text-gray-600 text-center border-t">
                  + {report.critical.length - 10} more critical issues
                </div>
              )}
            </div>
          </div>
        )}

        {/* High Priority Issues Table */}
        {report.high.length > 0 && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-orange-600 mb-4">⚠️ High Priority Issues</h2>
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <table className="w-full">
                <thead className="bg-orange-50 border-b-2 border-orange-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-bold text-orange-700 uppercase">Meeting ID</th>
                    <th className="px-6 py-3 text-left text-xs font-bold text-orange-700 uppercase">Blocks</th>
                    <th className="px-6 py-3 text-left text-xs font-bold text-orange-700 uppercase">Issues</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {report.high.slice(0, 10).map((meeting, idx) => (
                    <tr key={idx} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="font-mono text-sm font-semibold text-gray-900">{meeting.meeting_id}</div>
                        <div className="text-xs text-gray-500 mt-1">
                          Processed: {meeting.processed_at || 'Unknown'}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm">
                          <span className="text-gray-700">{meeting.block_count}</span>
                          <span className="text-gray-500"> / {meeting.expected_blocks}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="space-y-1">
                          {meeting.issues.map((issue, i) => (
                            <div key={i} className="flex items-start gap-2">
                              <span className={getSeverityBadge(issue.severity)}>
                                {issue.severity}
                              </span>
                              <span className="text-sm text-gray-700">{issue.message}</span>
                            </div>
                          ))}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {report.high.length > 10 && (
                <div className="px-6 py-3 bg-gray-50 text-sm text-gray-600 text-center border-t">
                  + {report.high.length - 10} more high priority issues
                </div>
              )}
            </div>
          </div>
        )}

        {/* All Clear */}
        {report.critical.length === 0 && report.high.length === 0 && report.medium.length === 0 && (
          <div className="bg-green-50 p-12 rounded-lg border-2 border-green-500 text-center">
            <div className="text-6xl mb-4">✅</div>
            <div className="text-3xl font-bold text-green-600 mb-2">All Systems Healthy</div>
            <div className="text-lg text-gray-700">
              No issues detected in the last {report.summary.total_scanned} meetings
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
