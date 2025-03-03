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
			  WellToWellDistance, 
			  WellDepth, 
			  WellXOffset, 
			  WellYOffset,  
			  Rows, 
			  Columns,
			  WellZOffset=0.29,
			  PlateLength=127.76, 
			  PlateWidth=85.48,  
			  OpenSCADPath=None, 
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
			PlateHeight (float): Height of the plate
			WellDiameter (float): Diameter of the wells
			WellToWellDistance (float): Spacing between the wells
			WellDepth (float): Depth of the wells
			WellXOffset (float): Offset of the centre of the first well away from the short edge of the plate
			WellYOffset (float): Offset of the centre of the first well away from the long edge of the plate
			Rows (int): Number of rows of wells
			Columns (int): Number of columns of wells
			WellZOffset (float, optional): Offset of the bottom of the wells away from the bottom of the plate. Only needed for example plate generation Defaults to 0.29.
			PlateLength (float, optional): Length of the plate. Defaults to 127.76.
			PlateWidth (float, optional): Width of the plate. Defaults to 85.48.
			OpenSCADPath (str, optional):  Path to OpenSCAD executable (used for exporting and rendering).. Defaults to None.
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
		self.WellXOffset = WellXOffset
		self.WellYOffset = WellYOffset
		self.WellZOffset = WellZOffset
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
		self.OpenSCADPath = OpenSCADPath
		self.Plate = None
		self.PlateStamp = None
		self.PlateMould = None
		self.Frame = None
		self.Cutter = None

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
				Plate -= sutils.translate([self.WellToWellDistance*column, self.WellToWellDistance*row, 0])(Well)
		self.Plate = Plate
	
	def generate_stamp(self):
		"Generates a plate Stamp with columns matching the wells of the plate"
		Base = solid.cube([self.PlateLength + (self.BrimExtension * 2), 
					 	   self.PlateWidth + (self.BrimExtension * 2), 
						   self.StampBaseHeight])
		# Creates the wells for the Stamp
		# Diameter is contracted by the modifier to create a gap between the Stamp and the well
		# Height is increased by the modifier to create a deeper well
		WellStamp = solid.cylinder(d=self.WellDiameter * (1.0 - self.StampWellModifier), 
							  		h=self.PlateHeight * (1.0 + self.StampDepthExtension), 
									segments=self.CylinderSegments
									)
		# Rotates the well by 45 degrees in case it is a square to ensure it is in the correct orientation
		WellStamp = solid.rotate(45)(WellStamp)
		# Moves the well to the correct initial position
		WellStamp = sutils.translate([self.WellXOffset + self.BrimExtension, self.WellYOffset + self.BrimExtension, self.StampBaseHeight])(WellStamp)
		# Distributes the wells across the Stamp
		for row in range(self.Rows):
			for column in range(self.Columns):
				Base += sutils.translate([self.WellToWellDistance*column, self.WellToWellDistance*row, 0])(WellStamp)
		self.PlateStamp = Base

	def generate_mould(self):
		"Generates a mould that sits on the frame. This will be used to create the agarose mould"
		# Generates the initial mould and frame cuboids
		Mould = solid.cube([self.PlateLength, self.PlateWidth, self.MouldThickness])
		# Creates the wells for the mould
		# Diameter is expanded by the same modifier as the Stamp and then adjusted again by the mould modifier
		WellMould = solid.cylinder(d=(self.WellDiameter * (1.0 + self.StampWellModifier)) * (1.0 + self.MouldWellModifier), 
							  h=self.MouldThickness, 
							  segments=self.CylinderSegments
							  )
		# Rotates the well by 45 degrees in case it is a square to ensure it is in the correct orientation
		WellMould = solid.rotate(45)(WellMould)
		# Moves the well to the correct initial position
		WellMould = sutils.translate([self.WellXOffset, 
								 self.WellYOffset,
								 0]
								 )(WellMould)
		# Distributes the wells across the mould
		for row in range(self.Rows):
			for column in range(self.Columns):
				Mould -= sutils.translate([self.WellToWellDistance*column, self.WellToWellDistance*row, 0])(WellMould)
		self.PlateMould = Mould

	# Get mesh functions
	def getPlate(self):
		if self.Plate is None:
			self.generate_plate()
		return self.Plate
	
	def getStamp(self):
		if self.PlateStamp is None:
			self.generate_stamp()
		return self.PlateStamp

	def getMould(self):
		if self.PlateMould is None:
			self.generate_mould()
		return self.PlateMould

	# Render functions
	def render_plate(self, Renderer=None):
		if self.Plate is None:
			self.generate_plate()
		if Renderer is None:
			if self.OpenSCADPath is None:
				raise AttributeError("OpenSCADPath is not set/Renderer is not provided")
			Renderer = viewscad.Renderer(openscad_exec=self.OpenSCADPath, grid_lines_width=5, draw_grids=True)
		Renderer.render(self.Plate)

	def render_stamp(self, Renderer=None):
		if self.PlateStamp is None:
			self.generate_stamp()
		if Renderer is None:
			if self.OpenSCADPath is None:
				raise AttributeError("OpenSCADPath is not set/Renderer is not provided")
			Renderer = viewscad.Renderer(openscad_exec=self.OpenSCADPath, grid_lines_width=5, draw_grids=True)
		Renderer.render(self.PlateStamp)
	
	def render_mould(self, Renderer=None):
		if self.PlateMould is None:
			self.generate_mould()
		if Renderer is None:
			if self.OpenSCADPath is None:
				raise AttributeError("OpenSCADPath is not set/Renderer is not provided")
			Renderer = viewscad.Renderer(openscad_exec=self.OpenSCADPath, grid_lines_width=5, draw_grids=True)
		Renderer.render(self.PlateMould)

	# Export functions
	def export_plate(self, filepath, stl=False, OpenSCADPath=None):
		if OpenSCADPath is None:
			if self.OpenSCADPath is None:
				raise AttributeError("OpenSCADPath is not set")
			OpenSCADPath = self.OpenSCADPath
		if self.Plate is None:
			self.generate_plate()
		export(self.Plate, self.OpenSCADPath, filepath, stl)

	def export_stamp(self, filepath, stl=False, OpenSCADPath=None):
		if OpenSCADPath is None:
			if self.OpenSCADPath is None:
				raise AttributeError("OpenSCADPath is not set")
			OpenSCADPath = self.OpenSCADPath
		if self.PlateStamp is None:
			self.generate_stamp()
		export(self.PlateStamp, self.OpenSCADPath, filepath, stl)

	def export_mould(self, filepath, stl=False, OpenSCADPath=None):
		if OpenSCADPath is None:
			if self.OpenSCADPath is None:
				raise AttributeError("OpenSCADPath is not set")
			OpenSCADPath = self.OpenSCADPath
		if self.PlateMould is None:
			self.generate_mould()
		export(self.PlateMould, self.OpenSCADPath, filepath, stl)