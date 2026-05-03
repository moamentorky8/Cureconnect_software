"use client";

import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import {
  signInWithEmailAndPassword,
  signInWithPopup,
} from "firebase/auth";
import { auth, googleProvider } from "../../lib/firebase";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);

  const getFriendlyError = (code: string) => {
    switch (code) {
      case "auth/user-not-found":
      case "auth/wrong-password":
      case "auth/invalid-credential":
        return "Invalid email or password. Please try again.";
      case "auth/too-many-requests":
        return "Too many failed attempts. Please try again later.";
      case "auth/user-disabled":
        return "This account has been disabled.";
      case "auth/network-request-failed":
        return "Network error. Please check your connection.";
      default:
        return "Login failed. Please try again.";
    }
  };

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!auth) {
      setError("Firebase is not configured. Please contact support.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      await signInWithEmailAndPassword(auth, email, password);
      router.push("/dashboard");
    } catch (err: unknown) {
      const code = (err as { code?: string })?.code ?? "";
      setError(getFriendlyError(code));
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    if (!auth || !googleProvider) {
      setError("Firebase is not configured. Please contact support.");
      return;
    }
    setGoogleLoading(true);
    setError("");
    try {
      await signInWithPopup(auth, googleProvider);
      router.push("/dashboard");
    } catch (err: unknown) {
      const code = (err as { code?: string })?.code ?? "";
      if (code !== "auth/popup-closed-by-user") {
        setError(getFriendlyError(code));
      }
    } finally {
      setGoogleLoading(false);
    }
  };

  return (
    <div className="px-6 pb-10 pt-4 md:px-10 md:pb-16">
      <div className="mx-auto grid max-w-6xl gap-8 lg:grid-cols-[1.05fr_0.95fr]">

        {/* Left panel */}
        <section className="rounded-[36px] bg-[linear-gradient(160deg,#006064_0%,#11838a_100%)] p-8 text-white shadow-[0_24px_60px_rgba(0,96,100,0.18)] md:p-10 flex flex-col justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-100">
              Secure Access
            </p>
            <h1 className="display-font mt-4 text-4xl font-bold leading-tight md:text-5xl">
              Welcome back to your patient care command center.
            </h1>
            <p className="mt-5 max-w-xl text-base leading-7 text-cyan-50/90">
              Sign in to monitor medication schedules, track patient vitals,
              and stay connected with your care team in real time.
            </p>
          </div>
          <div className="mt-10 flex items-center gap-4 rounded-[24px] bg-white/10 p-5 backdrop-blur">
            <Image
              src="/cureconnect-logo.jpg"
              alt="CureConnect Logo"
              width={48}
              height={48}
              className="h-12 w-12 rounded-2xl object-cover"
            />
            <div>
              <p className="display-font text-lg font-bold">CureConnect</p>
              <p className="text-sm text-cyan-100">Smart medication companion</p>
            </div>
          </div>
        </section>

        {/* Right panel — login form */}
        <section className="rounded-[36px] bg-white/95 p-8 shadow-sm ring-1 ring-white/80 md:p-10">
          <div className="mb-8">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[#006064]">
              Sign In
            </p>
            <h2 className="display-font mt-3 text-3xl font-bold text-slate-900">
              Access your dashboard
            </h2>
          </div>

          {/* Google Sign-In */}
          <button
            type="button"
            onClick={handleGoogleLogin}
            disabled={googleLoading}
            className="mb-6 flex w-full items-center justify-center gap-3 rounded-2xl border border-slate-200 bg-white px-5 py-3 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 hover:shadow-md disabled:opacity-60"
          >
            {googleLoading ? (
              <span className="h-5 w-5 animate-spin rounded-full border-2 border-slate-300 border-t-[#006064]" />
            ) : (
              <svg className="h-5 w-5" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
            )}
            {googleLoading ? "Signing in..." : "Continue with Google"}
          </button>

          {/* Divider */}
          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-slate-200" />
            </div>
            <div className="relative flex justify-center text-xs font-semibold uppercase tracking-widest text-slate-400">
              <span className="bg-white px-3">or sign in with email</span>
            </div>
          </div>

          {/* Error message */}
          {error && (
            <div className="mb-5 rounded-2xl border border-red-100 bg-red-50 p-4 text-sm font-semibold text-red-600">
              {error}
            </div>
          )}

          {/* Email / Password form */}
          <form onSubmit={handleEmailLogin} className="space-y-5">
            <div>
              <label htmlFor="email" className="mb-2 block text-sm font-semibold text-slate-700">
                Email
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="caregiver@cureconnect.com"
                className="w-full rounded-2xl border border-slate-200 bg-[#f7fbfd] px-4 py-3 text-sm outline-none transition focus:border-[#006064] focus:ring-4 focus:ring-cyan-100"
              />
            </div>
            <div>
              <div className="mb-2 flex items-center justify-between">
                <label htmlFor="password" className="block text-sm font-semibold text-slate-700">
                  Password
                </label>
                <Link
                  href="/reset-password"
                  className="text-xs font-bold text-[#59B585] transition-colors hover:text-[#006064]"
                >
                  Forgot Password?
                </Link>
              </div>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="w-full rounded-2xl border border-slate-200 bg-[#f7fbfd] px-4 py-3 text-sm outline-none transition focus:border-[#006064] focus:ring-4 focus:ring-cyan-100"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-2xl bg-[#006064] px-5 py-3 text-sm font-bold text-white shadow-lg shadow-cyan-950/20 transition hover:-translate-y-0.5 disabled:opacity-60"
            >
              {loading && (
                <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
              )}
              {loading ? "Signing in..." : "Login to CureConnect"}
            </button>
          </form>

          <div className="mt-8 border-t border-slate-100 pt-6 text-center">
            <p className="text-sm text-gray-600">
              Don&apos;t have an account?{" "}
              <Link href="/register" className="font-bold text-[#006064] hover:underline">
                Register Now
              </Link>
            </p>
          </div>
        </section>
      </div>
    </div>
  );
}
