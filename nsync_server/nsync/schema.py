import graphene

import nsync_server.nstore.schema as nschema
import nsync_server.account.schema as aschema


class Query(aschema.Query, nschema.Query, graphene.ObjectType):
 	pass


class Mutation(aschema.Mutation, nschema.Mutation, graphene.ObjectType):
	pass

core_schema = graphene.Schema(query=Query, mutation=Mutation)
