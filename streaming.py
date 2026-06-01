from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window, count, sum as spark_sum, lit
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType


spark = SparkSession.builder \
    .appName("LeBonCoinStreaming") \
    .config("spark.sql.shuffle.partitions", "2") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")


schema = StructType([
    StructField("timestamp", TimestampType(), True),
    StructField("user_id", StringType(), True),
    StructField("user_city", StringType(), True),
    StructField("product_id", StringType(), True),
    StructField("product_cat", StringType(), True),
    StructField("seller_id", StringType(), True),
    StructField("action_type", StringType(), True),
    StructField("price", DoubleType(), True)
])


df = spark.readStream \
    .schema(schema) \
    .json("data/stream")


# =========================
# 1) Statistiques streaming
# =========================

stats = df \
    .withWatermark("timestamp", "30 seconds") \
    .groupBy(
        window(col("timestamp"), "1 minute", "30 seconds"),
        col("action_type")
    ) \
    .agg(
        count("*").alias("nombre_actions"),
        spark_sum("price").alias("volume_prix")
    )


query_stats = stats.writeStream \
    .outputMode("append") \
    .format("json") \
    .option("path", "output/stats") \
    .option("checkpointLocation", "checkpoint/stats") \
    .start()


# =========================
# 2) Arêtes du graphe
# =========================

edges_user_product = df.select(
    col("user_id").alias("src"),
    col("product_id").alias("dst"),
    col("action_type").alias("relationship"),
    col("timestamp")
)

edges_seller_product = df.select(
    col("seller_id").alias("src"),
    col("product_id").alias("dst"),
    lit("PROPOSE").alias("relationship"),
    col("timestamp")
)

edges = edges_user_product.union(edges_seller_product)


query_edges = edges.writeStream \
    .outputMode("append") \
    .format("json") \
    .option("path", "output/graph") \
    .option("checkpointLocation", "checkpoint/graph") \
    .start()


print("Streaming lancé.")
print("Stats écrites dans output/stats/")
print("Graphe écrit dans output/graph/")
print("CTRL + C pour arrêter.")


spark.streams.awaitAnyTermination()
