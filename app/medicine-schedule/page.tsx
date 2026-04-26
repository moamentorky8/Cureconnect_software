type ScheduleStatus = "Completed" | "Upcoming" | "Planned";

const schedule: Array<{
  time: string;
  medicine: string;
  dosage: string;
  note: string;
  status: ScheduleStatus;
}> = [
  {
    time: "08:00 AM",
    medicine: "Morning Insulin",
    dosage: "10 units",
    note: "Take after breakfast.",
    status: "Completed",
  },
  {
    time: "01:00 PM",
    medicine: "Blood Pressure Tablet",
    dosage: "1 tablet",
    note: "Take with water.",
    status: "Upcoming",
  },
  {
    time: "07:30 PM",
    medicine: "Vitamin Support",
    dosage: "2 capsules",
    note: "Take after dinner.",
    status: "Planned",
  },
];

const tone: Record<ScheduleStatus, string> = {
  Completed: "bg-emerald-100 text-emerald-700",
  Upcoming: "bg-amber-100 text-amber-700",
  Planned: "bg-cyan-100 text-cyan-700",
};

export default function MedicineSchedulePage() {
  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <section className="rounded-[34px] bg-white/90 p-8 shadow-sm ring-1 ring-white/80">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[#006064]">
          Medicine Schedule
        </p>
        <h1 className="display-font mt-3 text-4xl font-bold text-slate-900">
          A simple, clinical timeline for every daily dose
        </h1>
        <p className="mt-3 max-w-3xl text-slate-600">
          This page stays connected to the shared sidebar so caregivers can move between planning,
          patient monitoring, and landing content without a full page reload.
        </p>
      </section>

      <section className="space-y-4">
        {schedule.map((item) => (
          <article
            key={`${item.time}-${item.medicine}`}
            className="grid gap-4 rounded-[30px] bg-white/90 p-6 shadow-sm ring-1 ring-white/80 md:grid-cols-[180px_1fr_auto]"
          >
            <div className="rounded-[24px] bg-[#E3F2FD] px-5 py-4 ring-1 ring-[#006064]/10">
              <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[#006064]">Time</p>
              <p className="display-font mt-2 text-2xl font-bold text-slate-900">{item.time}</p>
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-900">{item.medicine}</h2>
              <p className="mt-2 text-sm text-slate-600">Dosage: {item.dosage}</p>
              <p className="mt-1 text-sm text-slate-500">{item.note}</p>
            </div>
            <div className="flex items-start md:justify-end">
              <span className={`rounded-full px-4 py-2 text-sm font-bold ${tone[item.status]}`}>
                {item.status}
              </span>
            </div>
          </article>
        ))}
      </section>
    </div>
  );
}
