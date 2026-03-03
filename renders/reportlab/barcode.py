from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Flowable
from reportlab.graphics.barcode import code39, code128, qr  # Import code39
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

class BarcodeFlowable(Flowable):
    """A flowable that renders a barcode"""
    def __init__(self, barcode_value, barcode_type='code39', width=50*mm, height=15*mm):
        Flowable.__init__(self)
        self.barcode_value = barcode_value
        self.barcode_type = barcode_type
        self.width = width
        self.height = height
        
    def draw(self):
        if self.barcode_type == 'code39':
            # Code39 barcode
            barcode = code39.Standard39(
                self.barcode_value,
                barHeight=self.height*0.6,
                barWidth=0.25*mm,
                humanReadable=False,  # Show text below barcode
                checksum=0  # 0=no checksum, 1=add checksum
            )
            barcode.drawOn(self.canv, 0, 0)
        elif self.barcode_type == 'code128':
            # Code128 barcode (for comparison)
            barcode = code128.Code128(
                self.barcode_value,
                barHeight=self.height*0.6,
                barWidth=0.4*mm
            )
            barcode.drawOn(self.canv, 0, 0)
        elif self.barcode_type == 'qr':
            # QR code
            qr_code = qr.QrCodeWidget(self.barcode_value)
            bounds = qr_code.getBounds()
            qr_width = bounds[2] - bounds[0]
            qr_height = bounds[3] - bounds[1]
            drawing = Drawing(self.width, self.height, transform=[self.width/qr_width, 0, 0, self.height/qr_height, 0, 0])
            drawing.add(qr_code)
            renderPDF.draw(drawing, self.canv, 0, 0)
