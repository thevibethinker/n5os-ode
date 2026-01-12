import Stripe from "stripe";

const STRIPE_SECRET_KEY = process.env.STRIPE_SECRET_KEY;

if (!STRIPE_SECRET_KEY) {
  console.warn("⚠️  STRIPE_SECRET_KEY not set - Stripe features disabled");
}

export const stripe = STRIPE_SECRET_KEY
  ? new Stripe(STRIPE_SECRET_KEY)
  : null;

export const PRICE_AMOUNT = 500; // $5.00 in cents
export const CURRENCY = "usd";

export async function createCheckoutSession(
  sessionId: string,
  baseUrl: string
): Promise<Stripe.Checkout.Session | null> {
  if (!stripe) {
    console.error("Stripe not configured");
    return null;
  }

  const checkoutSession = await stripe.checkout.sessions.create({
    mode: "payment",
    line_items: [
      {
        price_data: {
          currency: CURRENCY,
          product_data: {
            name: "Am I Hired? - Interview Feedback",
            description: "Expert analysis of your interview performance",
          },
          unit_amount: PRICE_AMOUNT,
        },
        quantity: 1,
      },
    ],
    metadata: {
      session_id: sessionId,
    },
    success_url: `${baseUrl}/success?session_id=${sessionId}`,
    cancel_url: `${baseUrl}/?cancelled=true`,
  });

  return checkoutSession;
}

export async function verifyPayment(
  stripeSessionId: string
): Promise<{ paid: boolean; sessionId: string | null }> {
  if (!stripe) {
    return { paid: false, sessionId: null };
  }

  try {
    const session = await stripe.checkout.sessions.retrieve(stripeSessionId);
    return {
      paid: session.payment_status === "paid",
      sessionId: session.metadata?.session_id || null,
    };
  } catch (error) {
    console.error("Failed to verify payment:", error);
    return { paid: false, sessionId: null };
  }
}

