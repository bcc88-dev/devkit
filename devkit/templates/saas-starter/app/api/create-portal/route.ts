import { NextResponse } from 'next/server'
import Stripe from 'stripe'

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-04-10',
})

export async function GET(request: Request) {
  try {
    // In production, look up the Stripe customer ID for the logged-in user
    const session = await stripe.billingPortal.sessions.create({
      customer: 'placeholder_customer_id',
      return_url: `${request.headers.get('origin')}/dashboard`,
    })

    return NextResponse.redirect(session.url!, 303)
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 })
  }
}
