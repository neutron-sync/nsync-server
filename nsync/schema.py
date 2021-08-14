import graphene

import nstore.schema


class Query(nstore.schema.Query, graphene.ObjectType):
 	pass


core_schema = graphene.Schema(query=Query)
