import os
import re
import solid
import viewscad
import solid.utils as sutils
import subprocess


def export(mesh, openscadpath, filepath, stl=True, scad=False):
	"""Exports the mesh to scad/stl files using openscad

	Args:
		mesh (OpenSCADObject): Mesh to be exported
		openscadpath (str): Path to the openscad executable
		filepath (str): Desired savepath for the file
		stl (bool, optional): Whether to export as an stl. Defaults to True.
		scad (bool, optional): Whether to export as scad. Defaults to False.
	"""

	# Checks the extensions of the given savepath,
	# sets the stl and scad flags accordingly
	# and removes the extension from the savepath
	if re.search(r"\.scad$", filepath, re.IGNORECASE):
		scad = True
		filepath = ".".join(filepath.split(".")[:-1])
	elif re.search(r"\.stl$", filepath, re.IGNORECASE):
		stl = True
		filepath = ".".join(filepath.split(".")[:-1])
	# Exports the mesh to a scad file so it can be accessed by openscad
	solid.scad_render_to_file(mesh, filepath + ".scad")
	# If stl is enabled will render to an stl file using openscad
	if stl:
		# Calls command line to render the scad file to an stl file
		subprocess.run([openscadpath, '-o', filepath + ".stl", filepath + ".scad"])
		#  If scad is not required will remove the scad file
		if scad == False:
			os.remove(filepath + ".scad")

