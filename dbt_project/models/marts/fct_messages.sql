-- models/marts/fct_messages.sql

SELECT
    stg.message_id,
    stg.channel_id,
    dim_c.channel_name,
    stg.message_text,
    stg.message_date_utc::TIMESTAMP AS message_timestamp,
    CAST(TO_CHAR(stg.message_date_utc::TIMESTAMP, 'YYYYMMDD') AS INT) AS date_key,
    LENGTH(stg.message_text) AS message_length,
    stg.views_count,
    stg.forwards_count,
    stg.replies_count,
    stg.has_media,
    stg.has_image,
    stg.has_document,
    stg.scraped_at
FROM {{ ref('stg_telegram_messages') }} stg
LEFT JOIN {{ ref('dim_channels') }} dim_c
    ON stg.channel_id = dim_c.channel_id
