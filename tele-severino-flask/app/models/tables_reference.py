# ============================================================
# REFERÊNCIA DAS TABELAS FUTURAS DO POSTGRESQL
# ============================================================
#
# users
# - id
# - name
# - email
# - password_hash
# - account_type
# - created_at
#
# categories
# - id
# - slug
# - name
# - icon
# - tone
#
# specialists
# - id
# - user_id
# - name
# - role
# - category_slug
# - rating
# - reviews_count
# - price_per_minute
# - about
# - is_online
# - avatar_url
#
# specialist_tags
# - id
# - specialist_id
# - name
#
# calls
# - id
# - user_id
# - specialist_id
# - started_at
# - ended_at
# - total_seconds
# - total_value
# - status
#
# payments
# - id
# - user_id
# - specialist_id
# - call_id
# - amount
# - method
# - status
# - created_at
# - paid_at
#
# reviews
# - id
# - user_id
# - specialist_id
# - call_id
# - rating
# - comment
# - created_at
#
# platform_settings
# - id
# - platform_name
# - primary_color
# - logo_url
# - updated_at
# ============================================================
