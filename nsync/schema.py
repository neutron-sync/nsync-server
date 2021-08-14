import graphene

import nstore.schema


class Query(nstore.schema.Query, graphene.ObjectType):
 	pass


class Mutation(nstore.schema.Mutation, graphene.ObjectType):
	pass

core_schema = graphene.Schema(query=Query, mutation=Mutation)
