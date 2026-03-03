from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.units import inch

# Create PDF document
pdf_file = "table_example.pdf"
doc = SimpleDocTemplate(pdf_file, pagesize=letter)

# Sample data for the table
data = [
    ['Product', 'Quantity', 'Price', 'Total'],
    ['Widget A', '10', '$5.00', '$50.00'],
    ['Widget B', '5', '$12.00', '$60.00'],
    ['Widget C', '8', '$7.50', '$60.00'],
    ['Widget D', '15', '$3.00', '$45.00'],
    ['', '', 'Subtotal:', '$215.00']
]

# Create the table
table = Table(data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch])

# Add style to the table
style = TableStyle([
    # Header row styling
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 12),
    
    # Data rows styling
    ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
    ('FONTSIZE', (0, 1), (-1, -1), 10),
    
    # Total row styling
    ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
    ('FONTNAME', (2, -1), (-1, -1), 'Helvetica-Bold'),
    
    # Grid and borders
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ('BOX', (0, 0), (-1, -1), 2, colors.black),
    
    # Alignment adjustments
    ('ALIGN', (0, 1), (0, -1), 'LEFT'),  # Product names left-aligned
    ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),  # Numbers right-aligned
])

table.setStyle(style)

# Build PDF
doc.build([table])

print(f"PDF created successfully: {pdf_file}")