/*
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: Apache-2.0
*/

/*
 NIST Compliant Api Gateway REST API Construct
*/

import * as apigw from 'aws-cdk-lib/aws-apigateway';
import * as logs from 'aws-cdk-lib/aws-logs';
import { Construct } from 'constructs';

export interface NistRestApiProps {

  /**
     * Additional options for REST API
     * @type {apigw.RestApiProps}
     * @memberof NistRestApiProps
     */
  readonly options?: apigw.RestApiProps;

}


export class NistRestApi extends Construct {

  /**
     * Provides a REST API adhering to NIST SP 800-53 Revision 4 security standards.
     */
  static create(scope: Construct, id: string, props?: NistRestApiProps) {

    let deployOptions: apigw.StageOptions = {};
    let cachingOptions: apigw.StageOptions = {};

    if (props?.options?.deploy === undefined || props?.options?.deploy === true) {

      const logGroup = new logs.LogGroup(scope, 'ApiGatewayAccessLogs');

      if (props?.options?.deployOptions?.cachingEnabled) {
        cachingOptions = {
          cacheDataEncrypted: true,
        };
      }

      deployOptions = {
        loggingLevel: apigw.MethodLoggingLevel.ERROR,
        accessLogDestination: new apigw.LogGroupLogDestination(logGroup),
        ...cachingOptions,
      };

    }
    const secureRestApi = new apigw.RestApi(scope, id, {
      ...props?.options,
      cloudWatchRole: true,
      deployOptions: deployOptions,

    });
    return secureRestApi;
  }
  constructor(scope: Construct, id: string) {
    super(scope, id);

  }
}
