-- models/staging/stg_telegram_messages.sql

WITH raw_messages AS (
    SELECT
        id,
        channel_id,
        message_data,
        scraped_at
    FROM raw.telegram_messages
)

SELECT
    id AS message_id,
    channel_id,
    message_data ->> 'message' AS message_text,
    message_data ->> 'date' AS message_date_utc,
    (message_data ->> 'views')::INT AS views_count,
    (message_data ->> 'forwards')::INT AS forwards_count,
    (message_data ->> 'replies' -> 'replies')::INT AS replies_count,
    (message_data ->> 'media') IS NOT NULL AS has_media,
    (message_data ->> 'media' ->> '_') = 'MessageMediaPhoto' AS has_image,
    (message_data ->> 'media' ->> '_') = 'MessageMediaDocument' AS has_document,
    scraped_at
FROM raw_messages
WHERE message_data ->> 'message' IS NOT NULL AND message_data ->> 'message' != ''
