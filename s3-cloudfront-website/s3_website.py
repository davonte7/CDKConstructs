from constructs import Construct
from aws_cdk import (
    RemovalPolicy,
    aws_cognito as cognito,
    CfnOutput,
    Duration,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as cf_origins,
    aws_s3 as s3
)


class S3Website(Construct):

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

    # Hosting Bucket
        self.hosting_bucket = s3.Bucket(self, 'hosting-bucket',
                                   versioned=True,
                                   encryption=s3.BucketEncryption.S3_MANAGED,
                                   block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
                                   enforce_ssl=True)

        # CloudFront
        cf_error_response = cloudfront.ErrorResponse(
            http_status=403,
            response_page_path="/index.html",
            ttl=Duration.minutes(60)
        )
        self.cloudfront_distro = cloudfront.Distribution(self, 'hosting-distro',
                                                    default_behavior=cloudfront.BehaviorOptions(
                                                        origin=cf_origins.S3Origin(self.hosting_bucket),
                                                        origin_request_policy=cloudfront.OriginRequestPolicy.CORS_S3_ORIGIN,
                                                        viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS),
                                                    default_root_object="index.html",
                                                    error_responses=[cf_error_response])


        CfnOutput(scope=self, id="CloudFrontDistro", value=self.cloudfront_distro.distribution_domain_name,
                  export_name="Cloudfront-Url")