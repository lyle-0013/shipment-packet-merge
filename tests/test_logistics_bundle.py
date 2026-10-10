from logistics_bundle import ShipmentEvent, split_document_groups


def test_documents_are_split_per_tracking_number():
    events = [
        ShipmentEvent("order-1", "A", "packed", ["label-a", "invoice-a"]),
        ShipmentEvent("order-1", "B", "packed", ["label-b"]),
        ShipmentEvent("order-1", "A", "delivered", ["pod-a"]),
    ]
    assert split_document_groups(events) == [["label-a", "invoice-a", "pod-a"], ["label-b"]]
