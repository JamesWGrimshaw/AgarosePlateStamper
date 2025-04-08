import cadquery as cq

class multiwell_plate:
	def __init__(self,
			  PlateLength,
			  PlateWidth, 
			  WellDiameter, 
			  WellToWellDistance, 
			  WellDepth, 
			  Rows, 
			  Columns,
			  PlateHeight=13.4,
			  StampBaseHeight=5.0,
			  BrimExtension=0.0,
			  StampDepthExtension=1,
			  StampWellModifier=0.05, 
			  MouldWellModifier=0.01,
			  MouldThickness=2.0,
			  CuboidWellSize=None,
			  CylinderSegments=32):
		"""This class is used to create tools used to make agarose pads for a multiwell plate of the specified dimensions.

		Args:
			PlateLength (float): Length of the plate.
			PlateWidth (float): Width of the plate.
			WellDiameter (float): Diameter of the wells
			WellToWellDistance (float): Spacing between the wells
			WellDepth (float): Depth of the wells
			Rows (int): Number of rows of wells
			Columns (int): Number of columns of wells
			PlateHeight (float, optional): Height of the plate. Only needed for example plate generation. Defaults to 13.4.
			StampBaseHeight (float, optional): Height of the base of the plate Stamp. Defaults to 5.0.
			BrimExtension (float, optional): Amount to extend the brim that the frame sits on by. Defaults to 0.0.
			StampDepthExtension (float, optional): Amount to extend the Stamp pillars past the thickness of the mould. Defaults to 1.
			StampWellModifier (float, optional): Percentage modifier to shrink well size for the plate Stamp. Defaults to 0.05.
			MouldWellModifier (float, optional): Percentage modifier to increase well size for the mould relative to the Stamp. Defaults to 0.01.
			MouldThickness (float, optional): Thickness of the mould which determines agarose pad thickness. Defaults to 2.0.
			CuboidWellSize (float, optional): Size of the wells if they are cuboid. If not set will be cylinders. Defaults to None.
			CylinderSegments (int, optional): Number of segments the cylinders are rendered with. Higher number greatly reduces performance. Defaults to 32.
		"""

		self.PlateLength = PlateLength
		self.PlateWidth = PlateWidth
		self.PlateHeight = PlateHeight
		self.WellDiameter = WellDiameter
		self.WellToWellDistance = WellToWellDistance
		self.WellDepth = WellDepth
		self.Rows = Rows
		self.Columns = Columns
		self.StampBaseHeight = StampBaseHeight
		self.StampDepthExtension = StampDepthExtension
		self.StampWellModifier = StampWellModifier
		self.MouldWellModifier = MouldWellModifier
		self.MouldThickness = MouldThickness
		self.CylinderSegments = CylinderSegments

		self.check_parameters()

		self.BrimExtension = BrimExtension
		self.CuboidWellSize = CuboidWellSize
		
		# Sets the diameter of the holes in the mould to ensure they are smaller than the total well size
		self.MouldHoleSize = self.WellDiameter * (1.0 - self.MouldWellModifier)
		# Sets the diameter of the pillars in the stamp to ensure they are smaller 
		# than the mould holes so they can slide smoothly through these holes
		self.PillarDiameter = self.MouldHoleSize * (1.0 - self.StampWellModifier)
		# Sets the height of the stamp pillars to be the depth of the wells plus
		# the thickness of the mould plus the depth extension of the stamp
		self.PillarHeight = self.WellDepth + self.MouldThickness + self.StampDepthExtension

		self.generate_plate()
		self.generate_stamp()
		self.generate_mould()

		if self.CuboidWellSize:
			self.CylinderSegments = 4
			self.WellDiameter = self.CuboidWellSize

	def check_parameters(self):
		excluded = ["StampDepthExtension", 
			  		"StampWellModifier", 
					"MouldWellModifier"]
		for key, value in self.__dict__.items():
			if key in excluded:
				continue
			if value is None:
				raise AttributeError(f"{key} is not set")
			if value <= 0:
				raise ValueError(f"{key} must be greater than 0")
		
	# Mesh generation functions
	def generate_plate(self):
		"""Generates an example plate"""

		plate = (cq.Workplane("XY")
		   .box(self.PlateLength, self.PlateWidth, self.PlateHeight)
		   .faces(">Z")
		   .workplane()
		   .rarray(self.WellToWellDistance, self.WellToWellDistance, self.Columns, self.Rows, True)
		   .hole(self.WellDiameter, depth=self.WellDepth)
		)
		
		self.Plate = plate
	
	def generate_mould(self):
		"""Generates a mould that sits on the frame. This will be used to create the agarose mould"""

		mould = (cq.Workplane("XY")
		   .box(self.PlateLength, self.PlateWidth, self.MouldThickness)
		   .faces(">Z")
		   .workplane()
		   .rarray(self.WellToWellDistance, self.WellToWellDistance, self.Columns, self.Rows, True)
		   .hole(self.MouldHoleSize)
		)

		self.Mould = mould

	def generate_stamp(self):
		"""Generates a plate Stamp with columns matching the wells of the plate"""


		
		stamp = (cq.Workplane("XY")
		  .box(self.PlateLength + self.BrimExtension * 2, self.PlateWidth + self.BrimExtension * 2, self.StampBaseHeight)
		  .faces("<Z")
		  .workplane()
		  .rarray(self.WellToWellDistance, self.WellToWellDistance, self.Columns, self.Rows, True)
		  .circle(self.PillarDiameter / 2)
		  .extrude(self.PillarHeight)
		)

		stamp = stamp.mirror("XY")

		self.Stamp = stamp