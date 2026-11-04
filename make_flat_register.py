import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Flat Register"

# Headers
headers = ["FLAT NO", "Name", "Sign"]
ws.append(headers)

# Generate flat numbers: 13 floors x 4 flats each
# Floor 1: 101-104, Floor 2: 201-204, ..., Floor 13: 1301-1304
flat_nos = []
for floor in range(1, 14):
    for flat in range(1, 5):
        flat_nos.append(floor * 100 + flat)

# Add rows (Name and Sign left blank)
for f in flat_nos:
    ws.append([f, "", ""])

# Styling
header_font = Font(bold=True, color="FFFFFF", size=12)
header_fill = PatternFill("solid", fgColor="1F4E78")
header_align = Alignment(horizontal="center", vertical="center")
thin = Side(style="thin", color="B0B0B0")
border = Border(left=thin, right=thin, top=thin, bottom=thin)

# Style header row
for col in range(1, len(headers) + 1):
    cell = ws.cell(row=1, column=col)
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = header_align
    cell.border = border

# Style data rows
for row in range(2, ws.max_row + 1):
    for col in range(1, len(headers) + 1):
        cell = ws.cell(row=row, column=col)
        cell.border = border
        cell.alignment = Alignment(horizontal="center", vertical="center")
        if row % 2 == 0:
            cell.fill = PatternFill("solid", fgColor="F2F6FB")

# Column widths
widths = {"A": 12, "B": 30, "C": 20}
for col, w in widths.items():
    ws.column_dimensions[col].width = w

# Freeze header row
ws.freeze_panes = "A2"

# Save
out_path = r"C:\Users\krish\Downloads\GITHUB-UI_Agent\Flat_Register.xlsx"
wb.save(out_path)

print("Saved:", out_path)
print("Total flats:", len(flat_nos))
print("First flats:", flat_nos[:8])
print("Last flats:", flat_nos[-8:])
print("Floors: 1-13, 4 flats each")
