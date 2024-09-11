from oscar.core.loading import get_model, get_class

from .registry import PrefetchRegistry

ProductQuerySet = get_class("catalogue.managers", "ProductQuerySet")
ProductModel = get_model("catalogue", "Product")


class DefaultPrefetchRegistry(PrefetchRegistry):
    """
    This is the default prefetch registry that prefetches all the necessary fields for the product resource.
    Your project con customize this registry by either importing default_prefetch_registry and calling the
    register and unregister methods. Or you can subclass this registry, override the register method and
    pass your customized instance to the product_queryset_to_resources function.
    pr
    """

    def register(self):
        # ProductToResource.product_class -> get_product_class
        self.register_select_related(["product_class", "parent"])

        # ProductToResource.images -> get_all_images
        self.register_prefetch("images")

        # ProducToResource.map_stock_price -> fetch_for_product
        self.register_prefetch("stockrecords")

        # This gets prefetches somewhere (.categories.all()), it's not in get_categories as that does
        # .browsable() and that's where the prefetch_browsable_categories is for. But if we remove this,
        # the amount of queries will be more again. ToDo: Figure out where this is used and document it.
        self.register_prefetch("categories")

        # The parent and its related fields are prefetched in numerous places in the resource.
        # ProductToResource.product_class -> get_product_class (takes parent product_class if itself has no product_class)
        # ProductToResource.images -> get_all_images (takes parent images if itself has no images)
        self.register_prefetch("parent__product_class")
        self.register_prefetch("parent__images")

        # ProducToResource.attributes -> get_attribute_values
        def prefetch_attribute_values(queryset: ProductQuerySet, **kwargs):
            return queryset.prefetch_attribute_values(
                include_parent_children_attributes=kwargs.get("include_children", False)
            )

        self.register_prefetch(prefetch_attribute_values)

        # ProductToResource.categories -> get_categories
        # ProductToResource.categories -> get_categories -> looks up the parent categories if child
        def prefetch_browsable_categories(queryset: ProductQuerySet, **kwargs):
            return queryset.prefetch_browsable_categories()

        self.register_prefetch(prefetch_browsable_categories)

        # ProductToResource.map_stock_price -> fetch_for_parent -> product.children.public() -> stockrecords
        def prefetch_public_children_stockrecords(queryset: ProductQuerySet, **kwargs):
            return queryset.prefetch_public_children(
                queryset=ProductModel.objects.public().prefetch_related("stockrecords")
            )

        self.register_prefetch(prefetch_public_children_stockrecords)

        # Register children prefetches
        self.register_children_prefetch("children__images")
        self.register_children_prefetch("children__stockrecords")


default_prefetch_registry = DefaultPrefetchRegistry()
