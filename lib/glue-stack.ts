import * as cdk from 'aws-cdk-lib';
import * as glue from 'aws-cdk-lib/aws-glue';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as s3 from 'aws-cdk-lib/aws-s3';
import { Construct } from 'constructs';
import * as path from 'path';
import * as assets from 'aws-cdk-lib/aws-s3-assets';

export class GlueCdkStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);


    // IAM Role
    const glueRole = new iam.Role(this, 'GlueRole', {
      assumedBy: new iam.ServicePrincipal('glue.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSGlueServiceRole'),
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

    // Glue Database
    const glueDatabase = new glue.CfnDatabase(this, 'GlueDatabase', {
      catalogId: '851725280651',
      databaseInput: {
        name: 'my_glue_database',
      },
    });

    // Glue Classifier
    const glueClassifier = new glue.CfnClassifier(this, 'GlueClassifier', {
      csvClassifier: {
        name: 'my_csv_classifier',
        delimiter: ',',
      }

    });

    // Glue Crawlers
    const LuxCrawler = new glue.CfnCrawler(this, 'LuxCrawler', {
      role: glueRole.roleArn,
      databaseName: glueDatabase.ref,
      targets: {
        s3Targets: [{ path: 's3://housing-lu-omar/' }],
      },
      classifiers: [glueClassifier.ref],
    });

    // Upload job script as S3 asset
    const scriptAsset = new assets.Asset(this, 'Script', {
        path: path.join(__dirname,'..', 'etl', 'glue_job.py'),
      });

    // Create Glue Job output bucket
    const jobOutputBucket = new s3.Bucket(this, 'JobOutputBucket', {});
  

    // Glue Job
    const glueJob = new glue.CfnJob(this, 'GlueJob', {
      name: 'my_glue_job',
      role: glueRole.roleArn,
      command: {
        name: 'glueetl',
        scriptLocation: `s3://${scriptAsset.s3BucketName}/${scriptAsset.s3ObjectKey}`,
        pythonVersion: '3',
      },
      glueVersion: '2.0',
      maxRetries: 3,
      timeout: 2880,
      numberOfWorkers: 2,
      workerType: 'G.1X',
    });
  }
}
