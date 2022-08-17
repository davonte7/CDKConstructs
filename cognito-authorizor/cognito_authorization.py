from constructs import Construct
from aws_cdk import (
    RemovalPolicy,
    aws_cognito as cognito,
    CfnOutput,
    Duration
)


class CognitoAuthorization(Construct):

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # User Pool
        user_pool = cognito.UserPool(self, 'mc-userpool',
                                     enable_sms_role=True,
                                     password_policy=cognito.PasswordPolicy(min_length=12,
                                                                            require_lowercase=True,
                                                                            require_uppercase=True,
                                                                            require_digits=True,
                                                                            require_symbols=True,
                                                                            temp_password_validity=Duration.days(1)),
                                     self_sign_up_enabled=True,
                                     sign_in_aliases=cognito.SignInAliases(username=True, email=True),
                                     auto_verify=cognito.AutoVerifiedAttrs(email=True, phone=False),
                                     user_verification=cognito.UserVerificationConfig(
                                         email_style=cognito.VerificationEmailStyle.LINK)
                                     )

        # Cognito Client
        user_pool_client = cognito.UserPoolClient(self, 'mc-userpool-client',
                                                  user_pool=user_pool,
                                                  id_token_validity=Duration.hours(1),
                                                  access_token_validity=Duration.hours(1),
                                                  refresh_token_validity=Duration.days(1),
                                                  prevent_user_existence_errors=True
                                                  )

        # Identity Pool
        identity_pool = cognito.CfnIdentityPool(self, 'mc-identity-pool',
                                                allow_unauthenticated_identities=True,
                                                cognito_identity_providers=[
                                                    cognito.CfnIdentityPool.CognitoIdentityProviderProperty(
                                                        client_id=user_pool_client.user_pool_client_id,
                                                        provider_name=user_pool.user_pool_provider_name
                                                    )
                                                ]
                                                )

        CfnOutput(scope=self, id='UserPoolID', value=user_pool.user_pool_id, export_name="UserPoolID")
        CfnOutput(scope=self, id='ClientID', value=user_pool_client.user_pool_client_id, export_name="ClientID")
        CfnOutput(scope=self, id='IdentityPoolID', value=identity_pool.ref, export_name="IdentityPoolID")
        CfnOutput(scope=self, id='UserPoolARN', value=user_pool.user_pool_arn, export_name="UserPoolARN")