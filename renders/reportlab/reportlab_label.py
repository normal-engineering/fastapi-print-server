from ctypes import alignment
from turtle import left
import barcode
from reportlab.lib import styles
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Flowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code39, code128, qr  # Import code39
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, KeepInFrame
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.rl_config import defaultPageSize
from barcode import BarcodeFlowable


try:
    # Try to register Noto Sans CJK fonts (best option)
    pdfmetrics.registerFont(TTFont('ChineseFont', 'shared/fonts/NotoSansTC-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('ChineseFont-Bold', 'shared/fonts/NotoSansTC-Bold.ttf'))
    CHINESE_FONT = 'ChineseFont'
    CHINESE_FONT_BOLD = 'ChineseFont-Bold'
    print("Noto Sans CJK fonts registered successfully")
except Exception as e:
    print(f"Warning: Could not register Noto CJK fonts: {e}")

def table_custom(data, width, height, style):
    single = Table(data, colWidths=width, rowHeights=height)
    single.setStyle(style)
    return single

def create_sticker(data):
    obtnumber = data.get('obtnumber')
    dream_factory_qr = BarcodeFlowable(f"{data.get('date_shipping').replace('-', '')}|{obtnumber}", 'qr', width=18*mm, height=18*mm)

    styles = getSampleStyleSheet()
    style_normal = ParagraphStyle('Address', parent=styles["Normal"], fontSize=6, fontName=CHINESE_FONT)

    styles = TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ])

    style_left_table = TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONT', (0, 0), (-1, 0), CHINESE_FONT_BOLD),
        ('FONT', (0, 0), (0, -1), CHINESE_FONT_BOLD),  
        ('FONT', (1, 1), (-1, -1), CHINESE_FONT),       
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('FONT', (0, -3), (-1, -1), CHINESE_FONT_BOLD),  
        ('LEFTPADDING', (1, 0), (-1, -1), -2),  
        ('FONTSIZE', (0, 7), (-1, -3), 8),
    ])

    style_right_table = TableStyle([
        ('INNERGRID', (0, -2), (-3, -1), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('FONT', (0, 0), (-1, -1), CHINESE_FONT),       
        ('ALIGN', (0, 0), (-1, -2), 'LEFT'),
        ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
        ('FONTSIZE', (-1, -1), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 0.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), -0.5),
        ('LEFTPADDING', (0, 0), (-1, -1), -2),  
    ])

    left_table = [ 
        [table_custom(data=[
            [data.get('customer_no'), data.get('customer')],
            ['送貨日期:', data.get('date_shipping')], 
            ['送貨時間:', f'{data.get('time_delivery_start')}~{data.get('time_delivery_start')}'], 
            ['收件人:', data.get('recipient')],
            ['電話:', data.get('mobile')],
            ['地址:', Paragraph(data.get('address'), style_normal)],
            ['', ''],
            ['', f'{data.get('transport')} {data.get('thermo')}'],
            ['訂單編號:', data.get('sub')],
            ['備註:', Paragraph(data.get('comment'), style_normal)],
        ], width=[12*mm, 58*mm], height=None, style=style_left_table), 
        table_custom(data=[
            ['花錦織風呂敷自組禮盒', '[', '/20]'], 
            ['客製化婚卡', '[', '/1]'],
            ['', '', '第2箱/共5箱']
        ], width=[81*mm, 9*mm, 9*mm], height=None, style=style_right_table),
        dream_factory_qr],
    ]  

    sticker = Table(left_table, colWidths=[68*mm, 99*mm, 20*mm], rowHeights=65*mm)
    sticker.setStyle(styles)
    return sticker

