# TypeSafe AI / Jev — vendor documentation notes (fetched 2026-10-11)

Sources: https://docs.typesafe.ai/concepts/system-one, https://docs.typesafe.ai/primitives/choice,
https://jevtypesafeai.com/decide/docs, https://jevtypesafeai.com/how-to-use

- "System One" models: discriminative, return typed answers + probabilities, never generate text.
- Endpoint: `POST https://api.typesafe.ai/v1/systemone` (docs also show `/v1/decide`), bearer auth `TYPESAFE_API_KEY`.
- Body: `model` (`jev-latest` or pinned e.g. `jev-1.13.0`), `state` (string | object | array, ~64k tokens incl. questions), `questions` map.
- Question types: `choice` (≤255 labelled options, criteria = option → description), `score` (ordered), `noul` (boolean probability).
- Multiple questions evaluated in one round trip.
- Choice answer: `choice`, `probabilities` (sum 1), `confidence` = (p_max − 1/n) / (1 − 1/n).
- Example usage block: 62 input tokens → cost_usd 0.000026.
- Vendor states calibration is measured over groups; does not guarantee individual correctness.
- Latency: the user's spec claims 70–150 ms; NOT confirmed by the fetched docs.
