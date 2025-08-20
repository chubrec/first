from typing import Iterable, Tuple


def compute_line_subtotal(quantity: float, unit_price: float) -> float:
	return round((quantity or 0.0) * (unit_price or 0.0), 2)


def apply_coefficients(amount: float, complexity: float, urgency: float, floor: float) -> float:
	value = amount * (complexity or 1.0) * (urgency or 1.0) * (floor or 1.0)
	return round(value, 2)


def apply_discounts_and_markups(amount: float, discount_percent: float, markup_percent: float) -> float:
	discounted = amount * (1 - (discount_percent or 0.0) / 100.0)
	marked = discounted * (1 + (markup_percent or 0.0) / 100.0)
	return round(marked, 2)


def compute_totals(lines: Iterable[Tuple[float, float]], complexity: float, urgency: float, floor: float, discount_percent: float, markup_percent: float) -> dict:
	items_subtotal = round(sum(compute_line_subtotal(q, p) for q, p in lines), 2)
	after_coeffs = apply_coefficients(items_subtotal, complexity, urgency, floor)
	total = apply_discounts_and_markups(after_coeffs, discount_percent, markup_percent)
	return {
		"items_subtotal": items_subtotal,
		"after_coefficients": after_coeffs,
		"total": total,
	}