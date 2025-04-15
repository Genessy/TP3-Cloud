import os
from datetime import datetime
from google.cloud import storage
import mysql.connector

def hello_gcs(event, context):
    file_data = event
    file_name = file_data['name']
    bucket_name = file_data['bucket']

    if not file_name.lower().endswith(('.jpg', '.jpeg')):
        print("Fichier non supporté.")
        return

    new_name = datetime.now().strftime("%Y%m%d%H%M%S") + ".jpg"

    storage_client = storage.Client()
    source_bucket = storage_client.bucket(bucket_name)
    source_blob = source_bucket.blob(file_name)

    dest_bucket = storage_client.bucket("xxx-public")
    dest_blob = dest_bucket.blob(new_name)
    dest_blob.copy_from(source_blob)
    source_blob.delete()

    conn = mysql.connector.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASS"],
        database=os.environ["DB_NAME"]
    )
    cursor = conn.cursor()
    cursor.execute("INSERT INTO photos (url, tags) VALUES (%s, %s)", (f"gs://xxx-public/{new_name}", ""))
    conn.commit()
    cursor.close()
    conn.close()
