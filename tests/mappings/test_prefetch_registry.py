import unittest
from unittest.mock import Mock, patch, call

from django.db.models import Prefetch

from oscar.core.loading import get_class, get_model
from oscar_odin.mappings.prefetching.registry import PrefetchRegistry
from oscar_odin.mappings.prefetching.default_registry import (
    DefaultPrefetchRegistry,
    default_prefetch_registry,
)
from oscar_odin.mappings.catalogue import product_queryset_to_resources

ProductQuerySet = get_class("catalogue.managers", "ProductQuerySet")
Product = get_model("catalogue", "Product")


class TestPrefetchSystem(unittest.TestCase):
    def setUp(self):
        self.registry = DefaultPrefetchRegistry()

    def tearDown(self):
        # Clear the registry after each test
        self.registry.prefetches.clear()
        self.registry.children_prefetches.clear()
        self.registry.select_related.clear()

    def test_register_string_prefetch(self):
        self.registry.register_prefetch("test_prefetch")
        self.assertIn("test_prefetch", self.registry.prefetches)
        self.assertEqual(self.registry.prefetches["test_prefetch"], "test_prefetch")

    def test_register_prefetch_object(self):
        prefetch = Prefetch("test_prefetch")
        self.registry.register_prefetch(prefetch)
        self.assertIn("test_prefetch", self.registry.prefetches)
        self.assertEqual(self.registry.prefetches["test_prefetch"], prefetch)

    def test_register_callable_prefetch(self):
        def test_prefetch(queryset, **kwargs):
            return queryset

        self.registry.register_prefetch(test_prefetch)
        self.assertIn("test_prefetch", self.registry.prefetches)
        self.assertEqual(self.registry.prefetches["test_prefetch"], test_prefetch)

    def test_register_children_prefetch(self):
        self.registry.register_children_prefetch("test_children_prefetch")
        self.assertIn("test_children_prefetch", self.registry.children_prefetches)

    def test_register_select_related_string(self):
        self.registry.register_select_related("test_select")
        self.assertIn("test_select", self.registry.select_related)

    def test_register_select_related_list(self):
        self.registry.register_select_related(["test_select1", "test_select2"])
        self.assertIn("test_select1", self.registry.select_related)
        self.assertIn("test_select2", self.registry.select_related)

    def test_unregister_prefetch(self):
        self.registry.register_prefetch("test_prefetch")
        self.registry.unregister_prefetch("test_prefetch")
        self.assertNotIn("test_prefetch", self.registry.prefetches)

    def test_unregister_children_prefetch(self):
        self.registry.register_children_prefetch("test_children_prefetch")
        self.registry.unregister_children_prefetch("test_children_prefetch")
        self.assertNotIn("test_children_prefetch", self.registry.children_prefetches)

    def test_unregister_select_related(self):
        self.registry.register_select_related("test_select")
        self.registry.unregister_select_related("test_select")
        self.assertNotIn("test_select", self.registry.select_related)

    def test_get_prefetches(self):
        self.registry.register_prefetch("test_prefetch")
        prefetches = self.registry.get_prefetches()
        self.assertIn("test_prefetch", prefetches)

    def test_get_children_prefetches(self):
        self.registry.register_children_prefetch("test_children_prefetch")
        children_prefetches = self.registry.get_children_prefetches()
        self.assertIn("test_children_prefetch", children_prefetches)

    def test_get_select_related(self):
        self.registry.register_select_related("test_select")
        select_related = self.registry.get_select_related()
        self.assertIn("test_select", select_related)

    def test_get_key_string(self):
        key = self.registry._get_key("test_key")
        self.assertEqual(key, "test_key")

    def test_get_key_prefetch_object(self):
        prefetch = Prefetch("test_prefetch")
        key = self.registry._get_key(prefetch)
        self.assertEqual(key, "test_prefetch")

    def test_get_key_callable(self):
        def test_callable():
            pass

        key = self.registry._get_key(test_callable)
        self.assertEqual(key, "test_callable")

    def test_get_key_unsupported_type(self):
        with self.assertRaises(ValueError):
            self.registry._get_key(123)

    def test_default_prefetch_registry(self):
        registry = DefaultPrefetchRegistry()

        self.assertIn("product_class", registry.get_select_related())
        self.assertIn("parent", registry.get_select_related())

        prefetches = registry.get_prefetches()
        self.assertIn("images", prefetches)
        self.assertIn("stockrecords", prefetches)
        self.assertIn("categories", prefetches)
        self.assertIn("parent__product_class", prefetches)
        self.assertIn("parent__images", prefetches)
        self.assertIn("prefetch_attribute_values", prefetches)
        self.assertIn("prefetch_browsable_categories", prefetches)
        self.assertIn("prefetch_public_children_stockrecords", prefetches)

        children_prefetches = registry.get_children_prefetches()
        self.assertIn("children__images", children_prefetches)
        self.assertIn("children__stockrecords", children_prefetches)
