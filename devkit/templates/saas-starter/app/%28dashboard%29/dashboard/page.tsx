import { createServerComponentClient } from '@supabase/auth-helpers-nextjs'
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import Link from 'next/link'
import { prisma } from '@/lib/prisma'

export default async function Dashboard() {
  const supabase = createServerComponentClient({ cookies })
  const { data: { session } } = await supabase.auth.getSession()

  if (!session) {
    redirect('/login')
  }

  // In production, fetch subscription from DB
  // const user = await prisma.user.findUnique(...)

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>

      <div className="grid md:grid-cols-3 gap-6 mb-12">
        <div className="rounded-xl border border-slate-200 dark:border-slate-700 p-6">
          <p className="text-sm text-slate-500 mb-1">Plan</p>
          <p className="text-2xl font-bold">Free</p>
        </div>
        <div className="rounded-xl border border-slate-200 dark:border-slate-700 p-6">
          <p className="text-sm text-slate-500 mb-1">API Calls</p>
          <p className="text-2xl font-bold">0 / 100</p>
        </div>
        <div className="rounded-xl border border-slate-200 dark:border-slate-700 p-6">
          <p className="text-sm text-slate-500 mb-1">Repos</p>
          <p className="text-2xl font-bold">0 / 1</p>
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 dark:border-slate-700 p-8 text-center">
        <h2 className="text-xl font-bold mb-2">Upgrade to Pro</h2>
        <p className="text-slate-600 dark:text-slate-300 mb-4">
          Get 10,000 API calls/month, 10 repos, and email support for $29/mo.
        </p>
        <Link
          href="/dashboard/billing"
          className="inline-block bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700"
        >
          Manage Billing
        </Link>
      </div>
    </div>
  )
}
