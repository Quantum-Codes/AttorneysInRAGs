declare var Chart: any;
type Severity = "HIGH" | "MEDIUM" | "LOW";

interface ExtractedData {
  rawText?: string;
  docType?: string;
  pageURL?: string;
}

interface Violation {
  violating_rule: string;
  actual_rule: string;
  source: string;
  severity: Severity;
}

interface BackendResponse {
  summary: string;
  aggregations: {
    total_violations: number;
    high_severity: number;
    medium_severity: number;
    low_severity: number;
  };
  violations: Violation[];
}

/**
 * 1. The fetch function remains mostly the same, 
 * but we use explicit typing for the return.
 */
async function postData(url: string, payload: object): Promise<BackendResponse> {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return (await response.json()) as BackendResponse;
}

/**
 * 2. RenderDashboard now accepts the data as a parameter.
 * This ensures it only runs when data actually exists.
 */
const renderDashboard = (data: BackendResponse) => {
  /* === SEVERITY PIE CHART === */
  const severityCanvas = document.getElementById("severityChart") as HTMLCanvasElement;
  if (severityCanvas) {
    new Chart(severityCanvas, {
      type: "pie",
      data: {
        labels: ["High", "Medium", "Low"],
        datasets: [{
          data: [
            data.aggregations.high_severity,
            data.aggregations.medium_severity,
            data.aggregations.low_severity,
          ],
          backgroundColor: ["#ef4444", "#f59e0b", "#22c55e"],
          borderWidth: 0,
        }],
      },
      options: {
        plugins: { legend: { labels: { color: '#e5e7eb' } } }
      }
    });
  }

  /* === SOURCE BAR CHART === */
  const sourceCanvas = document.getElementById("sourceChart") as HTMLCanvasElement;
  if (sourceCanvas) {
    const sourceCount: Record<string, number> = {};
    data.violations.forEach((v) => {
      sourceCount[v.source] = (sourceCount[v.source] || 0) + 1;
    });

    new Chart(sourceCanvas, {
      type: "bar",
      data: {
        labels: Object.keys(sourceCount),
        datasets: [{
          label: "Violations",
          data: Object.values(sourceCount),
          backgroundColor: "#38bdf8",
        }],
      },
      options: {
        scales: {
          y: { beginAtZero: true, ticks: { color: '#94a3b8' } },
          x: { ticks: { color: '#94a3b8' } }
        },
        plugins: { legend: { labels: { color: '#e5e7eb' } } }
      }
    });
  }

  // UI Updates with null checking
  const safetyScoreEl = document.querySelector(".safety-score");
  if (safetyScoreEl) {
    const score = calculateRiskScore(
      data.aggregations.high_severity,
      data.aggregations.medium_severity,
      data.aggregations.low_severity
    );
    safetyScoreEl.innerHTML = `${score} %`;
  }

  const updateText = (selector: string, val: string | number) => {
    const el = document.querySelector(selector);
    if (el) el.innerHTML = `${val}`;
  };

  updateText(".violations", data.aggregations.total_violations);
  updateText(".risk-high", data.aggregations.high_severity);
  updateText(".risk-medium", data.aggregations.medium_severity);
  updateText(".risk-low", data.aggregations.low_severity);
  updateText(".summary", data.summary);

  /* === TABLE RENDER === */
  const table = document.getElementById("violationsTable");
  if (table) {
    table.innerHTML = data.violations.map(v => `
      <tr>
        <td>${v.violating_rule}</td>
        <td>${v.actual_rule}</td>
        <td>${v.source}</td>
        <td>
          <span class="badge badge-${v.severity.toLowerCase()}">${v.severity}</span>
        </td>
      </tr>
    `).join("");
  }
};

/**
 * 3. Execution Logic: The "Chain of Command"
 * Storage -> API -> Dashboard
 */
document.addEventListener("DOMContentLoaded", () => {
  chrome.storage.local.get(["rawText"], async (stored: ExtractedData) => {
    if (!stored.rawText) {
      console.error("No raw text found in storage.");
      return;
    }

    try {
      console.log("Sending text to API...");
      // Replace with your actual FastAPI endpoint
      const apiResult = await postData("https://your-api-url.com/analyze", {
        text: stored.rawText
      });

      console.log("API Success, rendering dashboard.");
      renderDashboard(apiResult);
    } catch (error) {
      console.error("Dashboard Loading Failed:", error);
    }
  });
});

export function calculateRiskScore(H: number, M: number, L: number): number {
  const weightedSum = (0.1053605 * H) + (0.051293 * M) + (0.0100503 * L);
  const riskScore = 100 * (1 - Math.exp(-weightedSum));
  return Number(riskScore.toFixed(2));
}
