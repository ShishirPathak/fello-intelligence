// Main resolved account intelligence card shown in the dashboard result state.
import ActionsCard from "./ActionsCard";
import BusinessSignals from "./BusinessSignals";
import IntentBadge from "./IntentBadge";
import PersonaCard from "./PersonaCard";
import TechStack from "./TechStack";

function formatTechStack(techStack) {
  if (!techStack || typeof techStack !== "object") {
    return [
      ["CRM", "Unknown"],
      ["Marketing", "Unknown"],
      ["Analytics", "Unknown"],
      ["Data", "Apollo"],
    ];
  }

  const entries = Object.entries(techStack).filter(([, value]) => value);
  return entries.length ? entries : [["Data", "Apollo"]];
}

export default function AccountCard({ account }) {
  const heroLetter = (account?.company_name || "?").charAt(0).toUpperCase();
  const personaConfidence = (account?.persona_confidence || 0) * 100;
  const intentSignals = account?.intent_signals?.length
    ? account.intent_signals
    : ["Limited behavioral signals available"];

  return (
    <section className="w-full rounded-[32px] border border-slate-800 bg-slate-900/70 p-6 backdrop-blur">
      <div className="rounded-[28px] border border-emerald-400/20 bg-[linear-gradient(135deg,rgba(16,185,129,0.14),rgba(15,23,42,0.88))] p-6">
        <div className="flex flex-col gap-6 xl:flex-row xl:items-center xl:justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-16 w-16 items-center justify-center rounded-3xl bg-white/10 text-2xl font-semibold text-white">
              {heroLetter}
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.28em] text-emerald-200/70">
                {account?.status || "resolved"} account
              </p>
              <h2 className="mt-2 text-3xl font-semibold text-white">
                {account?.company_name || "Unknown account"}
              </h2>
              <p className="mt-2 text-sm text-slate-300">
                {[account?.domain, account?.industry, account?.headquarters]
                  .filter(Boolean)
                  .join(" · ") || "No enrichment details available"}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
            <div className="rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                Intent
              </p>
              <p className="mt-2 text-3xl font-semibold text-white">
                {account?.intent_score ?? "0.0"}
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                Stage
              </p>
              <div className="mt-2">
                <IntentBadge stage={account?.intent_stage || "awareness"} />
              </div>
            </div>
            <div className="rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                Size
              </p>
              <p className="mt-2 text-lg font-medium text-white">
                {account?.company_size || "Unknown"}
              </p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-slate-950/40 px-4 py-3">
              <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                Founded
              </p>
              <p className="mt-2 text-lg font-medium text-white">
                {account?.founded_year || "Unknown"}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-5 grid gap-4 xl:grid-cols-2">
        <PersonaCard
          confidence={personaConfidence}
          reasoning={account?.persona_reasoning || "No persona reasoning available."}
          title={account?.likely_persona || "Unknown persona"}
        />

        <div className="rounded-[28px] border border-slate-800 bg-slate-950/80 p-5">
          <div className="flex items-center justify-between gap-4">
            <p className="text-xs uppercase tracking-[0.28em] text-slate-500">
              Intent signals
            </p>
            <IntentBadge stage={account?.intent_stage || "awareness"} />
          </div>
          <div className="mt-4 space-y-3">
            {intentSignals.map((signal) => (
              <div
                key={signal}
                className="rounded-2xl border border-slate-800 bg-slate-900/70 px-4 py-3 text-sm text-slate-300"
              >
                {signal}
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-[28px] border border-slate-800 bg-slate-950/80 p-5 xl:col-span-2">
          <p className="text-xs uppercase tracking-[0.28em] text-slate-500">
            AI summary
          </p>
          <p className="mt-3 text-sm leading-7 text-slate-300">
            {account?.ai_summary || "No AI summary available yet."}
          </p>
        </div>
      </div>

      <div className="mt-4 grid gap-4 xl:grid-cols-2">
        <ActionsCard actions={account?.recommended_actions} />
        <TechStack items={formatTechStack(account?.tech_stack)} />
      </div>

      <div className="mt-4">
        <BusinessSignals signals={account?.business_signals} />
      </div>
    </section>
  );
}
