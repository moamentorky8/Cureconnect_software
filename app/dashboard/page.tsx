"use client";

import { onValue, ref } from "firebase/database";
import { useEffect, useState } from "react";
import { database } from "../../lib/firebase";

type SensorState = {
  temperature: number;
  humidity: number;
  heartRate: number;
  drawerOpen: boolean;
  sosActive: boolean;
};

type MedicationItem = {
  id: string;
  name: string;
  time: string;
  status: "Taken" | "Pending" | "Missed";
};

const defaultSensors: SensorState = {
  temperature: 24,
  humidity: 51,
  heartRate: 74,
  drawerOpen: false,
  sosActive: false,
};

const defaultMedication: MedicationItem[] = [
  { id: "1", name: "Morning Insulin", time: "08:00 AM", status: "Taken" },
  { id: "2", name: "Blood Pressure Tablet", time: "01:00 PM", status: "Pending" },
  { id: "3", name: "Vitamin Support", time: "07:30 PM", status: "Missed" },
];

const statusTone = {
  Taken: "bg-emerald-100 text-emerald-700",
  Pending: "bg-amber-100 text-amber-700",
  Missed: "bg-rose-100 text-rose-700",
};

export default function DashboardPage() {
  const [sensors, setSensors] = useState<SensorState>(defaultSensors);
  const [medication, setMedication] = useState<MedicationItem[]>(defaultMedication);

  useEffect(() => {
    if (!database) {
      return;
    }

    const sensorRef = ref(database, "device/liveSensors");
    const medicationRef = ref(database, "users/demoUser/medicationStatus");

    const unsubscribeSensors = onValue(sensorRef, (snapshot) => {
      const data = snapshot.val();
      if (!data) {
        return;
      }

      setSensors((current) => ({
        ...current,
        temperature: Number(data.temperature ?? current.temperature),
        humidity: Number(data.humidity ?? current.humidity),
        heartRate: Number(data.heartRate ?? current.heartRate),
        drawerOpen: Boolean(data.drawerOpen ?? current.drawerOpen),
        sosActive: Boolean(data.sosActive ?? current.sosActive),
      }));
    });

    const unsubscribeMedication = onValue(medicationRef, (snapshot) => {
      const data = snapshot.val();
      if (!data) {
        return;
      }

      const entries = Object.entries(data).map(([id, item]) => {
        const value = item as Partial<MedicationItem>;

        return {
          id,
          name: value.name ?? "Medication",
          time: value.time ?? "--:--",
          status: (value.status as MedicationItem["status"]) ?? "Pending",
        };
      });

      setMedication(entries);
    });

    return () => {
      unsubscribeSensors();
      unsubscribeMedication();
    };
  }, []);

  const takenCount = medication.filter((item) => item.status === "Taken").length;

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <section className="rounded-[34px] bg-white/90 p-8 shadow-sm ring-1 ring-white/80">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[#006064]">
              Real-Time Dashboard
            </p>
            <h1 className="display-font mt-3 text-4xl font-bold text-slate-900">
              Live patient overview and medication status
            </h1>
            <p className="mt-3 max-w-3xl text-slate-600">
              Firebase-powered sensor cards update in real time while the dashboard keeps the
              patient&apos;s latest medication adherence visible at a glance.
            </p>
          </div>
          <div className="rounded-[28px] bg-[#E3F2FD] px-5 py-4 ring-1 ring-[#006064]/10">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[#006064]">
              Daily Progress
            </p>
            <p className="display-font mt-2 text-3xl font-bold text-slate-900">
              {takenCount}/{medication.length} doses taken
            </p>
          </div>
        </div>
      </section>

      <section className="grid gap-5 md:grid-cols-2 xl:grid-cols-4">
        {[
          { label: "Temperature", value: `${sensors.temperature}°C` },
          { label: "Humidity", value: `${sensors.humidity}%` },
          { label: "Heart Rate", value: `${sensors.heartRate} bpm` },
          { label: "Drawer Status", value: sensors.drawerOpen ? "Open" : "Closed" },
        ].map((item) => (
          <article
            key={item.label}
            className="rounded-[30px] bg-white/90 p-6 shadow-sm ring-1 ring-white/80"
          >
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[#006064]">
              {item.label}
            </p>
            <p className="display-font mt-4 text-3xl font-bold text-slate-900">{item.value}</p>
          </article>
        ))}
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <article className="rounded-[34px] bg-white/90 p-8 shadow-sm ring-1 ring-white/80">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[#006064]">
                Medication Status
              </p>
              <h2 className="display-font mt-2 text-2xl font-bold text-slate-900">
                Today&apos;s dose checklist
              </h2>
            </div>
            <span className="rounded-full bg-[#006064] px-4 py-2 text-xs font-bold uppercase tracking-[0.24em] text-white">
              Synced
            </span>
          </div>

          <div className="mt-6 space-y-4">
            {medication.map((item) => (
              <div
                key={item.id}
                className="flex flex-col gap-3 rounded-[28px] bg-[#f7fbfd] p-5 ring-1 ring-[#006064]/10 md:flex-row md:items-center md:justify-between"
              >
                <div>
                  <h3 className="text-lg font-bold text-slate-900">{item.name}</h3>
                  <p className="text-sm text-slate-500">{item.time}</p>
                </div>
                <span className={`w-fit rounded-full px-4 py-2 text-sm font-bold ${statusTone[item.status]}`}>
                  {item.status}
                </span>
              </div>
            ))}
          </div>
        </article>

        <article className="rounded-[34px] bg-[linear-gradient(160deg,#006064_0%,#11838a_100%)] p-8 text-white shadow-[0_24px_60px_rgba(0,96,100,0.2)]">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-cyan-100">
            Emergency Pulse
          </p>
          <h2 className="display-font mt-2 text-3xl font-bold">
            {sensors.sosActive ? "Immediate caregiver attention needed" : "System operating normally"}
          </h2>
          <p className="mt-4 text-sm leading-6 text-cyan-50/90">
            Tie this state to your Firebase emergency node to visually escalate SOS events across
            the dashboard in real time.
          </p>
          <div className="mt-8 rounded-[30px] bg-white/10 p-5 ring-1 ring-white/15">
            <p className="text-xs font-semibold uppercase tracking-[0.24em] text-cyan-100">
              Current Flag
            </p>
            <p className="mt-3 display-font text-3xl font-bold">
              {sensors.sosActive ? "SOS Active" : "Stable"}
            </p>
          </div>
        </article>
      </section>
    </div>
  );
}
