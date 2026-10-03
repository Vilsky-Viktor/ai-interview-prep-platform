import type { Product } from "@/types/billing"

/** The message key and values for a product's name in the interface language; billing's own
title is English only. */
export function productName(product: Product): [string, { count?: number }] {
  if (product.pass_days) {
    return ["pass", {}]
  }

  if (product.candidate_credits) {
    return ["candidates", { count: product.candidate_credits }]
  }

  return ["generations", { count: product.generation_credits }]
}
