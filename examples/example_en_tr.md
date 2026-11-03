# A sample revision path (fictional, public text)

These fictional clauses are deliberately not legal advice.

**Source (English)**: `A customer may cancel the subscription within 14 calendar days of purchase and receive a full refund.`

**Target (Turkish, deliberately wrong)**: `Müşteri, satın alma tarihinden itibaren 7 takvim günü içinde aboneliği iptal ederek tam ücret iadesi alabilir.`

The deadline changed from **14** to **7** days. This is a material difference.

```text
submit_pair(
  "en", "tr",
  "A customer may cancel the subscription within 14 calendar days of purchase and receive a full refund.",
  "Müşteri, satın alma tarihinden itibaren 7 takvim günü içinde aboneliği iptal ederek tam ücret iadesi alabilir.",
  "Fictional subscription cancellation policy"
)
# => case_id = 1
review(1)
# => expected MATERIAL_DIFFERENCE (AI agreement is not guaranteed)
revise_target(1,
  "Müşteri, satın alma tarihinden itibaren 14 takvim günü içinde aboneliği iptal ederek tam ücret iadesi alabilir.")
# => case_id = 2
review(2)
# => expected EQUIVALENT (AI agreement is not guaranteed)
get_case(1)  # still the original immutable review
get_case(2)  # revised child record with parent_id = 1
```

Also test genuine ambiguity: `"Customer may be refunded at the company's discretion"` versus a text guaranteeing a refund. Without context, systems must avoid false certainty.