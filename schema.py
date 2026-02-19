# alx_backend_graphql_crm/schema.py

import graphene
from crm.schema import Query as CRMQuery  # import your app's Query
# from crm.schema import Mutation as CRMMutation  # optional, if you have mutations

class Query(CRMQuery, graphene.ObjectType):
    pass

# class Mutation(CRMMutation, graphene.ObjectType):
#     pass

schema = graphene.Schema(query=Query)