class Plate:
	def __init__(self, 
			  PlateHeight, 
			  WellDiameter, 
			  WellSpacing, 
			  WellDepth, 
			  WellXOffset, 
			  WellYOffset,  
			  Rows, 
			  Columns,
			  WellZOffset=0.29,
			  PlateLength=127.76, 
			  PlateWidth=85.48,  
			  OpenSCADPath=None, 
			  InsertBaseHeight=5.0,
			  FrameSlotModifier=0.05,
			  BrimExtension=0.0,
			  NoBrim=False,
			  InsertDepthModifier=0.05, 
			  InsertWellModifier=0.05, 
			  TopperWellModifier=0.01,
			  TopperSlotModifier=0.05,
			  MouldWellClearance=1,
			  TopperDepth=0.5,
			  TopperBaseThickness=3.0,
			  FrameWallThickness=5.0,
			  CuboidWellSize=None,
			  CylinderSegments=32,
			  CutterBaseThickness=5.0,
			  CutterEdgeThickness=0.5,
			  CutterDiameterModifier=0.05,
			  CutterEdgeLength=2.0,
			  CutterGuideSides=4,
			  CutterGuideLength=8.0,
			  CutterGuideOffset=0.5,
			  CutterGuideModifier=0.025):
		"""This class is used to create tools used to make agarose pads for a multiwell plate of the specified dimensions.

		Args:
			PlateHeight (float): Height of the plate
			WellDiameter (float): Diameter of the wells
			WellSpacing (float): Spacing between the wells
			WellDepth (float): Depth of the wells
			WellXOffset (float): Offset of the centre of the first well away from the short edge of the plate
			WellYOffset (float): Offset of the centre of the first well away from the long edge of the plate
			Rows (int): Number of rows of wells
			Columns (int): Number of columns of wells
			WellZOffset (float, optional): Offset of the bottom of the wells away from the bottom of the plate. Only needed for example plate generation Defaults to 0.29.
			PlateLength (float, optional): Length of the plate. Defaults to 127.76.
			PlateWidth (float, optional): Width of the plate. Defaults to 85.48.
			OpenSCADPath (str, optional):  Path to OpenSCAD executable (used for exporting and rendering).. Defaults to None.
			InsertBaseHeight (float, optional): Height of the base of the plate insert. Defaults to 5.0.
			FrameSlotModifier (float, optional): Percentage modifier to increase the size of the slot for the frame to sit in. Defaults to 0.05.
			BrimExtension (float, optional): Amount to extend the brim that the frame sits on by. Defaults to 0.0.
			NoBrim (bool, optional): Whether to include a brim for the frame to sit on. Defaults to False.
			InsertDepthModifier (float, optional): Percentage modifier to increase well depth for the plate insert. Defaults to 0.05.
			InsertWellModifier (float, optional): Percentage modifier to shrink well size for the plate insert. Defaults to 0.05.
			TopperWellModifier (float, optional): Percentage modifier to increase well size for the topper relative to the insert. Defaults to 0.01.
			TopperSlotModifier (float, optional): Percentage modifier to increase the size of the slot for the topper to sit in. Defaults to 0.05.
			MouldWellClearance (int, optional): How far from the edges of the wells the agarose moould of the topper will extend too. Defaults to 1.
			TopperDepth (float, optional): Depth of the topper mould giving thickness of agarose. Defaults to 0.5.
			TopperBaseThickness (float, optional): Thickness of the base of the topper. Defaults to 3.0.
			FrameWallThickness (float, optional): Thickness of the frame holding up the topper. Defaults to 5.0.
			CuboidWellSize (float, optional): Size of the wells if they are cuboid. If not set will be cylinders. Defaults to None.
			CylinderSegments (int, optional): Number of segments the cylinders are rendered with. Higher number greatly reduces performance. Defaults to 32.
			CutterBaseThickness (float, optional): Thickness of the base of the cutter. Defaults to 5.0.
			CutterEdgeThickness (float, optional): Thickness of the cutting edges of the cutter. Defaults to 0.5.
			CutterDiameterModifier (float, optional): Percentage modifier to decrease the size of the cutter wells relative to the topper wells. Defaults to 0.05.
			CutterEdgeLength (float, optional): Length of the cutting edges of the cutter. Defaults to 2.0.
			CutterGuideSides (int, optional): Length of the X/Y sides of the guide used in the cutter. Defaults to 4.
			CutterGuideLength (float, optional): Length the cutter guide extends. Defaults to 8.0.
			CutterGuideOffset (float, optional): How far from the edges of the frame wall the guide for the cutter is placed. Defaults to 0.5.
			CutterGuideModifier (float, optional): Percentage modifier to reduce size of the cutter guide so it fits in the holes. Defaults to 0.05.
		"""

		self.PlateLength = PlateLength
		self.PlateWidth = PlateWidth
		self.PlateHeight = PlateHeight
		self.WellDiameter = WellDiameter
		self.WellSpacing = WellSpacing
		self.WellDepth = WellDepth
		self.WellXOffset = WellXOffset
		self.WellYOffset = WellYOffset
		self.WellZOffset = WellZOffset
		self.Rows = Rows
		self.Columns = Columns
		self.InsertBaseHeight = InsertBaseHeight
		self.FrameSlotModifier = FrameSlotModifier
		self.InsertDepthModifier = InsertDepthModifier
		self.InsertWellModifier = InsertWellModifier
		self.TopperWellModifier = TopperWellModifier
		self.TopperSlotModifier = TopperSlotModifier
		self.MouldWellClearance = MouldWellClearance
		self.TopperDepth = TopperDepth
		self.TopperBaseThickness = TopperBaseThickness
		self.FrameWallThickness = FrameWallThickness
		self.CylinderSegments = CylinderSegments
		self.CutterBaseThickness = CutterBaseThickness
		self.CutterEdgeThickness = CutterEdgeThickness
		self.CutterDiameterModifier = CutterDiameterModifier
		self.CutterEdgeLength = CutterEdgeLength
		self.CutterGuideSides = CutterGuideSides
		self.CutterGuideLength = CutterGuideLength
		self.CutterGuideOffset = CutterGuideOffset
		self.CutterGuideModifier = CutterGuideModifier

		self.check_parameters()

		self.BrimExtension = BrimExtension
		self.NoBrim = NoBrim
		self.CuboidWellSize = CuboidWellSize
		self.OpenSCADPath = OpenSCADPath
		self.Plate = None
		self.PlateInsert = None
		self.PlateTopper = None
		self.Frame = None
		self.Cutter = None

		if self.CuboidWellSize:
			self.CylinderSegments = 4
			self.WellDiameter = self.CuboidWellSize

	def check_parameters(self):
		excluded = ["InsertDepthModifier", 
			  		"InsertWellModifier", 
					"TopperWellModifier", 
					"MouldWellClearance", 
					"FrameSlotModifier",
					"CuttingEdgeModifier", 
					"CutterGuideModifier"]
		for key, value in self.__dict__.items():
			if key in excluded:
				continue
			if value is None:
				raise AttributeError(f"{key} is not set")
			if value <= 0:
				raise ValueError(f"{key} must be greater than 0")
		MaxFrameWalls = min(self.WellXOffset, self.WellYOffset) - (self.WellDiameter/2)
		if self.FrameWallThickness >= MaxFrameWalls:
			raise ValueError(f"FrameWallThickness must be less than {MaxFrameWalls} (the distance between the wells and the edge of the plate)")
		MaxCutterGuideOffset = ((((max(self.WellXOffset, self.WellYOffset) 
						   		- (self.WellDiameter/2))
								- self.MouldWellClearance)
								- self.CutterGuideSides)
								- self.FrameWallThickness
								)
		MaxWellClearance = self.MouldWellClearance - MaxCutterGuideOffset
		if self.CutterGuideOffset >= MaxCutterGuideOffset:
			raise ValueError(f"Either CutterGuideOffset must be less than {MaxCutterGuideOffset}" 
					+ f" or MouldWellClearance must be less than {MaxWellClearance} in order to not overlap")
		
	# Mesh generation functions
	def generate_plate(self):
		"Generates an example plate"
		Plate = solid.cube([self.PlateLength, self.PlateWidth, self.PlateHeight])
		Well = solid.cylinder(d=self.WellDiameter, h=self.WellDepth, segments=self.CylinderSegments)
		# Rotates the well by 45 degrees in case it is a square to ensure it is in the correct orientation
		Well = solid.rotate(45)(Well)
		# Moves the well to the correct initial position
		Well = sutils.translate([self.WellXOffset, self.WellYOffset, self.WellZOffset])(Well)
		# Distributes the wells across the plate
		for row in range(self.Rows):
			for column in range(self.Columns):
				Plate -= sutils.translate([self.WellSpacing*column, self.WellSpacing*row, 0])(Well)
		self.Plate = Plate
	
	def generate_insert(self):
		"Generates a plate insert with columns matching the wells of the plate"
		Base = solid.cube([self.PlateLength + (self.BrimExtension * 2), 
					 	   self.PlateWidth + (self.BrimExtension * 2), 
						   self.InsertBaseHeight])
		# Creates a the walls of the insert used for the insert frame to create a slot for them to sit in
		# The height is half the depth of the insert base to represent the offset
		Walls = solid.cube([self.PlateLength + (self.BrimExtension * 2), 
					  		self.PlateWidth + (self.BrimExtension * 2), 
							self.InsertBaseHeight])
		# Adjusts the wall thickness by the modifier to create a slot for the frame to sit in
		ModifiedFrameWallThickness = self.FrameWallThickness * (1.0 + self.FrameSlotModifier)
		# Creates the hole in the walls leaving only the frame
		# Need to subtract double the wall thickness for the two sides
		WallsHole = solid.cube([self.PlateLength - (ModifiedFrameWallThickness * 2), 
						  		self.PlateWidth - (ModifiedFrameWallThickness * 2),
						  		self.InsertBaseHeight]
								)
		
		Walls -= sutils.translate([ModifiedFrameWallThickness + self.BrimExtension,
							 	   ModifiedFrameWallThickness + self.BrimExtension, 
								   0]
								   )(WallsHole)
		# If a brim is wanted then the walls are translated by half the thickness of the base
		if self.NoBrim == False:
			Walls = sutils.translate([0, 0, self.InsertBaseHeight/2])(Walls)
		# Subtracts the frame inset from the insert
		Base -=  Walls 
		# Creates the wells for the insert
		# Diameter is contracted by the modifier to create a gap between the insert and the well
		# Height is increased by the modifier to create a deeper well
		WellInsert = solid.cylinder(d=self.WellDiameter * (1.0 - self.InsertWellModifier), 
							  		h=self.PlateHeight * (1.0 + self.InsertDepthModifier), 
									segments=self.CylinderSegments
									)
		# Rotates the well by 45 degrees in case it is a square to ensure it is in the correct orientation
		WellInsert = solid.rotate(45)(WellInsert)
		# Moves the well to the correct initial position
		WellInsert = sutils.translate([self.WellXOffset + self.BrimExtension, self.WellYOffset + self.BrimExtension, self.InsertBaseHeight])(WellInsert)
		# Distributes the wells across the insert
		for row in range(self.Rows):
			for column in range(self.Columns):
				Base += sutils.translate([self.WellSpacing*column, self.WellSpacing*row, 0])(WellInsert)
		self.PlateInsert = Base

	def generate_frame(self):
		"Generates a frame that sits on the insert to hold the topper in place"
		# Modifying the gap between the topper and the frame to create a slot for the topper to sit in
		GapMod = self.FrameWallThickness * (1.0 - self.TopperSlotModifier)
		# Need to reduce plate length and width by the wall thickness to create the frame
		# Only sub by 1x the thickness as will be half overlapping with the frame
		TopperLength = self.PlateLength - GapMod
		TopperWidth = self.PlateWidth - GapMod
		# Generates the initial topper and frame cuboids
		TopperHole = solid.cube([TopperLength, TopperWidth, self.TopperBaseThickness], center=True)
		# Height includes the height of the insert - half the depth of the insert base and the topper depth
		# This is used for the frame of the topper
		FrameHeight = (self.PlateHeight * (1.0 + self.InsertDepthModifier)) + (self.InsertBaseHeight/2) + self.TopperDepth
		# If a brim is not included need to increase height to make it still level with the insert
		if self.NoBrim == True:
			FrameHeight += self.InsertBaseHeight/2
		Frame = solid.cube([self.PlateLength, self.PlateWidth, FrameHeight], center=True)
		# Creates the hole in the frame leaving only the walls
		# Need to subtract double the wall thickness for the two sides
		FrameHole = solid.cube([self.PlateLength - (self.FrameWallThickness * 2), 
						  		self.PlateWidth - (self.FrameWallThickness * 2), 
								FrameHeight],
								center=True
								)
		Frame -= FrameHole
		# Subtracts the topper from the top of the frame to create an inset for it
		# Move up half the FrameHeight as was centered
		Frame -= sutils.translate([0, 0, (FrameHeight - self.TopperBaseThickness)/2])(TopperHole)
		self.Frame = Frame

	def generate_topper(self):
		"Generates a topper that sits on the frame. This will be used to create the agarose mould"
		# Need to reduce plate length and width by the wall thickness to create the frame
		# Only sub by 1x the thickness as will be half overlapping with the frame
		TopperLength = self.PlateLength - self.FrameWallThickness
		TopperWidth = self.PlateWidth - self.FrameWallThickness
		# Generates the initial topper and frame cuboids
		Topper = solid.cube([TopperLength, TopperWidth, self.TopperBaseThickness])
		# Creates the mould for the agarose to sit in for the topper
		# Need to adjust the X/Y offsets by the well radius and the inputted clearance
		# Then multiply by 2 as this is being used for the sides of the shape so occurs on both sides
		XMouldOffset = (self.WellXOffset - (self.WellDiameter/2 + self.MouldWellClearance)) * 2
		YMouldOffset = (self.WellYOffset - (self.WellDiameter/2 + self.MouldWellClearance)) * 2
		# Creates the mould for the agarose to sit in for the topper
		Mould = solid.cube([self.PlateLength - XMouldOffset, self.PlateWidth - YMouldOffset, self.TopperDepth])
		# Subtracts the mould from the topper
		# Need to move by half the offset (as this is not counting both sides) 
		# and half the thickness of the frame walls as these will be where the topper is overlapping
		# Z is adjusted up by the base thickness of the topper minus the depth of the agarose mould
		Topper -= sutils.translate([(XMouldOffset/2) - (self.FrameWallThickness/2), 
							  (YMouldOffset/2) - (self.FrameWallThickness/2), 
							  self.TopperBaseThickness - self.TopperDepth]
							  )(Mould)
		# Creates the wells for the topper
		# Diameter is expanded by the same modifier as the insert and then adjusted again by the topper modifier
		WellTopper = solid.cylinder(d=(self.WellDiameter * (1.0 + self.InsertWellModifier)) * (1.0 + self.TopperWellModifier), 
							  h=self.TopperBaseThickness, 
							  segments=self.CylinderSegments
							  )
		# Rotates the well by 45 degrees in case it is a square to ensure it is in the correct orientation
		WellTopper = solid.rotate(45)(WellTopper)
		# Moves the well to the correct initial position
		WellTopper = sutils.translate([self.WellXOffset - self.FrameWallThickness/2, 
								 self.WellYOffset - self.FrameWallThickness/2, 
								 0]
								 )(WellTopper)
		# Distributes the wells across the topper
		for row in range(self.Rows):
			for column in range(self.Columns):
				Topper -= sutils.translate([self.WellSpacing*column, self.WellSpacing*row, 0])(WellTopper)
		
		# Generates a cuboid to serve as a hole for the cutters guide
		GuideHole = solid.cube([self.CutterGuideSides, self.CutterGuideSides, self.TopperBaseThickness])
		# Adjusts the offset to account for the frame walls	
		AdjustedOffset = self.CutterGuideOffset + (self.FrameWallThickness/2)
		# Need a different offset on the far sides as will need to also account
		# for the thickness of the guide cube
		NoCubeOffset = AdjustedOffset + self.CutterGuideSides
		# Creates the 4 guide holes in the corners of the topper
		# First Corner (X1 Y1)
		Topper -= sutils.translate([AdjustedOffset, AdjustedOffset, 0])(GuideHole)
		# Second Corner (X2, Y1)
		Topper -= sutils.translate([TopperLength - NoCubeOffset, AdjustedOffset, 0])(GuideHole)
		# Third Corner (X1, Y2)
		Topper -= sutils.translate([AdjustedOffset, TopperWidth - NoCubeOffset, 0])(GuideHole)
		# Fourth Corner (X2, Y2)
		Topper -= sutils.translate([TopperLength - NoCubeOffset, TopperWidth - NoCubeOffset, 0])(GuideHole)
		self.PlateTopper = Topper

	def generate_cutter(self):
		"Generates a tool to cut around the wells so excess agarose is not pulling off the agarose on the columns"
		# Generates the base of the cutter
		Cutter = solid.cube([self.PlateLength, self.PlateWidth, self.CutterBaseThickness])
		# Sets the diameter of the well to be the same as the insert pillars with a modifier
		WellDiameter = (self.WellDiameter * (1.0 + self.InsertWellModifier)) * (1.0 - self.CutterDiameterModifier)
		# Inner well is the same size as the topper wells. 
		# Needs to be centered so can subtract from the outer well
		InnerWell = solid.cylinder(d=WellDiameter, 
							 h=self.CutterEdgeLength, 
							 segments=self.CylinderSegments, 
							 center=True
							 )
		# Outer well is increased by the size of the cutting edge x2 (for both sides) 
		# Also needs to be centered
		OuterWell = solid.cylinder(d=(WellDiameter + (self.CutterEdgeThickness * 2)), 
							 h=self.CutterEdgeLength, 
							 segments=self.CylinderSegments, 
							 center=True
							 )
		# Subtracts the inner well from the outer well to create a "pipe" to serve as cutting edge
		OuterWell -= InnerWell
		# Rotates the well by 45 degrees in case it is a square to ensure it is in the correct orientation
		OuterWell = solid.rotate(45)(OuterWell)
		# Moves the well to the correct initial position
		# Need to move up in Z addtionally by half the cutting edge length as it was centered
		OuterWell = sutils.translate([self.WellXOffset, 
									self.WellYOffset, 
									self.CutterBaseThickness + (self.CutterEdgeLength/2)]
									)(OuterWell)
		# Distributes the wells across the cutter
		for row in range(self.Rows):
			for column in range(self.Columns):
				Cutter += sutils.translate([self.WellSpacing*column, self.WellSpacing*row, 0])(OuterWell)
		# Adjusts the size of the guide to fit in the holes
		AdjustedSideSize = self.CutterGuideSides * (1.0 - self.CutterGuideModifier)
		DifferenceFromHole = (self.CutterGuideSides - AdjustedSideSize)
		# Generates a cuboid to serve as a guide for the cutter
		Guide = solid.cube([AdjustedSideSize, AdjustedSideSize, self.CutterGuideLength])
		# Adjusts the offset to account for the frame walls and the smaller guide size relative to the hole
		AdjustedOffset = self.CutterGuideOffset + self.FrameWallThickness + (DifferenceFromHole/2)
		# Need a different offset on the far sides as will need to also account
		# for the thickness of the guide cube
		NoCubeOffset = AdjustedOffset + AdjustedSideSize
		# Creates the 4 guide holes in the corners of the cutter
		# First Corner (X1 Y1)
		Cutter += sutils.translate([AdjustedOffset, AdjustedOffset, self.CutterBaseThickness])(Guide)
		# Second Corner (X2, Y1)
		Cutter += sutils.translate([self.PlateLength - NoCubeOffset, AdjustedOffset, self.CutterBaseThickness])(Guide)
		# Third Corner (X1, Y2)
		Cutter += sutils.translate([AdjustedOffset, self.PlateWidth - NoCubeOffset, self.CutterBaseThickness])(Guide)
		# Fourth Corner (X2, Y2)
		Cutter += sutils.translate([self.PlateLength - NoCubeOffset, self.PlateWidth - NoCubeOffset, self.CutterBaseThickness])(Guide)
		self.Cutter = Cutter

	# Get mesh functions
	def getPlate(self):
		if self.Plate is None:
			self.generate_plate()
		return self.Plate
	
	def getInsert(self):
		if self.PlateInsert is None:
			self.generate_insert()
		return self.PlateInsert

	def getTopper(self):
		if self.PlateTopper is None:
			self.generate_topper()
		return self.PlateTopper
	
	def getFrame(self):
		if self.Frame is None:
			self.generate_frame()
		return self.Frame
	
	def getCutter(self):
		if self.Cutter is None:
			self.generate_cutter()
		return self.Cutter

	# Render functions
	def render_plate(self, Renderer=None):
		if self.Plate is None:
			self.generate_plate()
		if Renderer is None:
			if self.OpenSCADPath is None:
				raise AttributeError("OpenSCADPath is not set/Renderer is not provided")
			Renderer = viewscad.Renderer(openscad_exec=self.OpenSCADPath, grid_lines_width=5, draw_grids=True)
		Renderer.render(self.Plate)

	def render_insert(self, Renderer=None):
		if self.PlateInsert is None:
			self.generate_insert()
		if Renderer is None:
			if self.OpenSCADPath is None:
				raise AttributeError("OpenSCADPath is not set/Renderer is not provided")
			Renderer = viewscad.Renderer(openscad_exec=self.OpenSCADPath, grid_lines_width=5, draw_grids=True)
		Renderer.render(self.PlateInsert)
	
	def render_topper(self, Renderer=None):
		if self.PlateTopper is None:
			self.generate_topper()
		if Renderer is None:
			if self.OpenSCADPath is None:
				raise AttributeError("OpenSCADPath is not set/Renderer is not provided")
			Renderer = viewscad.Renderer(openscad_exec=self.OpenSCADPath, grid_lines_width=5, draw_grids=True)
		Renderer.render(self.PlateTopper)

	def render_frame(self, Renderer=None):
		if self.Frame is None:
			self.generate_frame()
		if Renderer is None:
			if self.OpenSCADPath is None:
				raise AttributeError("OpenSCADPath is not set/Renderer is not provided")
			Renderer = viewscad.Renderer(openscad_exec=self.OpenSCADPath, grid_lines_width=5, draw_grids=True)
		Renderer.render(self.Frame)
	
	def render_cutter(self, Renderer=None):
		if self.Cutter is None:
			self.generate_cutter()
		if Renderer is None:
			if self.OpenSCADPath is None:
				raise AttributeError("OpenSCADPath is not set/Renderer is not provided")
			Renderer = viewscad.Renderer(openscad_exec=self.OpenSCADPath, grid_lines_width=5, draw_grids=True)
		Renderer.render(self.Cutter)

	# Export functions
	def export_plate(self, filepath, stl=False, OpenSCADPath=None):
		if OpenSCADPath is None:
			if self.OpenSCADPath is None:
				raise AttributeError("OpenSCADPath is not set")
			OpenSCADPath = self.OpenSCADPath
		if self.Plate is None:
			self.generate_plate()
		export(self.Plate, self.OpenSCADPath, filepath, stl)

	def export_insert(self, filepath, stl=False, OpenSCADPath=None):
		if OpenSCADPath is None:
			if self.OpenSCADPath is None:
				raise AttributeError("OpenSCADPath is not set")
			OpenSCADPath = self.OpenSCADPath
		if self.PlateInsert is None:
			self.generate_insert()
		export(self.PlateInsert, self.OpenSCADPath, filepath, stl)

	def export_topper(self, filepath, stl=False, OpenSCADPath=None):
		if OpenSCADPath is None:
			if self.OpenSCADPath is None:
				raise AttributeError("OpenSCADPath is not set")
			OpenSCADPath = self.OpenSCADPath
		if self.PlateTopper is None:
			self.generate_topper()
		export(self.PlateTopper, self.OpenSCADPath, filepath, stl)
	
	def export_frame(self, filepath, stl=False, OpenSCADPath=None):
		if OpenSCADPath is None:
			if self.OpenSCADPath is None:
				raise AttributeError("OpenSCADPath is not set")
			OpenSCADPath = self.OpenSCADPath
		if self.Frame is None:
			self.generate_frame()
		export(self.Frame, self.OpenSCADPath, filepath, stl)
	
	def export_cutter(self, filepath, stl=False, OpenSCADPath=None):
		if OpenSCADPath is None:
			if self.OpenSCADPath is None:
				raise AttributeError("OpenSCADPath is not set")
			OpenSCADPath = self.OpenSCADPath
		if self.Cutter is None:
			self.generate_cutter()
		export(self.Cutter, self.OpenSCADPath, filepath, stl)