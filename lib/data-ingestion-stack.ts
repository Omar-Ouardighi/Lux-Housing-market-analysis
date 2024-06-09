import * as cdk from 'aws-cdk-lib';
import * as path from 'path';
import { Construct } from 'constructs';
import {aws_lambda as lambda, aws_iam as iam, aws_s3 as s3} from 'aws-cdk-lib';


export class DataIngestionStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

  // Create a role for the Lambda function
  const luxRole = new iam.Role(this, 'luxRole', {
    roleName: 'luxRole',
    assumedBy: new iam.CompositePrincipal(
      new iam.ServicePrincipal('lambda.amazonaws.com'),
      new iam.ServicePrincipal('glue.amazonaws.com')
    ),
    managedPolicies: [
      iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
      iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSGlueServiceRole')
    ],
    inlinePolicies: {
      'S3Policy': new iam.PolicyDocument({
        statements: [
          new iam.PolicyStatement({
            actions: ['s3:*'],
            resources: ['*'],
          }),
        ],
      }),
    },
  });

    const bucket = new s3.Bucket(this, 'luxBucket', {
      bucketName: 'housing-lu-omar',
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

  // Create a Lambda Layer with requests
    const scrapeLayer = new lambda.LayerVersion(this, 'scrapeLayer', {
      layerVersionName: 'scrapeLayer',
      code: lambda.Code.fromAsset(path.join(__dirname, 'lambda-layer')),
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_12],
      description: 'A layer with BeautifulSoup4, lxml, Requests and pandas',
      compatibleArchitectures: [lambda.Architecture.X86_64],

    });

    const ingestionLambda = new lambda.Function(this, 'IngestionLambda', {
      functionName: 'IngestionLambda',
      runtime: lambda.Runtime.PYTHON_3_12,
      code: lambda.Code.fromAsset('etl'),
      handler: 'scraper.handler',
      role: luxRole,
      layers: [scrapeLayer],
      timeout: cdk.Duration.minutes(15),
  })
    
}
}
