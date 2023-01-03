/*
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: Apache-2.0
*/

/*
 NIST Compliant Lambda Function Construct
*/

import * as awsLambda from 'aws-cdk-lib/aws-lambda';
import * as logs from 'aws-cdk-lib/aws-logs';
import { Construct } from 'constructs';

const runtimes: any = {
  PYTHON: awsLambda.Runtime.PYTHON_3_9,
  NODE: awsLambda.Runtime.NODEJS_16_X,
  JAVA: awsLambda.Runtime.JAVA_11,
  GO: awsLambda.Runtime.GO_1_X,
  RUBY: awsLambda.Runtime.RUBY_2_7,
  CONTAINER: awsLambda.Runtime.FROM_IMAGE,
  DOTNET: awsLambda.Runtime.DOTNET_CORE_3_1,
};

export interface NistLambdaProps {

  /**
   * Source for Lambda Code
   * @type {awsLambda.Code}
   * @memberof NistLambdaProps
   */
  readonly code: awsLambda.Code;

  /**
   * Pointer to Lambda Handler
   * @type {string}
   * @memberof NistLambdaProps
   */
  readonly handler: string;

  /**
   * Programming Language of Lambda Function to be used to get Version
   * @type {NistRuntime}
   * @memberof NistLambdaProps
   */
  readonly runtime: 'PYTHON' | 'NODE' | 'JAVA' | 'GO' | 'RUBY' | 'CONTAINER' | 'DOTNET';

  /**
   * Additional options for Lambda Function
   * @type {awsLambda.FunctionOptions}
   * @memberof NistLambdaProps
   */
  readonly options?: awsLambda.FunctionOptions;
}


export class NistFunction extends Construct {
  // secureFunction: awsLambda.Function;
  static create(scope: Construct, id: string, props: NistLambdaProps) {
    const secureFunction = new awsLambda.Function(scope, id, {
      code: props.code,
      handler: props.handler,
      logRetention: logs.RetentionDays.TEN_YEARS,
      runtime: runtimes[props.runtime],
      ...props.options,
    });
    return secureFunction;
  }

  /**
 * Provides a Lambda Function adhering to NIST SP 800-53 Revision 4 security standards.
 */
  constructor(scope: Construct, id: string) {
    super(scope, id);

    // this.secureFunction = new awsLambda.Function(scope, id, {
    //   code: props.code,
    //   handler: props.handler,
    //   logRetention: logs.RetentionDays.TEN_YEARS,
    //   runtime: runtimes[props.runtime],
    //   ...props.options,
    // });

  }
}
