-- models/marts/dim_channels.sql

SELECT DISTINCT
    channel_id,
    -- In a real scenario, you'd join with a source that provides channel names
    -- For now, we'll use a placeholder or try to extract from message_data if available
    'Channel ' || channel_id AS channel_name, -- Placeholder
    'Description for Channel ' || channel_id AS channel_description, -- Placeholder
    CURRENT_TIMESTAMP AS created_at,
    CURRENT_TIMESTAMP AS updated_at
FROM {{ ref('stg_telegram_messages') }}
WHERE channel_id IS NOT NULL
