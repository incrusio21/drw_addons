# Copyright (c) 2023, DAS and contributors
# For license information, please see license.txt

from base64 import b32encode, b64encode
from io import BytesIO

def get_qr_svg_code_asset(items):
	maks_per_row = 2
	qr_code = {}
	for row in items:
		qr = get_qr_svg_code(row.asset)

		bari_qr = len(qr_code) or 1
		if qr_code.get(bari_qr) and len(qr_code[bari_qr]) >= maks_per_row:
			bari_qr += 1

		qr_code.setdefault(bari_qr, [])
		qr_code[bari_qr].append({
			"name": row.asset,
			"qr": qr
		})

	return qr_code

def get_qr_svg_code(totp_uri):
	"""Get SVG code to display Qrcode for OTP."""
	from pyqrcode import create as qrcreate

	url = qrcreate(totp_uri)
	svg = ""
	stream = BytesIO()
	try:
		url.svg(stream, scale=6, module_color="#222")
		svg = stream.getvalue().decode().replace("\n", "")
		svg = b64encode(svg.encode())
	finally:
		stream.close()

	return svg.decode()