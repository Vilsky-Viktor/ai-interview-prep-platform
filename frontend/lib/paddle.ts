import {
  CheckoutEventNames,
  initializePaddle,
  type Paddle,
} from "@paddle/paddle-js"

import type { Catalog } from "@/types/billing"

let paddle: Promise<Paddle | undefined> | null = null
let onCompleted: (() => void) | null = null

/** Paddle.js, loaded once on the first purchase. */
function load(catalog: Catalog) {
  paddle ??= initializePaddle({
    environment:
      catalog.environment === "production" ? "production" : "sandbox",
    token: catalog.client_token,
    eventCallback: (event) => {
      if (event.name === CheckoutEventNames.CHECKOUT_COMPLETED) {
        onCompleted?.()
      }
    },
  })

  return paddle
}

/**
 * Opens Paddle's checkout for one product. `customData` says whose wallet gets it; what it
 * grants is decided by the backend from Paddle's price, once the payment has gone through.
 */
export async function openCheckout(
  catalog: Catalog,
  priceId: string,
  customData: Record<string, string>,
  email: string | null,
  completed: () => void
) {
  onCompleted = completed
  const instance = await load(catalog)

  instance?.Checkout.open({
    items: [{ priceId, quantity: 1 }],
    customData,
    ...(email ? { customer: { email } } : {}),
  })
}