def create_label(data):

    postnumber = data.get('postnumber')
    obtnumber = data.get('obtnumber')

    postnumber_barcode = BarcodeFlowable(postnumber, 'code39', width=40*mm, height=14*mm)
    obtnumber_barcode = BarcodeFlowable(obtnumber, 'code39', width=45*mm, height=8*mm)
    obtnumber_barcode_big = BarcodeFlowable(obtnumber, 'code39', width=60*mm, height=14*mm)
    
    tcat_qr = BarcodeFlowable(f"01|{obtnumber}|10|{data.get('customer_id')[:-2]}|N||01|01|+{postnumber.replace('-', '')}||01|||||||||||||", 'qr', width=18*mm, height=18*mm)

    styles = getSampleStyleSheet()

    style_normal = ParagraphStyle('Address', parent=styles["Normal"], fontSize=7, leading=9, fontName=CHINESE_FONT_BOLD)

    style_left = TableStyle([
        ('FONT', (0, 0), (-1, -1), CHINESE_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, 0), 40),
        ('RIGHTPADDING', (0, 1), (-1, 1), 40),
        ('RIGHTPADDING', (0, 2), (-1, 2), 15),
        ('RIGHTPADDING', (0, 3), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 2), (-1, 2), 5),
        ('BOTTOMPADDING', (0, 2), (-1, -1), 0),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
    ])

    style_left_sub = TableStyle([
        ('FONT', (0, 0), (0, -1), CHINESE_FONT_BOLD),
        ('FONT', (1, 0), (-1, -1), CHINESE_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 2), (-1, -1), 0),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ])

    style_left_4_grid = TableStyle([
        ('BOX', (0, 0), (-1,-1), 0.25, colors.black),
        ('INNERGRID', (0 ,0), (-1, -1), 0.25, colors.black),
        ('FONT', (0, 0), (-1, 1), CHINESE_FONT_BOLD),
        ('FONT', (0, 1), (-1, -1), CHINESE_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ])

    style_left_2_grid = TableStyle([
        ('BOX', (0, 0), (-1,-1), 0.25, colors.black),
        ('INNERGRID', (0 ,0), (-1, -1), 0.25, colors.black),
        ('FONT', (0, 0), (-1, 1), CHINESE_FONT_BOLD),
        ('FONT', (0, 1), (-1, -1), CHINESE_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ])

    style_left_recipient_grid = TableStyle([
        ('FONT', (0, 0), (-1, -1), CHINESE_FONT),
        ('FONT', (0, 1), (-1, 1), CHINESE_FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('FONTSIZE', (0, 1), (-1, -2), 10),
        ('TOPPADDING', (0, 0), (-1, -1), -1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), -1),
        ('ALIGN', (0, 0), (-1, 2), 'LEFT'),
        ('ALIGN', (0, 2), (-1, -1), 'RIGHT'),
    ])

    style_left_sender_grid = TableStyle([
        ('FONT', (0, 0), (-1, -1), CHINESE_FONT),
        ('FONT', (0, 1), (-1, 1), CHINESE_FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('ALIGN', (0, 0), (-1, 2), 'LEFT'),
        ('ALIGN', (0, 2), (-1, -1), 'RIGHT'),
    ])

    style_left_address_grid = TableStyle([
        ('BOX', (0, 0), (-1,-1), 0.25, colors.black),
        ('INNERGRID', (0 ,0), (-1, -1), 0.25, colors.black),
        ('FONT', (0, 0), (-1, 1), CHINESE_FONT_BOLD),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),     
    ])

    style_right_barcode = TableStyle([
        ('FONT', (0, 0), (-1, -1), CHINESE_FONT),
        ('FONTSIZE', (0, 0), (-1, 0), 20),
        ('TOPPADDING', (0, 0), (0, 0), -6.75),
        ('FONT', (1, 0), (-2, -1), CHINESE_FONT_BOLD),
        ('TOPPADDING', (1, 0), (-2, 0), 8),
        ('LEFTPADDING', (0, 0), (0, 0), -12),
        ('TOPPADDING', (2, 0), (-1, 0), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6.5),
        ('TOPPADDING', (0, 1), (-1, -1), 0),
        ('TOPPADDING', (0, -1), (-3, -1), -15),
        ('TOPPADDING', (-2, -1), (-1, -1), -8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 0),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('VALIGN', (0, -1), (0, -1), 'BOTTOM'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, -1), (1, -1), -10),
        ('LEFTPADDING', (1, -1), (-1, -1), 51.25),
    ])

    style_right_delivery_info = TableStyle([
        ('BOX', (0, 0), (-1,-1), 0.25, colors.black),
        ('INNERGRID', (0 ,0), (-1, -1), 0.25, colors.black),
        ('FONT', (0, 0), (-1, -2), CHINESE_FONT_BOLD),
        ('FONT', (0, 1), (-1, -1), CHINESE_FONT),
        ('FONTSIZE', (0, 0), (-1, -2), 7),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 0.5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0.5),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
    ])

    style_right_order = TableStyle([
        ('BOX', (0, 0), (-1,-3), 0.25, colors.black),
        ('INNERGRID', (0 ,0), (-1, -3), 0.25, colors.black),
        ('FONT', (0, 0), (0, -1), CHINESE_FONT_BOLD),
        ('FONT', (1, 0), (-1, -1), CHINESE_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ])
    
    style_signature_box = TableStyle([
        ('BOX', (0, 0), (-1,-1), 0.25, colors.black),
        ('INNERGRID', (0 ,0), (-1, -1), 0.25, colors.black),
        ('FONT', (1, 0), (-1, -1), CHINESE_FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 6),
        ('FONTSIZE', (2, 0), (-1, -1), 3),
        ('FONTSIZE', (1, 0), (1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ])

    page_data = [
        [table_custom(data=[ [obtnumber_barcode], 
                             [f'包裹查詢號碼 : {obtnumber}'], 
                             [table_custom(data=[ ['收貨日','希望配達日','希望配達時段','發貨所'],
                                                  [data.get('date_shipping'),data.get('date_delivery'),f'{data.get('time_delivery_start')}~{data.get('time_delivery_start')}','中和二所'] ],
                                           width=[16*mm, 18*mm, 20*mm, 15*mm], height=None, style=style_left_4_grid)], 
                             [table_custom(data=[ [Paragraph('收件人', style_normal), table_custom(data=[ [data.get('address')], 
                                                                                                         [data.get('recipient')],
                                                                                                         [data.get('mobile')] ], 
                                                                                                  width=[ 63*mm ], height=None, style=style_left_recipient_grid)] ], 
                                           width=[ 6*mm, 63*mm ], height=None, style=style_left_address_grid)], 
                             [table_custom(data=[ [Paragraph('寄件人', style_normal), table_custom(data=[ [data.get('fulfillment.address')], 
                                                                                                         [data.get('company')],
                                                                                                         [data.get('fulfillment.phone')] ], 
                                                                                                  width=[ 63*mm ], height=None, style=style_left_sender_grid)] ], 
                                           width=[ 6*mm, 63*mm ], height=None, style=style_left_address_grid)], 
                             [table_custom(data=[ ['品名' , '代收貨款'], 
                                                  ['0015-其他', '不收款'] ], 
                                           width=[34*mm, 35*mm], height=None, style=style_left_2_grid)], 
                             [table_custom(data=[ [ '訂單編號 : ', data.get('sub')] ], width=[20*mm, 49*mm], height=None, style=style_left_sub)]  ],                                                                              
                      width=[ 70*mm ], height=None, style=style_left), 
         
         table_custom(data=[ [postnumber_barcode, postnumber, table_custom(data=[ ['希望配達日'], 
                                                                                  [data.get('date_shipping')] ], width=[20*mm], height=None, style=style_right_delivery_info)],
                             
                             [table_custom(data=[ [Paragraph('收件人', style_normal), table_custom(data=[ [data.get('address')], 
                                                                                                         [data.get('recipient')],
                                                                                                         [data.get('mobile')] ], 
                                                                                                  width=[ 93*mm ], height=None, style=style_left_recipient_grid) ] ], 
                                           width=[ 6*mm, 94*mm ], height=None, style=style_left_address_grid), '', table_custom(data=[ ['希望配達時段'],
                                                                                                                                       [f'{data.get('time_delivery_start')}~{data.get('time_delivery_start')}'] ], width=[20*mm], height=None, style=style_right_delivery_info)], 
                             [table_custom(data=[ [Paragraph('寄件人', style_normal), table_custom(data=[ [data.get('fulfillment.address')], 
                                                                                                         [data.get('company')],
                                                                                                         [data.get('fulfillment.phone')] ], 
                                                                                                  width=[ 93*mm ], height=None, style=style_left_sender_grid) ] ], 
                                           width=[ 6*mm, 94*mm ], height=None, style=style_left_address_grid), '', table_custom(data=[ ['尺寸'],
                                                                                                                                       ['90 cm 常溫'] ], width=[20*mm], height=None, style=style_right_delivery_info)], 
                             
                             [table_custom(data=[ ['備註', ''], 
                                                  ['品名', '0015-其他'],
                                                  ['訂單編號', data.get('sub')], 
                                                  ['客戶', data.get('customer_id')],
                                                  ['單號', obtnumber] ], width=[15*mm, 85*mm], height=None, style=style_right_order), '', table_custom(data=[ [tcat_qr] ], width=[20*mm], height=None, style=style_right_delivery_info)],
                             [obtnumber_barcode_big, table_custom(data=[[ Paragraph('代收貨款', style_normal), '不收款',  Paragraph('收件人簽名', style_normal), '']], width=[7*mm, 20*mm, 7*mm, 20*mm], height=15.5*mm, style=style_signature_box)] ], width=[50*mm, 50*mm, 20*mm], height=None, style=style_right_barcode), ''],
        
    ]
    
    page_layout = Table(page_data, rowHeights=70*mm, splitByRow=5)

    page_layout.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, 0), -15),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
    return page_layout

def create_shipping_label_code39(output_path, data):

    """
    Create a shipping label using Code39 barcodes
    Same as before but using Code39 instead of Code128
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=5*mm,
        bottomMargin=5*mm,
        leftMargin=5*mm,
        rightMargin=20*mm
    )

    story = []
    page_data = [
        [create_label(data)],
        [create_sticker(data)],
        [create_label(data)],
        [create_sticker(data)],
        ]

    page_layout = Table(page_data, rowHeights=70*mm, splitByRow=5)
    page_layout.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, 1), 'TOP'),
        ('VALIGN', (0, -1), (-1, -1), 'BOTTOM'),
    ]))
    story.append(page_layout)

    doc.build(story)
    print(f"Shipping label with Code39 created: {output_path}")

if __name__ == "__main__":
    # Create shipping label with Code39
    sample_data = {
        'obtnumber': '907572734046',  # Code39 compatible value
        'date_shipping': '2026-02-01',
        'date_delivery': '2026-02-03',
        'time_delivery_start': '14:00',
        'time_delivery_end': '16:00',
        'postnumber': '83-820-02-B',  # Code39 compatible value
        'sub': 'O25003669002',
        'customer': '林安琪(黃鼎喻/王奕雯)',
        'transport':'黑貓宅急便',
        'thermo':'常溫',
        'comment':'請安排2/2-2/3出貨，出貨後約1-3 個工作日到貨 婚期2026/1/31 出貨前，請先拍照給玟妤確認，謝謝',
        'customer_no': '0032368',
        'customer_id': '428609240200',
        'address': '116台北市文山區羅斯福路五段273號2樓',
        'recipient': '林月霜',
        'mobile': '0933039896',
        'fulfillment.address': '235450新北市中和區中正路1215號2樓',
        'company': '巧櫻有限公司',
        'fulfillment.phone':'0233652252'
    }

    create_shipping_label_code39('shipping_label_code39_TEST.pdf', sample_data)