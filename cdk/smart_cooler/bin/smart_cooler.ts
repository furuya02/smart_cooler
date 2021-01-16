#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from '@aws-cdk/core';
import { SmartCoolerStack } from '../lib/smart_cooler-stack';

const app = new cdk.App();
new SmartCoolerStack(app, 'SmartCoolerStack');
