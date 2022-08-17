from constructs import Construct
from aws_cdk import (
    RemovalPolicy,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_lambda as lambda_,
    aws_codecommit as codecommit,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions,
    aws_iam as iam,
    Duration,
    Aws
)


class ReactPipeline(Construct):

    def __init__(self, scope: Construct, id: str,distro: cloudfront.Distribution, bucket: s3.Bucket, **kwargs):
        super().__init__(scope, id, **kwargs)

        python_lambda_kwargs = {
                'handler': 'lambda_function.lambda_handler',
                'runtime': lambda_.Runtime.PYTHON_3_9,
                'timeout': Duration.minutes(2)
            }
     
        # Invalidate Cache Lambda
        invalidate_cache = lambda_.Function(self, 'invalidate-cache', **python_lambda_kwargs,
                                            code=lambda_.Code.from_asset('app_cdk/assets/lambdas/invalidate-cache'),
                                            initial_policy=[iam.PolicyStatement(
                                                actions=["cloudfront:CreateInvalidation",
                                                         "cloudfront:CreateInvalidation",
                                                         "codepipeline:PutJobFailureResult", ],
                                                resources=[("arn:aws:cloudfront::" + str(
                                                    Aws.ACCOUNT_ID) + ":distribution/" + distro.distribution_id),
                                                           "arn:aws:pipeline::" + str(Aws.ACCOUNT_ID) + ":*"
                                                           ])],
                                            function_name="cdk-invalidate-cache")

        # CodeCommit
        repo = codecommit.Repository(self, 'mc-code-commit', repository_name="Meeting-Compress")
        repo.apply_removal_policy(RemovalPolicy.RETAIN)

        # CodeBuild
        mc_build_project = codebuild.PipelineProject(
            scope=self,
            id=f"Meeting-Compress-Build{id}",
            environment=codebuild.BuildEnvironment(privileged=True),
            build_spec=codebuild.BuildSpec.from_object(
                dict(
                    version="0.2",
                    phases={
                        "install": {"commands": ["n 14.18.3", "npm install"]},
                        "build": {"commands": ["INLINE_RUNTIME_CHUNK=false npm run build"]},
                    },
                    artifacts={
                        "files": ["./*", "static/css/*", "static/js/*", "static/media/*"],
                        "base-directory": "build/",
                        "discard-paths": "no",
                    }
                )
            ),
        )

        # CodePipeline
        source_output = codepipeline.Artifact()
        mc_build_output = codepipeline.Artifact("CDK-BUILD-OUTPUT")
        codepipeline.Pipeline(self, "Meeting-Compress-Pipeline",
                              pipeline_name="Meeting-Compress-Pipeline",
                              stages=[
                                  codepipeline.StageProps(
                                      stage_name="Source",
                                      actions=[
                                          codepipeline_actions.CodeCommitSourceAction(
                                              action_name="Get_Source",
                                              repository=repo,
                                              output=source_output,
                                              branch="main"
                                          )

                                      ]
                                  ),
                                  codepipeline.StageProps(
                                      stage_name="Build",
                                      actions=[
                                          codepipeline_actions.CodeBuildAction(
                                              action_name="Meeting-Compress-Build",
                                              project=mc_build_project,
                                              input=source_output,
                                              outputs=[mc_build_output]
                                          )
                                      ]
                                  ),
                                  codepipeline.StageProps(
                                      stage_name="Deploy",
                                      actions=[
                                          codepipeline_actions.S3DeployAction(
                                              action_name="Deploy_Website",
                                              bucket=bucket,
                                              input=mc_build_output
                                          )
                                      ]
                                  ),
                                  codepipeline.StageProps(
                                      stage_name="Invalidate-Cache",
                                      actions=[
                                          codepipeline_actions.LambdaInvokeAction(
                                              action_name="Invalidate_Cache",
                                              lambda_=invalidate_cache,
                                              user_parameters={
                                                  'distributionId': distro.distribution_id,
                                                  'objectPaths': ["/*"]}
                                          )
                                      ]
                                  )
                              ],
                              )