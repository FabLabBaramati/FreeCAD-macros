"""
HoneycombSolid --> Honeycomb solid creator.
(c) 2021 Christian González Di Antonio <christiangda@gmail.com>
"""

import math

import FreeCAD as app

import Part


class HoneycombSolid:

    def __init__(self, obj, version):
        # Custom properties of Honeycomb feature.
        obj.addProperty('App::PropertyLength', 'Length', 'Honeycomb', 'Length of the Honeycomb').Length=100.0
        obj.addProperty('App::PropertyLength', 'Width', 'Honeycomb', 'Width of the Honeycomb').Width=100.0
        obj.addProperty('App::PropertyLength', 'Height', 'Honeycomb', 'Height of the Honeycomb').Height=2.0
        obj.addProperty('App::PropertyLength', 'Circumradius', 'Polygon', 'Radius of the inner circle').Circumradius=5.0
        obj.addProperty('App::PropertyLength', 'Thickness', 'Walls', 'Thickness of the honeycomb walls').Thickness=1.0
        obj.Proxy = self

        self.Type = 'HoneycombSolid'
        self.Version = version

    def onChanged(self, fp, prop):
        """Callback on changed property."""
        # app.Console.PrintMessage("Change property: " + str(prop) + "\n")
        pass

    def execute(self, fp):
        """Callback when doing a recomputation."""
        length = fp.Length
        width = fp.Width
        height = fp.Height
        radius = fp.Circumradius
        thickness = fp.Thickness

        edges = 6

        # Container box, used to cut the polygon array.
        container = Part.makeBox(length, width, height)

        ###############################################################
        # Create the first polygon.
        m = app.Matrix()
        edges_angle = math.radians(360.0 / edges)
        m.rotateZ(edges_angle)
        v = app.Vector(radius, 0.0, 0.0)

        figure = []
        for _ in range(edges):
            figure.append(v)
            v = m.multiply(v)
        figure.append(v)
        polygon = Part.makePolygon(figure)

        # Move it to the center of the container box.
        polygon.translate(app.Vector(length / 2.0, width / 2.0, 0.0))

        # Create a face for the first polygon.
        f1 = Part.Face([polygon])

        #######################################################################
        # Create copies of polygon using radial pattern.

        # Calculate how many circunferences need to cover the maximum
        # length of the container box.
        n_cols = math.ceil((length / (radius + thickness) / 2.0))
        n_rows = math.ceil((width / (radius + thickness) / 2.0) + 3.0)
        # app.Console.PrintMessage("n_cols: " + str(n_cols) + " n_rows: " + str(n_rows) + "\n")

        # To store all the polygon faces.
        e_faces = []
        # Add the first one created before.
        e_faces.append(f1)

        # Iterate over each imaginary circle which circunference contains the
        # center of the polygon circle.
        def append_face(x_delta, y_delta):
            x_origin = column * x_delta
            y_origin = row * y_delta

            delta_x_y = app.Vector(x_origin, y_origin, 0.0)

            polygon_copy = polygon.copy()
            polygon_copy.translate(delta_x_y)
            fn = Part.Face([polygon_copy])
            e_faces.append(fn)

        for column in range(-n_cols, n_cols):
            for row in range(-n_rows, n_rows):
                centers_distance = thickness + 2.0 * radius * math.sin(edges_angle)
                x_delta = centers_distance * math.sin(edges_angle)
                if (column == 0) and (row == 0):
                    continue
                if column % 2 != 0:
                    # Odd column.
                    if row % 2 != 0:
                        # Odd row.
                        y_delta = centers_distance * math.cos(edges_angle)
                        append_face(x_delta, y_delta)
                else:
                    # Even column.
                    if (row <= (n_rows/2)) and (row >= (-n_rows/2)):
                        y_delta = centers_distance
                        append_face(x_delta, y_delta)

        # Join all the faces.
        shell = Part.makeShell(e_faces)
        extruded_polygon = shell.extrude(app.Vector(0.0, 0.0, height))

        # Cut the array of solids using the container box.
        # Comment it out to see the array of solids.
        shape = container.cut(extruded_polygon)

        fp.Shape = shape  # Comment out to see the array of solids.
        # fp.Shape = extruded_polygon  # Uncomment it to see the array of solids.

    def __getstate__(self):
        """Callback called when saving the document.

        When saving the document this object gets stored using Python's cPickle module.
        Since we have some un-pickable here -- the Coin stuff -- we must define this method
        to return a tuple of all pickable objects or None.

        """
        return self.Type, self.Version

    def __setstate__(self, state):
        """Callback called when the document is restored.

        When restoring the pickled object from document we have the chance to set some
        internals here.

        """
        self.Type = state[0]
        self.Version = state[1]


