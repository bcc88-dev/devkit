import Stripe from 'stripe'

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2024-04-10',
  typescript: true,
})

export const TIER_PRICES = {
  PRO: process.env.STRIPE_PRO_PRICE_ID,
  ENTERPRISE: process.env.STRIPE_ENTERPRISE_PRICE_ID,
} as const

export const TIER_LIMITS = {
  FREE: { apiCalls: 100, repos: 1 },
  PRO: { apiCalls: 10000, repos: 10 },
  ENTERPRISE: { apiCalls: 100000, repos: 100 },
} as const
