#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { DataIngestionStack } from '../lib/data-ingestion-stack';
import { TrustStack } from '../lib/trust-stack';
import { GlueCdkStack } from '../lib/glue-stack';

const app = new cdk.App();

new TrustStack(app, 'TrustStack', {});
new DataIngestionStack(app, 'DataIngestionStack', {});
new GlueCdkStack(app, 'GlueCdkStack', {});