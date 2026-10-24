# ReclaimAI Verified Facts and Official Citations Log

This document tracks all statutory provisions, legal deadlines, and technical protocols verified against primary sources during the Fetch-A-Thon 3.0 build.

| Domain | Statutory Authority / Protocol | Section / Rule | Key Fact / Verified Detail | Primary Source URL | Verified Date |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **E-Commerce** | Consumer Protection (E-Commerce) Rules, 2020 | Rule 5(4) | Grievance acknowledgment mandatory within **48 hours**; resolution mandatory within **1 month (30 days)**. | https://consumeraffairs.nic.in/acts-and-rules/consumer-protection/consumer-protection-e-commerce-rules-2020 | 2026-10-24 |
| **Consumer Rights** | Consumer Protection Act, 2019 (Act 35 of 2019) | Section 2(9), 2(11) | Right to seek redressal against unfair trade practices and deficiency in service. Digital filing permitted via e-Daakhil. | https://consumeraffairs.nic.in | 2026-10-24 |
| **Online Filing** | Ministry of Consumer Affairs, GOI | e-Daakhil Portal | Online consumer case filing before District, State, and National Consumer Commissions without physical presence. | https://edaakhil.nic.in | 2026-10-24 |
| **National Helpline** | Department of Consumer Affairs | NCH / INGRAM | National Consumer Helpline Toll-free 1915 / consumerhelpline.gov.in for immediate grievance logging. | https://consumerhelpline.gov.in | 2026-10-24 |
| **Aviation / Flights** | DGCA Civil Aviation Requirements | CAR Section 3, Series M, Part IV | Ticket refunds for credit card cancellations must be credited within **7 working days**; baggage loss compensation up to ₹20,000. | https://www.dgca.gov.in | 2026-10-24 |
| **Banking & UPI** | RBI Integrated Ombudsman Scheme, 2021 | RB-IOS Section 8 & 11 | Prerequisite: Entity complaint first. If unanswered in **30 days** or rejected, escalate to CMS portal. Compensation up to ₹20L + ₹1L agony. | https://cms.rbi.org.in | 2026-10-24 |
| **Interactive Cards** | Fetch.ai Agentverse / ASI:One ACP | ACP Metadata v1 | Cards require `card_protocol_version: "1"`, `card_kind`, `requires_card_interaction: "true"`, and JSON-stringified `card_payload` in `MetadataContent`. Predefined kinds: `form`, `detail`, `review`, `carousel`. | https://docs.agentverse.ai/documentation/advanced-usages/predefined-card-schemas | 2026-10-24 |
| **Payment Protocol** | Fetch.ai Payment Protocol | `payment_protocol_spec` | `Funds(payment_method="fet_direct")`, `RequestPayment`, `CommitPayment`, `CompletePayment`. On-chain verification via `cosmpy` against testnet (`atestfet`) or mainnet (`afet`). | https://innovationlab.fetch.ai/resources/docs/agent-transaction/agent-payment-protocol | 2026-10-24 |
