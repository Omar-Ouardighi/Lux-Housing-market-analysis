import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

# Initialize Glue Context
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read the data from the Glue Data Catalog
datasource = glueContext.create_dynamic_frame.from_catalog(database = "your_database_name", table_name = "your_table_name", transformation_ctx = "datasource")

# Convert DynamicFrame to DataFrame
df = datasource.toDF()

# Transform the data
# 1. Remove Euro symbol from price and convert it to integer
# 2. Trim spaces from the location
# 3. Remove square meter symbol and convert area to integer
from pyspark.sql.functions import regexp_replace, trim, col

df_transformed = df.withColumn("price", regexp_replace(col("price"), "[\s€\u202f]", "").cast("integer")) \
                   .withColumn("location", trim(col("location"))) \
                   .withColumn("area", regexp_replace(col("area"), "[\sm²]", "").cast("integer")) \
                   .withColumn("number_of_rooms", col("number_of_rooms").cast("integer")) \
                   .withColumn("number_of_bathrooms", col("number_of_bathrooms").cast("integer")) \
                   .withColumn("parking_spaces", col("parking_spaces").cast("integer"))

# Convert DataFrame back to DynamicFrame
dynamic_frame_transformed = DynamicFrame.fromDF(df_transformed, glueContext, "dynamic_frame_transformed")

# Write the transformed data back to S3
output_path = "s3://your-output-bucket/transformed-data/"
glueContext.write_dynamic_frame.from_options(frame = dynamic_frame_transformed, connection_type = "s3", connection_options = {"path": output_path}, format = "csv")

# Commit job
job.commit()
