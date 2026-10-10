import base64

from logistics_bundle import InfraiClient, ShipmentEvent, build_order_packet


def sample_pdf() -> str:
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 72 72] /Contents 4 0 R >>",
        b"<< /Length 0 >>\nstream\n\nendstream",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, body in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode() + body + b"\nendobj\n")
    xref = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode())
    pdf.extend(f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return base64.b64encode(pdf).decode("ascii")


def main() -> None:
    pdf = sample_pdf()
    events = [
        ShipmentEvent("order-1042", "TRACK-A", "label_created", [pdf, pdf]),
        ShipmentEvent("order-1042", "TRACK-B", "delivered", [pdf]),
    ]
    result = build_order_packet(events, InfraiClient())
    print(result)


if __name__ == "__main__":
    main()