class ViewProviderHoneycombSolid:
    def __init__(self, obj):
        """Set this object to the proxy object of the actual view provider."""
        obj.Proxy = self

    def attach(self, obj):
        """Setup the scene sub-graph of the view provider."""
        return

    def updateData(self, fp, prop):
        """Handle changes of a property."""
        return

    def getDisplayModes(self, obj):
        """Return a list of display modes."""
        modes = []
        return modes

    def getDefaultDisplayMode(self):
        """Return the name of the default display mode.

        It must be defined in getDisplayModes.

        """
        return 'Shaded'

    def setDisplayMode(self, mode):
        """Map the display mode with those defined in getDisplayModes.

        Map the display mode defined in `attach()` with those defined in
        getDisplayModes.

        Since they have the same names nothing needs to be done. This method is
        optional.

        """
        return mode

    def onChanged(self, vp, prop):
        """Print the name of the property that has changed."""
        # app.Console.PrintMessage("Change property: " + str(prop) + "\n")
        pass

    def getIcon(self):
        """Return the icon in XMP format which will appear in the tree view.

        This method is optional and if not defined a default icon is shown.

        """
        return """
            /* XPM */
            static const char * ViewProviderHoneycombSolid_xpm[] = {
            "16 16 54 1",
            " 	c None",
            ".	c #181818",
            "+	c #5F5F5F",
            "@	c #636363",
            "#	c #353535",
            "$	c #474747",
            "%	c #434343",
            "&	c #606060",
            "*	c #424242",
            "=	c #111111",
            "-	c #444444",
            ";	c #151515",
            ">	c #3F3F3F",
            ",	c #1E1E1E",
            "'	c #1C1C1C",
            ")	c #1B1B1B",
            "!	c #2C2C2C",
            "~	c #535353",
            "{	c #0A0A0A",
            "]	c #363636",
            "^	c #383838",
            "/	c #2F2F2F",
            "(	c #252525",
            "_	c #555555",
            ":	c #393939",
            "<	c #515151",
            "[	c #262626",
            "}	c #161616",
            "|	c #464646",
            "1	c #4F4F4F",
            "2	c #545454",
            "3	c #3A3A3A",
            "4	c #131313",
            "5	c #121212",
            "6	c #5E5E5E",
            "7	c #0C0C0C",
            "8	c #0F0F0F",
            "9	c #0B0B0B",
            "0	c #0D0D0D",
            "a	c #1D1D1D",
            "b	c #292929",
            "c	c #3D3D3D",
            "d	c #222222",
            "e	c #171717",
            "f	c #1A1A1A",
            "g	c #282828",
            "h	c #272727",
            "i	c #5A5A5A",
            "j	c #3C3C3C",
            "k	c #595959",
            "l	c #616161",
            "m	c #505050",
            "n	c #2E2E2E",
            "o	c #565656",
            "   .+@@   #$    ",
            "    %@&* =-$    ",
            "    ;>,')!~&    ",
            "    {]^  /@@    ",
            "@   ($$   _@@   ",
            "@   :$    /@@   ",
            "<][}|1     2~3['",
            "445#6@     78889",
            "%  '&@@    #$   ",
            "$   $@@   0-$   ",
            "    a&@+  b$$   ",
            "     c*[de>_    ",
            "@    fgh {i@@   ",
            "@    ^$   j@@   ",
            "@@  4|$   {k@@  ",
            "lm ,n$     ]@o^["};
            """

    def __getstate__(self):
        """Callback called when saving the document.

        When saving the document this object gets stored using Python's cPickle module.
        Since we have some un-pickable here -- the Coin stuff -- we must define this method
        to return a tuple of all pickable objects or None.

        """
        return None

    def __setstate__(self,state):
        """Callback called when the document is restored.

        When restoring the pickled object from document we have the chance to set some
        internals here.

        """
        return None


def makeHoneycombSolid(version):
    doc = app.activeDocument()

    if doc is None:
        doc = app.newDocument()

    obj = doc.addObject('Part::FeaturePython', 'HoneycombSolid')
    HoneycombSolid(obj, version)
    ViewProviderHoneycombSolid(obj.ViewObject)
    doc.recompute()
