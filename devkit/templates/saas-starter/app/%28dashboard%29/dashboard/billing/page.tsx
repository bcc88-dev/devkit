import { createServerComponentClient } from '@supabase/auth-helpers-nextjs'
import { cookies } from 'next/headers'
import { redirect } from 'next/navigation'
import Link from 'next/link'

export default async function BillingPage() {
  const supabase = createServerComponentClient({ cookies })
  const { data: { session } } = await supabase.auth.getSession()

  if (!session) {
    redirect('/login')
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold mb-8">Billing</h1>

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className="rounded-xl border border-slate-200 dark:border-slate-700 p-6">
          <h2 className="text-lg font-bold mb-1">Pro — $29/mo</h2>
          <p className="text-sm text-slate-500 mb-4">10,000 API calls, 10 repos, email support</p>
          <Link
            href="/api/create-checkout?tier=PRO"
            className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-primary-700"
          >
            Subscribe
          </Link>
        </div>
        <div className="rounded-xl border border-slate-200 dark:border-slate-700 p-6">
          <h2 className="text-lg font-bold mb-1">Enterprise — $99/mo</h2>
          <p className="text-sm text-slate-500 mb-4">100,000 API calls, unlimited repos, priority support</p>
          <Link
            href="/api/create-checkout?tier=ENTERPRISE"
            className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-primary-700"
          >
            Subscribe
          </Link>
        </div>
      </div>

      <div className="text-center">
        <Link
          href="/api/create-portal"
          className="text-sm text-primary-600 hover:text-primary-700"
        >
          Customer Portal (manage existing subscription)
        </Link>
      </div>
    </div>
  )
}
