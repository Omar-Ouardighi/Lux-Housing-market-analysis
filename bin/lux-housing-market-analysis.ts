#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { DataIngestionStack } from '../lib/data-ingestion-stack';
import { TrustStack } from '../lib/trust-stack';
import { GlueCdkStack } from '../lib/glue-stack';

const app = new cdk.App();

const env = { region: 'us-east-1' }
new TrustStack(app, 'TrustStack', {
  env: env,
  description: 'Trust Stack'
});
new DataIngestionStack(app, 'DataIngestionStack', {
  env: env,
  description: 'Data Ingestion Stack'
});
new GlueCdkStack(app, 'GlueCdkStack', {
  env: env,
  description: 'Glue Cdk'
});