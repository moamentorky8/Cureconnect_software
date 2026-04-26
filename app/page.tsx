import Link from "next/link";

const featureCards = [
  {
    title: "Live Sensor Oversight",
    description:
      "Monitor drawer status, emergency activity, and room conditions from a single care hub.",
  },
  {
    title: "Medication Adherence",
    description:
      "Track each scheduled dose and quickly spot upcoming, missed, or completed medicines.",
  },
  {
    title: "Family-Friendly Experience",
    description:
      "Keep caregivers informed with a clean interface designed for confidence and speed.",
  },
];

export default function LandingPage() {
  return (
    <div className="mx-auto max-w-7xl space-y-10">
      <section className="relative overflow-hidden rounded-[36px] bg-[linear-gradient(135deg,#006064_0%,#0f8b8f_55%,#7dd3d8_100%)] px-6 py-10 text-white shadow-[0_24px_60px_rgba(0,96,100,0.18)] md:px-10 md:py-14">
        <div className="absolute right-0 top-0 h-56 w-56 rounded-full bg-white/10 blur-3xl" />
        <div className="absolute bottom-0 left-16 h-40 w-40 rounded-full bg-cyan-200/20 blur-3xl" />
        <div className="relative z-10 max-w-3xl">
          <p className="mb-4 inline-flex rounded-full bg-white/10 px-4 py-2 text-xs font-semibold uppercase tracking-[0.28em] text-cyan-50">
            Connected Healthcare
          </p>
          <h1 className="display-font text-4xl font-bold leading-tight md:text-6xl">
            Smart navigation for medication care, patient monitoring, and daily routines.
          </h1>
          <p className="mt-5 max-w-2xl text-base text-cyan-50/90 md:text-lg">
            CureConnect brings the landing experience, real-time dashboard, and medicine schedule
            into one smooth Next.js App Router flow with a professional clinical UI.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <Link
              href="/dashboard"
              className="rounded-full bg-white px-6 py-3 text-sm font-bold text-[#006064] shadow-lg transition hover:-translate-y-0.5"
            >
              Open Dashboard
            </Link>
            <Link
              href="/medicine-schedule"
              className="rounded-full border border-white/30 px-6 py-3 text-sm font-bold text-white transition hover:bg-white/10"
            >
              View Schedule
            </Link>
          </div>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-[32px] bg-white/90 p-8 shadow-sm ring-1 ring-white/80">
          <p className="text-sm font-semibold uppercase tracking-[0.25em] text-[#006064]">
            Care Coordination
          </p>
          <h2 className="display-font mt-3 text-3xl font-bold text-slate-900">
            A calm interface for a high-trust medical workflow
          </h2>
          <p className="mt-4 max-w-2xl text-slate-600">
            The new navigation pattern keeps caregivers oriented at all times, preserves fast
            client-side page transitions, and highlights medication status with a clear medical
            visual language based on soft blue and deep teal.
          </p>
          <div className="mt-8 grid gap-4 md:grid-cols-3">
            {featureCards.map((card) => (
              <article
                key={card.title}
                className="rounded-[28px] bg-[#E3F2FD] p-5 ring-1 ring-[#006064]/10 transition hover:-translate-y-1 hover:shadow-lg"
              >
                <h3 className="display-font text-lg font-bold text-[#006064]">{card.title}</h3>
                <p className="mt-3 text-sm leading-6 text-slate-600">{card.description}</p>
              </article>
            ))}
          </div>
        </div>

        <aside className="rounded-[32px] bg-white/90 p-8 shadow-sm ring-1 ring-white/80">
          <p className="text-sm font-semibold uppercase tracking-[0.25em] text-[#006064]">
            Quick Access
          </p>
          <div className="mt-6 space-y-4">
            <Link
              href="/login"
              className="block rounded-[28px] bg-[#006064] px-6 py-5 text-white shadow-lg shadow-cyan-950/15 transition hover:-translate-y-0.5"
            >
              <span className="block text-xs font-semibold uppercase tracking-[0.24em] text-cyan-100">
                Authentication
              </span>
              <span className="mt-2 block display-font text-2xl font-bold">Login Screen</span>
            </Link>
            <Link
              href="/dashboard"
              className="block rounded-[28px] bg-[#f7fbfd] px-6 py-5 ring-1 ring-[#006064]/10 transition hover:-translate-y-0.5 hover:shadow-lg"
            >
              <span className="block text-xs font-semibold uppercase tracking-[0.24em] text-[#006064]">
                Monitoring
              </span>
              <span className="mt-2 block display-font text-2xl font-bold text-slate-900">
                Real-Time Dashboard
              </span>
            </Link>
            <Link
              href="/medicine-schedule"
              className="block rounded-[28px] bg-[#f7fbfd] px-6 py-5 ring-1 ring-[#006064]/10 transition hover:-translate-y-0.5 hover:shadow-lg"
            >
              <span className="block text-xs font-semibold uppercase tracking-[0.24em] text-[#006064]">
                Planning
              </span>
              <span className="mt-2 block display-font text-2xl font-bold text-slate-900">
                Medicine Schedule
              </span>
            </Link>
          </div>
        </aside>
      </section>
    </div>
  );
}
