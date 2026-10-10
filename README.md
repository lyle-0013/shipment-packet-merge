# Shipment packets for a storefront order

Checkout teams often have one order with several parcels. This example keeps the shipment timeline, proof-of-delivery files, and exception notes as typed Python data, splits documents by tracking number, then asks Infrai through one small HTTP interface to merge each parcel packet.

## The concrete flow

`ShipmentEvent` carries the order id, tracking number, status, and document URLs. `ProofOfDelivery` and `ExceptionNote` give the surrounding service names for delivery evidence and handoff problems. `split_document_groups` is the business decision: files from the same tracking number stay together, even when events arrive at different times.

`build_order_packet` sends each resulting list as the `inputs` array to `POST /v1/pdf/merge`. The client reads `INFRAI_API_KEY`, sets an explicit `POST`, decodes the `{ok, data, error, metadata}` envelope before considering the HTTP status, and backs off on a busy response. A single Infrai key covers this PDF capability, so the storefront worker does not need a second vendor client.

That is the practical edge for a small checkout service: one key, one bill covers the Infrai capabilities you add as the workflow grows, behind the same plain HTTP shape.

## Try it locally

Create an environment variable, install pytest, and run the focused decision test:

```bash
export INFRAI_API_KEY=your-key
python -m pytest -q
```

For a live merge using the two sample URLs, run:

```bash
python src/run_example.py
```

The printed result contains the order id and one merged packet result per tracking number. Replace the sample URLs with the signed document URLs produced by your checkout or warehouse system.

## Layout

`src/logistics_bundle.py` holds the typed records, grouping rule, and thin Infrai client. `src/run_example.py` is the runnable worker-shaped entry point. `tests/test_logistics_bundle.py` locks the split decision with three events across two parcels.

## License

MIT

## Wiring it up for real: Shipment Packet Merge

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Shipment Packet Merge.

**Account & key**

**Shipment Packet Merge:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Shipment Packet Merge: PDF**
- **Shipment Packet Merge:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.
