// Top-level dashboard shell for the Fello Intelligence frontend.
import { useState } from "react";

import AccountCard from "./components/AccountCard";
import InputPanel from "./components/InputPanel";
import UnresolvedCard from "./components/UnresolvedCard";

const API_BASE_URL = "http://localhost:8000";
const mockRecentVisitors = [
  {
    id: "visitor_001",
    label: "HubSpot",
    ip: "34.201.12.88",
    pages: ["/pricing", "/ai-sales-agent", "/case-studies"],
    score: 8.5,
    time_on_site_seconds: 222,
    visits_this_week: 3,
  },
  {
    id: "visitor_002",
    label: "Salesforce",
    ip: "52.14.33.91",
    pages: ["/case-studies", "/features", "/about"],
    score: 5.0,
    time_on_site_seconds: 110,
    visits_this_week: 2,
  },
  {
    id: "visitor_003",
    label: "Unresolved Residential",
    ip: "98.76.54.32",
    pages: ["/pricing"],
    score: 1.0,
    time_on_site_seconds: 30,
    visits_this_week: 1,
  },
  {
    id: "visitor_004",
    label: "Adobe",
    ip: "18.204.55.12",
    pages: ["/blog", "/about"],
    score: 1.0,
    time_on_site_seconds: 55,
    visits_this_week: 1,
  },
];

function scoreTone(score) {
  if (score >= 7) {
    return "bg-emerald-400";
  }
  if (score >= 4) {
    return "bg-orange-400";
  }
  return "bg-slate-500";
}

function App() {
  const [mode, setMode] = useState("visitor");
  const [viewState, setViewState] = useState("empty");
  const [formState, setFormState] = useState({
    ip: "34.201.12.88",
    pages: "/pricing, /ai-sales-agent, /case-studies",
    timeOnSiteSeconds: "222",
    visitsThisWeek: "3",
  });
  const [companyList, setCompanyList] = useState("HubSpot\nSalesforce\nAdobe");
  const [result, setResult] = useState(null);
  const [errorMessage, setErrorMessage] = useState("");
  const [loading, setLoading] = useState(false);

  function handleChangeField(field, value) {
    setFormState((current) => ({ ...current, [field]: value }));
  }

  function handleReset() {
    setViewState("empty");
    setResult(null);
    setErrorMessage("");
  }

  async function runVisitorAnalyze(visitorPayload) {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
      body: JSON.stringify(visitorPayload),
      headers: { "Content-Type": "application/json" },
      method: "POST",
    });
    if (!response.ok) {
      throw new Error("Analyze request failed.");
    }

    return response.json();
  }

  async function handleAnalyze() {
    setLoading(true);
    setErrorMessage("");
    setViewState("loading");

    try {
      if (mode === "visitor") {
        const payload = await runVisitorAnalyze({
          ip: formState.ip,
          pages: formState.pages
            .split(",")
            .map((page) => page.trim())
            .filter(Boolean),
          time_on_site_seconds: Number(formState.timeOnSiteSeconds || 0),
          visits_this_week: Number(formState.visitsThisWeek || 0),
        });
        setResult(payload);
        setViewState(payload.status === "unresolved" ? "unresolved" : "result");
      } else {
        const response = await fetch(`${API_BASE_URL}/enrich-batch`, {
          body: JSON.stringify({
            companies: companyList
              .split("\n")
              .map((name) => name.trim())
              .filter(Boolean),
          }),
          headers: { "Content-Type": "application/json" },
          method: "POST",
        });
        if (!response.ok) {
          throw new Error("Batch enrichment request failed.");
        }

        const payload = await response.json();
        const firstResult = payload[0] || null;
        setResult(firstResult);
        setViewState(firstResult?.status === "unresolved" ? "unresolved" : "result");
      }
    } catch (error) {
      setErrorMessage(error.message || "Unable to reach the backend API.");
      setViewState("empty");
    } finally {
      setLoading(false);
    }
  }

  async function handleSelectVisitor(visitor) {
    setMode("visitor");
    setFormState({
      ip: visitor.ip,
      pages: visitor.pages.join(", "),
      timeOnSiteSeconds: String(visitor.time_on_site_seconds),
      visitsThisWeek: String(visitor.visits_this_week),
    });
    setLoading(true);
    setErrorMessage("");
    setViewState("loading");

    try {
      const payload = await runVisitorAnalyze({
        ip: visitor.ip,
        pages: visitor.pages,
        time_on_site_seconds: visitor.time_on_site_seconds,
        visits_this_week: visitor.visits_this_week,
      });
      setResult(payload);
      setViewState(payload.status === "unresolved" ? "unresolved" : "result");
    } catch (error) {
      setErrorMessage(error.message || "Unable to reach the backend API.");
      setViewState("empty");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(52,211,153,0.18),_transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(59,130,246,0.14),_transparent_28%)]">
        <div className="mx-auto flex min-h-screen max-w-[1600px] flex-col bg-hero-grid bg-hero-grid px-4 py-4 lg:flex-row lg:px-6">
          <InputPanel
            companyList={companyList}
            formState={formState}
            loading={loading}
            mode={mode}
            onAnalyze={handleAnalyze}
            onChangeCompanyList={setCompanyList}
            onChangeField={handleChangeField}
            onReset={handleReset}
            onSelectVisitor={handleSelectVisitor}
            recentVisitors={mockRecentVisitors}
            scoreTone={scoreTone}
            setMode={setMode}
          />

          <main className="relative mt-4 flex-1 lg:mt-0 lg:pl-4">
            <div className="flex min-h-[calc(100vh-2rem)] items-stretch">
              {errorMessage && (
                <div className="absolute left-4 right-4 top-4 z-10 rounded-2xl border border-red-400/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
                  {errorMessage}
                </div>
              )}

              {viewState === "empty" && (
                <section className="flex w-full items-center justify-center rounded-[32px] border border-dashed border-slate-800 bg-slate-900/55 p-10 backdrop-blur">
                  <div className="max-w-md text-center">
                    <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full border border-slate-800 bg-slate-950/80 text-3xl">
                      ◌
                    </div>
                    <h2 className="mt-6 text-3xl font-semibold text-white">
                      Select a visitor to analyze
                    </h2>
                    <p className="mt-3 text-sm leading-7 text-slate-400">
                      Run a visitor signal or paste a company list to generate account
                      intelligence cards for Fello&apos;s sales team.
                    </p>
                  </div>
                </section>
              )}

              {viewState === "loading" && (
                <section className="grid w-full gap-4 rounded-[32px] border border-slate-800 bg-slate-900/60 p-6 md:grid-cols-2 xl:grid-cols-3">
                  {Array.from({ length: 6 }).map((_, index) => (
                    <div
                      key={index}
                      className="h-40 animate-pulse rounded-[28px] border border-slate-800 bg-slate-950/80"
                    />
                  ))}
                </section>
              )}

              {viewState === "result" && result && <AccountCard account={result} />}

              {viewState === "unresolved" && <UnresolvedCard result={result} />}
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}

export default App;
