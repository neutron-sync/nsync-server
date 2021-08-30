from graphql import GraphQLError


class AuthMutation:
    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        if info.context.user.is_authenticated:
            if info.context.user.has_credit:
                return super().mutate_and_get_payload(root, info, **input)

            raise GraphQLError('Additional Credit Required')

        raise GraphQLError('Authenication Required')
