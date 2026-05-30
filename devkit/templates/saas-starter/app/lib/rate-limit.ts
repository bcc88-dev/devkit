/**
 * Rate limiting by subscription tier
 */
export function getRateLimit(tier: string): { requests: number; window: number } {
  switch (tier) {
    case 'FREE':
      return { requests: 10, window: 60 }      // 10 req/min
    case 'PRO':
      return { requests: 100, window: 60 }      // 100 req/min
    case 'ENTERPRISE':
      return { requests: 1000, window: 60 }     // 1000 req/min
    default:
      return { requests: 10, window: 60 }
  }
}
