// USER SECTIONS 
Table users {
  id uuid [pk] // have same id as supabase auth user
  email varchar [not null, unique]
  first_name varchar
  last_name varchar
  gender boolean 
  born_date datetime
  city varchar
  job varchar
  last_login timestampz [default: `now()`]
  provider enum // FACEBOOK, GOOGLE, EMAIL
  created_at timestamptz [default: `now()`]
  updated_at timestampz [default: `now()`]
} 

Table memberships {
  id uuid [pk]
  name varchar [not null, unique] // bronze, silver, gold 
  points int
  max_cards int
  max_receipt_scans_per_month int
  max_cashback_calculations_per_month int
  created_at timestamptz [default: `now()`]
}

Table user_memberships { 
  id uuid [pk]
  user_id uuid [not null, ref: > users.id]
  membership_id uuid [not null, ref: > memberships.id]
  status varchar [not null] // active, expired, canceled
  started_at timestamptz [not null]
  expired_at timestamptz
  created_at timestamptz [default: `now()`]
}

// SOURCE OF TRUTH FOR BANKING 
Table banks {
  id uuid [pk]
  swift_code  varchar(20)
  name varchar(50) [not null]
  short_name varchar(30) [not null]
  created_at timestamptz [default: `now()`]
}

Table cards {
  id uuid [pk]
  bank_id uuid [not null, ref: > banks.id]
  name varchar [not null]
  network varchar // Visa, Mastercard, JCB, Amex
  card_type varchar [default: 'credit'] // credit, debit
  annual_fee numeric(14,2)
  source_url text
  is_active boolean [default: true]
  created_at timestamptz [default: `now()`]
}

Table user_cards {
  id uuid [pk]
  user_id uuid [not null, ref: > users.id]
  credit_card_id uuid [not null, ref: > cards.id]
  nickname varchar
  billing_cycle_day int
  is_default boolean [default: false]
  has_annual_fee boolean [default: false]
  created_at timestamptz [default: `now()`]
}

Table merchant_category_codes {
  code varchar(4) [pk, unique]
  description text [not null]
  category enum  
/*
Agricultural services
Contracted services
Transportation services
Utility services
Retail outlet services
Clothing shops
Utilities
Miscellaneous shops
Business services
Professional services and membership organizations
Government services
*/
  is_active boolean [default: true]
  valid_payment enum // V - VISA, M - MASTERCARD, VM - BOTH V and M, TSYS - TSYS System 
  created_at timestamptz [default: `now()`]
  updated_at timestamptz [default: `now()`]
}

Table merchants {
  id uuid [pk]
  branch text [not null]
  brand text [not null]
  mcc_code varchar(4) [ref: > merchant_category_codes.code]
  created_at timestamptz [default: `now()`]
}

Table transactions {
  id uuid [pk]
  user_card_id uuid [not null, ref: > user_cards.id]
  merchant_id uuid [ref: > merchants.id]
  transaction_date timestamptz [not null]
  amount numeric(15,2) [not null]
  mcc_source enum // bank_statement, user_feedback, predicted, admin_verified
  cashback_estimated_amount numeric(15,2)
  source varchar [default: 'manual'] // manual, receipt_scan, notification, import
  note text
  location varchar // tp.hcm, ha noi, ...
  created_at timestamptz [default: `now()`]
  updated_at timestamptz [default: `now()`]
}

Table merchant_mcc_feedbacks {
  id uuid [pk]
  user_id uuid [not null, ref: > users.id]
  merchant_id uuid [not null, ref: > merchants.id]
  transaction_id uuid [ref: > transactions.id]
  suggested_mcc_code varchar(4) [not null, ref: > merchant_category_codes.code]
  evidence_type varchar // receipt, bank_statement, notification, user_memory
  note text
  status varchar [default: 'pending'] // pending, accepted, rejected
  created_at timestamptz [default: `now()`]

  indexes {
    (merchant_id, suggested_mcc_code)
    (user_id, merchant_id, transaction_id)
  }
}

Table reward_rules {
  id uuid [pk]
  credit_card_id uuid [not null, ref: > cards.id]
  name varchar [not null] // Dining cashback, Online cashback
  reward_type varchar [not null] // cashback, points, miles
  cashback_rate numeric(6,4) // 0.0500 = 5%
  points_rate numeric(10,4)
  monthly_cap_amount numeric(14,2)
  minimum_transaction_amount numeric(14,2)
  minimum_monthly_spend numeric(14,2)
  eligible_channel varchar [default: 'any'] // offline, online, any
  conditions_text text
  effective_from date
  effective_to date
  source_url text
  is_active boolean [default: true] 
  created_at timestamptz [default: `now()`]
}

Table reward_rule_mccs {
  id uuid [pk]
  reward_rule_id uuid [not null, ref: > reward_rules.id]
  mcc_code varchar(4) [not null, ref: > merchant_category_codes.code]
  match_type enum [not null] // eligible, excluded

  indexes {
    (reward_rule_id, mcc_code, match_type) [unique]
  }
}

Table cashback_calculations {
  id uuid [pk]
  transaction_id uuid [not null, ref: > transactions.id]
  user_card_id uuid [not null, ref: > user_cards.id]
  reward_rule_id uuid [ref: > reward_rules.id]
  estimated_cashback_amount numeric(14,2)
  applied_rate numeric(6,4)
  explanation text
  status varchar [default: 'estimated'] // estimated, confirmed, rejected
  created_at timestamptz [default: `now()`]
} 
