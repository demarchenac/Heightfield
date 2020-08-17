# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 11:58:01 2020

@author: John Corro
@author: Cristhyan De Marchena
"""

import vtk

warp = vtk.vtkWarpScalar()

def get_program_parameters():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('vti_file', nargs='?', default=None, help='vti file')
    parser.add_argument('texture_file', nargs='?', default=None, help='jpg file')
    args = parser.parse_args()
    
    return args.vti_file, args.texture_file

def generate_slide_bar():
    red_r = 224/255
    red_g = 69/255
    red_b = 85/255
    green_r = 70/255
    green_g = 224/255
    green_b = 105/255
    white = 242/255
    
    #build a slide bar
    slide_bar = vtk.vtkSliderRepresentation2D()
    
    slide_bar.SetMinimumValue(-100.0)
    slide_bar.SetMaximumValue(100.0)
    slide_bar.SetTitleText("Scalar Value")
    
    slide_bar.GetSliderProperty().SetColor(red_r, red_g, red_b)
    slide_bar.GetTitleProperty().SetColor(white, white, white)
    slide_bar.GetLabelProperty().SetColor(red_r, red_g, red_b)
    slide_bar.GetSelectedProperty().SetColor(green_r, green_g, green_b)
    slide_bar.GetTubeProperty().SetColor(white, white, white)
    slide_bar.GetCapProperty().SetColor(red_r, red_g, red_b)
    
    slide_bar.GetPoint1Coordinate().SetCoordinateSystemToDisplay()
    slide_bar.GetPoint1Coordinate().SetValue(30,100)
    
    slide_bar.GetPoint2Coordinate().SetCoordinateSystemToDisplay()
    slide_bar.GetPoint2Coordinate().SetValue(330,100)
    return slide_bar

def custom_callback(obj, event):
    # print("interaction called")
    value = int (obj.GetRepresentation().GetValue())
    global warp
    warp.SetScaleFactor(value)
    warp.Update()

def main():
    # Define stuff
    vti_file, texture_file = get_program_parameters()
    colors = vtk.vtkNamedColors() 
    
    # Read vti file
    reader = vtk.vtkXMLImageDataReader()
    reader.SetFileName(vti_file)
    
    # Load texture
    readerFactory = vtk.vtkImageReader2Factory()
    textureFile = readerFactory.CreateImageReader2(texture_file)
    textureFile.SetFileName(texture_file)
    textureFile.Update()

    atext = vtk.vtkTexture()
    atext.SetInputConnection(textureFile.GetOutputPort())
    atext.InterpolateOn()

    # generate warp from vti.
    global warp
    warp.SetInputConnection(reader.GetOutputPort())
    warp.SetScaleFactor(-75)
    
    merge_warp = vtk.vtkMergeFilter()
    merge_warp.SetGeometryConnection(warp.GetOutputPort())
    merge_warp.SetScalarsConnection(reader.GetOutputPort())
    
    # testing merge texture image with warp.
    #merge = vtk.vtkMergeFilter()
    #merge.SetGeometryConnection(merge_warp.GetOutputPort())
    #merge.SetScalarsConnection(textureFile.GetOutputPort())
    
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputConnection(merge_warp.GetOutputPort())
    mapper.SetScalarRange(0, 255)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    
    # texture assigment doesn't work.
    #actor.SetTexture(atext)
    
    # Create renderer stuff
    renderer = vtk.vtkRenderer()
    renderer_window = vtk.vtkRenderWindow()
    renderer_window.AddRenderer(renderer)
    renderer_window_interactor = vtk.vtkRenderWindowInteractor()
    renderer_window_interactor.SetRenderWindow(renderer_window)
    
    # add slide bar   
    slide_bar = generate_slide_bar()
    slider_widget = vtk.vtkSliderWidget()
    slider_widget.SetInteractor(renderer_window_interactor)
    slider_widget.SetRepresentation(slide_bar)
    slider_widget.AddObserver("InteractionEvent", custom_callback)
    slider_widget.EnabledOn()

    
    # Add the actors to the renderer, set the background and size
    renderer.AddActor(actor)
    renderer.ResetCamera()
    renderer.GetActiveCamera().Azimuth(180)
    renderer.GetActiveCamera().Roll(180)
    renderer.GetActiveCamera().Yaw(0)
    renderer.GetActiveCamera().Elevation(0)
    renderer.SetBackground(0.1, 0.1, 0.1)
    renderer.ResetCameraClippingRange()
    
    renderer_window.SetSize(1200, 800)
    
    cam1 = renderer.GetActiveCamera()
    cam1.Zoom(1.5)
    
    renderer_window_interactor.Initialize()
    renderer_window.Render()
    renderer_window_interactor.Start()

if __name__ == '__main__':
    main()