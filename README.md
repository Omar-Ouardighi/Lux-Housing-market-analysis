Lux Housing Market Analysis
This project is a cloud-based solution for analyzing the housing market in Luxembourg. It uses AWS Cloud Development Kit (CDK) to define cloud resources in a programmatic way.

Project Structure
The project consists of three main components, each represented by a stack:

TrustStack: This stack is responsible for managing trust relationships and permissions.

DataIngestionStack: This stack is responsible for data ingestion. It might include resources like S3 buckets, Glue crawlers, and more.

GlueCdkStack: This stack is responsible for managing AWS Glue resources. AWS Glue is a fully managed extract, transform, and load (ETL) service that makes it easy to prepare and load your data for analytics.

![Architecture Design](img\diagram.png)