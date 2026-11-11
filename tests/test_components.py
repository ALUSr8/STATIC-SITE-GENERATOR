import unittest

from modules.component_definitions import COMPONENT_TYPES


class ComponentDefinitionTests(unittest.TestCase):

    def test_expected_component_types_are_registered(self):

        self.assertIn("hero", COMPONENT_TYPES)
        self.assertIn("text", COMPONENT_TYPES)
        self.assertIn("image", COMPONENT_TYPES)
        self.assertIn("gallery", COMPONENT_TYPES)
        self.assertIn("features", COMPONENT_TYPES)
        self.assertIn("cta", COMPONENT_TYPES)
        self.assertIn("testimonial", COMPONENT_TYPES)
        self.assertIn("pricing", COMPONENT_TYPES)
        self.assertIn("contact", COMPONENT_TYPES)
        self.assertIn("business_card", COMPONENT_TYPES)
        self.assertIn("product_demo", COMPONENT_TYPES)
        self.assertIn("blog_post", COMPONENT_TYPES)
        self.assertIn("portfolio", COMPONENT_TYPES)
        self.assertIn("footer", COMPONENT_TYPES)


if __name__ == "__main__":
    unittest.main()
