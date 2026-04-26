"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import { useState } from "react";

type NavItem = {
  href: string;
  label: string;
  short: string;
};

const navItems: NavItem[] = [
  { href: "/", label: "Landing Page", short: "LP" },
  { href: "/dashboard", label: "Dashboard", short: "DB" },
  { href: "/medicine-schedule", label: "Medicine Schedule", short: "MS" },
];

const footerNames = ["Moamen Abdel Fattah", "Malak Mohamed"];

function SidebarLinks({
  pathname,
  onNavigate,
}: {
  pathname: string;
  onNavigate?: () => void;
}) {
  return (
    <nav className="space-y-2">
      {navItems.map((item) => {
        const isActive = pathname === item.href;

        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={onNavigate}
            className={`group flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-semibold transition ${
              isActive
                ? "bg-[#006064] text-white shadow-lg shadow-cyan-950/20"
                : "text-slate-700 hover:bg-white hover:text-[#006064]"
            }`}
          >
            <span
              className={`flex h-10 w-10 items-center justify-center rounded-2xl text-xs font-bold ${
                isActive
                  ? "bg-white/20 text-white"
                  : "bg-[#006064]/10 text-[#006064] group-hover:bg-[#006064]/15"
              }`}
            >
              {item.short}
            </span>
            <span>{item.label}</span>
          </Link>
        );
      })}
    </nav>
  );
}

export default function Navbar({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const isLoginPage = pathname === "/login";

  if (isLoginPage) {
    return (
      <div className="relative min-h-screen overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(0,96,100,0.18),transparent_30%),linear-gradient(180deg,#F8FDFF_0%,#E3F2FD_100%)]" />
        <header className="relative z-10 px-6 py-6 md:px-10">
          <Link href="/" className="inline-flex items-center gap-3 rounded-full bg-white/90 px-4 py-3 shadow-sm ring-1 ring-slate-200 backdrop-blur">
            <Image
              src="/cureconnect-logo.jpg"
              alt="CureConnect Logo"
              width={44}
              height={44}
              className="h-11 w-11 rounded-full object-cover"
            />
            <div>
              <p className="display-font text-lg font-bold text-[#006064]">CureConnect</p>
              <p className="text-xs font-medium text-slate-500">Smart medication companion</p>
            </div>
          </Link>
        </header>
        <main className="relative z-10">{children}</main>
        <footer className="relative z-10 border-t border-white/60 px-6 py-5 text-center text-sm text-slate-600">
          <p className="font-semibold text-[#006064]">CureConnect</p>
          <p>{footerNames.join(" • ")}</p>
        </footer>
      </div>
    );
  }

  return (
    <div className="min-h-screen md:flex">
      <aside className="hidden w-80 flex-col border-r border-white/70 bg-white/70 p-6 backdrop-blur-xl md:flex">
        <Link href="/" className="mb-8 flex items-center gap-3 rounded-[28px] bg-white p-4 shadow-sm ring-1 ring-slate-100">
          <Image
            src="/cureconnect-logo.jpg"
            alt="CureConnect Logo"
            width={56}
            height={56}
            className="h-14 w-14 rounded-2xl object-cover"
          />
          <div>
            <p className="display-font text-2xl font-bold text-[#006064]">CureConnect</p>
            <p className="text-sm text-slate-500">Connected care navigation</p>
          </div>
        </Link>

        <SidebarLinks pathname={pathname} />

        <div className="mt-8 rounded-[28px] bg-[#006064] p-5 text-white shadow-xl shadow-cyan-950/20">
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-cyan-100">Live Monitoring</p>
          <p className="mt-3 display-font text-2xl font-bold">Always-on patient overview</p>
          <p className="mt-2 text-sm text-cyan-50/90">
            Navigate between medication, monitoring, and patient status without reloading.
          </p>
        </div>

        <footer className="mt-auto pt-8 text-sm text-slate-600">
          <p className="font-semibold text-[#006064]">CureConnect</p>
          <p className="mt-1">{footerNames.join(" • ")}</p>
        </footer>
      </aside>

      <div className="flex min-h-screen flex-1 flex-col">
        <header className="sticky top-0 z-40 flex items-center justify-between border-b border-white/70 bg-white/85 px-5 py-4 backdrop-blur md:hidden">
          <Link href="/" className="flex items-center gap-3">
            <Image
              src="/cureconnect-logo.jpg"
              alt="CureConnect Logo"
              width={40}
              height={40}
              className="h-10 w-10 rounded-xl object-cover"
            />
            <span className="display-font text-xl font-bold text-[#006064]">CureConnect</span>
          </Link>
          <button
            type="button"
            aria-label="Open navigation"
            onClick={() => setOpen(true)}
            className="rounded-2xl bg-[#006064] px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-cyan-950/20"
          >
            Menu
          </button>
        </header>

        {open ? (
          <div className="fixed inset-0 z-50 bg-slate-950/40 md:hidden" onClick={() => setOpen(false)}>
            <aside
              className="absolute left-0 top-0 h-full w-80 bg-[#f7fbfd] p-6 shadow-2xl"
              onClick={(event) => event.stopPropagation()}
            >
              <div className="mb-8 flex items-center justify-between">
                <Link href="/" className="flex items-center gap-3" onClick={() => setOpen(false)}>
                  <Image
                    src="/cureconnect-logo.jpg"
                    alt="CureConnect Logo"
                    width={44}
                    height={44}
                    className="h-11 w-11 rounded-2xl object-cover"
                  />
                  <span className="display-font text-xl font-bold text-[#006064]">CureConnect</span>
                </Link>
                <button
                  type="button"
                  onClick={() => setOpen(false)}
                  className="rounded-full bg-white px-3 py-1 text-sm font-semibold text-slate-500 shadow"
                >
                  Close
                </button>
              </div>
              <SidebarLinks pathname={pathname} onNavigate={() => setOpen(false)} />
            </aside>
          </div>
        ) : null}

        <main className="flex-1 px-4 py-6 md:px-8 md:py-8">{children}</main>

        <footer className="border-t border-white/70 px-4 py-5 text-center text-sm text-slate-600 md:hidden">
          <p className="font-semibold text-[#006064]">CureConnect</p>
          <p>{footerNames.join(" • ")}</p>
        </footer>
      </div>
    </div>
  );
}
