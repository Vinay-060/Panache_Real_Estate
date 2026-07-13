AED_USD = 3.6725


def generate_payment_breakdown(budget):

    booking = budget * 0.20
    installments = budget * 0.80

    return {
        "booking_aed": booking,
        "booking_usd": booking / AED_USD,

        "installments_aed": installments,
        "installments_usd": installments / AED_USD
    }
    
    