import graphene
from graphene_django import DjangoObjectType
from crm.models import Product

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "stock")

class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        increment = graphene.Int(default_value=10)  # Increment by default 10

    updated_products = graphene.List(ProductType)
    message = graphene.String()

    def mutate(self, info, increment):
        # Query products with stock < 10
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_products = []

        for product in low_stock_products:
            product.stock += increment
            product.save()
            updated_products.append(product)

        message = f"{len(updated_products)} products restocked successfully."
        return UpdateLowStockProducts(updated_products=updated_products, message=message)

class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()
