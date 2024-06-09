#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { DataIngestionStack } from '../lib/data-ingestion-stack';
import { TrustStack } from '../lib/trust-stack';

const app = new cdk.App();
new DataIngestionStack(app, 'DataIngestionStack', {});
new TrustStack(app, 'TrustStack', {});