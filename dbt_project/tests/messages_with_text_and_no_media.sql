-- dbt_project/tests/messages_with_text_and_no_media.sql
-- This test is referenced in fct_messages.yml

SELECT
    message_id
FROM {{ ref('fct_messages') }}
WHERE message_text IS NOT NULL
  AND has_media = FALSE
  AND message_text ILIKE '%product%' -- Example: If a message mentions 'product', it should have an image.
  AND NOT has_image
