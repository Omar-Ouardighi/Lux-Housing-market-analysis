import sys

from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import regexp_replace, trim, col

sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)


def extract_houston_from_catalog(database, listing_table_name):
    raw_listing_dynamic_frame = glueContext.create_dynamic_frame.from_catalog(
        database=database, table_name=listing_table_name
    )
    df = raw_listing_dynamic_frame.toDF()
    return df

def transform_data(df):
    """
    Transform the data
    1. Remove Euro symbol from price and convert it to integer
    2. Trim spaces from the location
    3. Remove square meter symbol and convert area to integer
    """
    df_transformed = df.withColumn("price", regexp_replace(col("price"), "[\s€\u00A0\u202f]", "").cast("integer")) \
                   .withColumn("location", trim(col("location"))) \
                   .withColumn("area", regexp_replace(col("area"), "[\sm²]", "").cast("integer")) 
    return df_transformed


def load_to_s3(glue_dynamic_frame):
    s3output = glueContext.getSink(
        path="s3://glue-luxjob-output-bucket/transformed/",
        connection_type="s3",
        updateBehavior="UPDATE_IN_DATABASE",
        partitionKeys=[],
        compression="snappy",
        enableUpdateCatalog=True,
        transformation_ctx="s3output",
    )

    s3output.setCatalogInfo(
        catalogDatabase="my_glue_database", catalogTableName="lux_flats"
    )

    s3output.setFormat("glueparquet")
    s3output.writeFrame(glue_dynamic_frame)


if __name__ == "__main__":
    database = "my_glue_database"
    listing_table_name = "housing_lu_omar"
    df_listing = extract_houston_from_catalog(database, listing_table_name)
    
    df_final = transform_data(df_listing)
    # going from Spark dataframe to glue dynamic frame
    
    glue_dynamic_frame = DynamicFrame.fromDF(df_final, glueContext, "glue_etl")

    # load to s3
    load_to_s3(glue_dynamic_frame)
    
    job.commit()





