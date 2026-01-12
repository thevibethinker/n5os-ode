// Zo Stripe Integration
// Verifies payments through Zo's API instead of direct Stripe calls
// This eliminates the need for STRIPE_SECRET_KEY in the app

const ZO_API_BASE = "https://api.zo.computer";

interface ZoOrder {
  id: string;
  stripe_checkout_session_id: string;
  status: string;
  customer_email: string | null;
  amount_total: number;
  currency: string;
  created_at: string;
  product_name: string;
}

interface ZoOrdersResponse {
  orders: ZoOrder[];
}

/**
 * Verify a payment by checking if the checkout session exists in Zo's order list
 */
export async function verifyPaymentViaZo(
  checkoutSessionId: string
): Promise<{ paid: boolean; order: ZoOrder | null }> {
  const token = process.env.ZO_CLIENT_IDENTITY_TOKEN;
  
  if (!token) {
    console.error("ZO_CLIENT_IDENTITY_TOKEN not available");
    return { paid: false, order: null };
  }

  try {
    // Call Zo's API to list orders
    const response = await fetch(`${ZO_API_BASE}/stripe/orders?testmode=false`, {
      method: "GET",
      headers: {
        "Authorization": token,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      // Try test mode if live mode fails
      const testResponse = await fetch(`${ZO_API_BASE}/stripe/orders?testmode=true`, {
        method: "GET",
        headers: {
          "Authorization": token,
          "Content-Type": "application/json",
        },
      });
      
      if (!testResponse.ok) {
        console.error("Failed to fetch orders from Zo API:", await testResponse.text());
        return { paid: false, order: null };
      }
      
      const testData = await testResponse.json() as ZoOrdersResponse;
      const order = testData.orders?.find(o => o.stripe_checkout_session_id === checkoutSessionId);
      return { paid: !!order, order: order || null };
    }

    const data = await response.json() as ZoOrdersResponse;
    const order = data.orders?.find(o => o.stripe_checkout_session_id === checkoutSessionId);
    
    return { paid: !!order, order: order || null };
  } catch (error) {
    console.error("Error verifying payment via Zo:", error);
    return { paid: false, order: null };
  }
}

/**
 * Get the payment link URL for Am I Hired?
 * This should be set as an environment variable after creating the payment link via Zo
 */
export function getPaymentLinkUrl(sessionId: string): string {
  const baseUrl = process.env.PAYMENT_LINK_URL;
  
  if (!baseUrl) {
    console.warn("PAYMENT_LINK_URL not set - payment flow will not work");
    return "#";
  }
  
  // Payment link URL - Stripe will append checkout session info on redirect
  return baseUrl;
}

/**
 * Build the success URL for Stripe redirect
 * Includes the checkout_session_id placeholder that Stripe will replace
 */
export function buildSuccessUrl(baseUrl: string, sessionId: string): string {
  // {CHECKOUT_SESSION_ID} is a Stripe template variable that gets replaced
  return `${baseUrl}/success?session_id=${sessionId}&checkout_session_id={CHECKOUT_SESSION_ID}`;
}

