import Link from "next/link";

export default function LoginPage() {
  return (
    <div className="px-6 pb-10 pt-4 md:px-10 md:pb-16">
      <div className="mx-auto grid max-w-6xl gap-8 lg:grid-cols-[1.05fr_0.95fr]">
        
        {/* القسم الأيسر: رسالة الترحيب */}
        <section className="rounded-[36px] bg-[linear-gradient(160deg,#006064_0%,#11838a_100%)] p-8 text-white shadow-[0_24px_60px_rgba(0,96,100,0.18)] md:p-10">
          <p className="text-sm font-semibold uppercase tracking-[0.28em] text-cyan-100">
            Secure Access
          </p>
          <h1 className="display-font mt-4 text-4xl font-bold leading-tight md:text-5xl">
            Welcome back to your patient care command center.
          </h1>
          <p className="mt-5 max-w-xl text-base leading-7 text-cyan-50/90">
            The login screen now carries the CureConnect identity in the same visual system as the
            rest of the application.
          </p>
        </section>

        {/* القسم الأيمن: نموذج تسجيل الدخول */}
        <section className="rounded-[36px] bg-white/95 p-8 shadow-sm ring-1 ring-white/80 md:p-10">
          <div className="mb-8">
            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-[#006064]">
              Sign In
            </p>
            <h2 className="display-font mt-3 text-3xl font-bold text-slate-900">
              Access the CureConnect dashboard
            </h2>
          </div>

          <form className="space-y-5">
            <div>
              <label htmlFor="email" className="mb-2 block text-sm font-semibold text-slate-700">
                Email
              </label>
              <input
                id="email"
                type="email"
                placeholder="caregiver@cureconnect.com"
                className="w-full rounded-2xl border border-slate-200 bg-[#f7fbfd] px-4 py-3 text-sm outline-none transition focus:border-[#006064] focus:ring-4 focus:ring-cyan-100"
              />
            </div>
            <div>
              <div className="flex justify-between items-center mb-2">
                <label htmlFor="password" className="block text-sm font-semibold text-slate-700">
                  Password
                </label>
                {/* رابط نسيت كلمة المرور */}
                <Link href="/reset-password" class="text-xs font-bold text-[#59B585] hover:text-[#006064] transition-colors">
                  Forgot Password?
                </Link>
              </div>
              <input
                id="password"
                type="password"
                placeholder="Enter your password"
                className="w-full rounded-2xl border border-slate-200 bg-[#f7fbfd] px-4 py-3 text-sm outline-none transition focus:border-[#006064] focus:ring-4 focus:ring-cyan-100"
              />
            </div>
            
            <button
              type="submit"
              className="w-full rounded-2xl bg-[#006064] px-5 py-3 text-sm font-bold text-white shadow-lg shadow-cyan-950/20 transition hover:-translate-y-0.5"
            >
              Login to CureConnect
            </button>
          </form>

          {/* روابط إضافية لربط الصفحات */}
          <div className="mt-8 pt-6 border-t border-slate-100 text-center">
            <p className="text-sm text-gray-600">
              Don't have an account?{" "}
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
