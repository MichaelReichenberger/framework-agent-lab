"""Independent boundary regression derived from the customer pricing rules."""
import unittest
from decimal import Decimal

from orders.pricing import quote


class StudentPricingRegression(unittest.TestCase):
    def test_line_rounding_reaches_free_shipping_threshold(self):
        # 99.995 * 1 rounds HALF_UP to 100.00 before shipping is decided.
        # With no discount, discounted goods are 100.00: shipping is zero.
        result = quote([{"unit_price": Decimal("99.995"), "quantity": 1}])
        self.assertEqual(result, {
            "subtotal": Decimal("100.00"),
            "shipping": Decimal("0.00"),
            "total": Decimal("100.00"),
        })
        for value in result.values():
            self.assertIsInstance(value, Decimal)


if __name__ == "__main__":
    unittest.main()
