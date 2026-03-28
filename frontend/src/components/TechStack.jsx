// Card component for displaying inferred CRM, marketing, and analytics tooling.
const defaultStack = [
  ["CRM", "Salesforce"],
  ["Marketing", "HubSpot"],
  ["Analytics", "Google Analytics"],
  ["Data", "Apollo"],
];

function normalizeItems(items) {
  if (!items || typeof items !== "object") {
    return defaultStack;
  }

  const entries = Object.entries(items).filter(([, value]) => value);
  return entries.length ? entries : defaultStack;
}

export default function TechStack({ items = defaultStack }) {
  const normalizedItems = Array.isArray(items) ? items : normalizeItems(items);

  return (
    <div className="rounded-[28px] border border-slate-800 bg-slate-950/80 p-5">
      <p className="text-xs uppercase tracking-[0.28em] text-slate-500">Tech stack</p>
      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        {normalizedItems.map(([label, value]) => (
          <div
            key={label}
            className="rounded-2xl border border-slate-800 bg-slate-900/70 px-4 py-4"
          >
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">{label}</p>
            <p className="mt-2 text-sm font-medium text-white">{value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
