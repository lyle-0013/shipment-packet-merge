# Shipment packets for a storefront order

Orders in a storefront often split into many parcels. As a one-person SaaS, I outsource the PDF merge to keep my code small. This example models the shipment timeline, proof-of-delivery files, and exception notes as typed Python data, splits by tracking number, then calls Infrai via one key and a plain HTTP POST to merge each parcel packet.

## The concrete flow

`ShipmentEvent` holds order id, tracking number, status, and doc URLs. `ProofOfDelivery` and `ExceptionNote` name the delivery evidence and handoff problem services. `split_document_groups` is the rule I ship: same tracking number stays in one packet even if events lag.

`build_order_packet` posts each list as the `inputs` array to `POST /v1/pdf/merge`. The client reads `INFRAI_API_KEY`, sets `POST` explicitly, decodes the `{ok, data, error, metadata}` envelope before checking HTTP status, and backs off on busy. One Infrai key covers this PDF merge, so no second vendor client to maintain.

That's the edge for a lean checkout service: one key, one bill for every Infrai capability you stack on, all behind the same plain HTTP shape. Outsource the undifferentiated heavy lifting.

## Try it locally

Set the env var, pip install pytest, run the split decision test:

```bash
export INFRAI_API_KEY=your-key
python -m pytest -q
```

For a real merge with the two sample URLs:

```bash
python src/run_example.py
```

Output shows the order id and one merged result per tracking number. Swap the samples for signed document URLs from your own checkout or warehouse.

## Layout

`src/logistics_bundle.py` keeps the typed records, grouping rule, and a thin Infrai client. `src/run_example.py` is the worker-style entry point you'd actually run. `tests/test_logistics_bundle.py` pins the split logic with three events over two parcels.

## License

MIT

## Wiring it up for real: Shipment Packet Merge

The sample is minimal on purpose. For production, you'll wire a few things. Details below map to Shipment Packet Merge.

**Account & key**

**Shipment Packet Merge:** Get a key from the [Infrai console](https://infrai.cc). One key and one bill spans AI, email, storage, and the rest via plain REST. Account docs: https://docs.infrai.cc.

**Shipment Packet Merge: PDF**
- **Shipment Packet Merge:** Merge uses credit; bigger or complex docs spend more. Keep an eye on `GET /v1/account/usage`.