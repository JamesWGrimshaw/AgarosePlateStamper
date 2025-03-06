import drawsvg as dw
import PySide6
import math
import AgarosePlateInsert

def getAngleBetweenPoints(x1, y1, x2, y2):
	Angle = math.atan2(y2 - y1, x2 - x1)
	return Angle

def getLineEndCoords(X, Y, Length, Angle):
	"""Gets the end coordinates of a line from the 
		start coordinates, length and angle of the line

	Args:
		X (float): Starting x coordinate
		Y (float): Starting y coordinate
		Length (float): Length of the line
		Angle (int): Angle of the line

	Returns:
		float: End x coordinate
		float: End y coordinate
	"""	

	# These equations generate the end coordinates and returns them
	End_X = X + Length * math.cos(Angle)
	End_Y = abs(-Y + Length * math.sin(Angle))
	return End_X, End_Y

# Does not work for non 90 degree angles
def generateArrow(x1, y1, x2, y2, Width):
	Arrow = dw.Group()
	Arrow.append(dw.Line(x1, y1, x2, y2, stroke="black"))
	Angle = getAngleBetweenPoints(x1, y1, x2, y2)
	WidthTopStart = getLineEndCoords(x1, y1, Width/2, Angle + math.radians(90))
	WidthBottomStart = getLineEndCoords(x1, y1, Width/2, Angle - math.radians(90))
	Arrow.append(dw.Line(WidthTopStart[0], WidthTopStart[1], WidthBottomStart[0], WidthBottomStart[1], stroke="black"))
	WidthTopEnd = getLineEndCoords(x2, y2, Width/2, Angle + math.radians(90))
	WidthBottomEnd = getLineEndCoords(x2, y2, Width/2, Angle - math.radians(90))
	Arrow.append(dw.Line(WidthTopEnd[0], WidthTopEnd[1], WidthBottomEnd[0], WidthBottomEnd[1], stroke="black"))
	return Arrow

def draw_plate_svg(plate):
	"""Generates a SVG representation of the plate

	Args:
		plate (AgarosePlateInsert.Plate): A plate object defining the plate dimensions
	"""
	
	DrawringDimensions = plate.PlateLength * 1.6
	PlateScheme = dw.Drawing(DrawringDimensions, DrawringDimensions, origin=(0, 0))
	PlateStartX = plate.PlateLength/2
	PlateStartY = plate.PlateLength/5
	PlateEndX = PlateStartX + plate.PlateLength
	PlateEndY = PlateStartY + plate.PlateWidth
	WellXOffset = PlateStartX + plate.WellXOffset
	WellYOffset = PlateStartY + plate.WellYOffset 

	# Generates the plate outline
	PlateScheme.append(dw.Lines(PlateStartX, PlateStartY + plate.WellToWellDistance,
									PlateStartX, PlateStartY + plate.PlateWidth,
									PlateStartX + plate.PlateLength, PlateStartY + plate.PlateWidth,
									PlateStartX + plate.PlateLength, PlateStartY,
									PlateStartX + plate.WellToWellDistance, PlateStartY,
									stroke="black", fill="none", close="true"))
	
	# Adds in the wells
	for row in range(plate.Rows):
		for col in range(plate.Columns):
			PlateScheme.append(dw.Circle(WellXOffset + col * plate.WellToWellDistance, WellYOffset + row * plate.WellToWellDistance, plate.WellDiameter/2, stroke='black', fill='none'))

	ArbUnit = plate.PlateWidth/10
	# Plate Length arrow
	PlateScheme.append((generateArrow(PlateStartX, PlateStartY - ArbUnit, PlateEndX, PlateStartY - ArbUnit, ArbUnit/1.75)))
	PlateScheme.append((dw.Text("Length\n   ", font_size=ArbUnit*0.75, path=dw.Line(PlateStartX, PlateStartY - ArbUnit*1.5, PlateEndX, PlateStartY - ArbUnit*1.5), font_weight="bold", text_anchor="middle")))
	# Plate Width arrow
	PlateScheme.append((generateArrow(PlateStartX - ArbUnit * 5, PlateStartY, PlateStartX - ArbUnit * 5, PlateEndY, ArbUnit/1.75)))
	PlateScheme.append((dw.Text("Width", font_size=ArbUnit*0.75, path=dw.Line(PlateStartX - ArbUnit*5.5, PlateEndY, PlateStartX - ArbUnit*5.5, PlateStartY), font_weight="bold", text_anchor="middle")))


	return PlateScheme
