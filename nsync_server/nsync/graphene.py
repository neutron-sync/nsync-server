from graphql import GraphQLError


class AuthMutation:
    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        print('NARF')
        if info.context.user.is_authenticated:
            if info.context.user.username != 'tokenuser':
                return super().mutate_and_get_payload(root, info, **input)

        raise GraphQLError('Authenication Required')
