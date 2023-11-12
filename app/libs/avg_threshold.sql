SELECT AVG((price_high + price_low) / 2)
FROM ottmarfvv_coderhouse.landing_stock_exchange
WHERE symbol like '{{ params.stock }}'
    AND datetime between '{{ params.start_date }}' AND '{{ params.end_date }}';