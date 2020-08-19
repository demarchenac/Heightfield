# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 11:58:01 2020

@author: Jhon Corro
@author: Cristhyan De Marchena
"""
import vtk

warp = vtk.vtkWarpScalar()

def get_program_parameters():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('data_file', nargs='?', default=None, help='data file')
    parser.add_argument('texture_file', nargs='?', default=None, help='texture file')
    args = parser.parse_args()
    
    return args.data_file, args.texture_file

def read_file(file_name):
    import os
    if(file_name):
        path, extension = os.path.splitext(file_name)
        extension = extension.lower()
        if extension == ".vti":
            reader = vtk.vtkXMLImageDataReader()
            reader.SetFileName(file_name)
        elif extension == ".vtp":
            reader = vtk.vtkXMLPolyDataReader()
            reader.SetFileName(file_name)
        elif extension == ".jpg":
            readerFactory = vtk.vtkImageReader2Factory()
            img_file = readerFactory.CreateImageReader2(file_name)
            img_file.SetFileName(file_name)
            img_file.Update()
            reader = img_file
        else:
            # the file provided doesn't match the accepted extenstions
            reader = None
    else:
        reader = None
    return reader

def generate_texture(texture_file):
    texture_file = read_file(texture_file)
    if(texture_file):
        texture = vtk.vtkTexture()
        texture.SetInputConnection(texture_file.GetOutputPort())
        texture.InterpolateOn()
    else: 
        texture = None
    return texture
    

def generate_actor(data, texture):
    # Warp the input data.
    global warp
    warp.SetInputConnection(data.GetOutputPort())
    warp.SetScaleFactor(0)
    
    # Add mapper.
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputConnection(warp.GetOutputPort())
    mapper.SetScalarRange(0, 255)
    mapper.ScalarVisibilityOff()
    
    # Generate actor from mapper.
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.SetTexture(texture)
    return actor

def generate_slide_bar():
    # Slidebar colors
    red_r = 224/255
    red_g = 69/255
    red_b = 85/255
    green_r = 70/255
    green_g = 224/255
    green_b = 105/255
    white = 242/255
    
    # Create Slidebar
    slide_bar = vtk.vtkSliderRepresentation2D()
    
    # Set range and title.
    slide_bar.SetMinimumValue(-100.0)
    slide_bar.SetMaximumValue(100.0)
    slide_bar.SetValue(0)
    slide_bar.SetTitleText("Scalar Value")
    
    # Set colors.
    slide_bar.GetSliderProperty().SetColor(red_r, red_g, red_b)
    slide_bar.GetTitleProperty().SetColor(white, white, white)
    slide_bar.GetLabelProperty().SetColor(red_r, red_g, red_b)
    slide_bar.GetSelectedProperty().SetColor(green_r, green_g, green_b)
    slide_bar.GetTubeProperty().SetColor(white, white, white)
    slide_bar.GetCapProperty().SetColor(red_r, red_g, red_b)
    
    # Set coordinates.
    slide_bar.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
    slide_bar.GetPoint1Coordinate().SetValue(0.78, 0.1)
    
    slide_bar.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
    slide_bar.GetPoint2Coordinate().SetValue(0.98 , 0.1)
    return slide_bar

def custom_callback(obj, event):
    # print("interaction called")
    value = int (obj.GetRepresentation().GetValue())
    global warp
    warp.SetScaleFactor(value)
    warp.Update()

def generate_gui(actor):
    # Create renderer stuff
    renderer = vtk.vtkRenderer()
    renderer_window = vtk.vtkRenderWindow()
    renderer_window.AddRenderer(renderer)
    renderer_window_interactor = vtk.vtkRenderWindowInteractor()
    renderer_window_interactor.SetRenderWindow(renderer_window)
    
    # Add slide bar   
    slide_bar = generate_slide_bar()
    slider_widget = vtk.vtkSliderWidget()
    slider_widget.SetInteractor(renderer_window_interactor)
    slider_widget.SetRepresentation(slide_bar)
    slider_widget.AddObserver("InteractionEvent", custom_callback)
    slider_widget.EnabledOn()

    
    # Add the actor and camera to the renderer, set background and size
    renderer.AddActor(actor)
    renderer.ResetCamera()
    renderer.GetActiveCamera().Azimuth(180)
    renderer.GetActiveCamera().Roll(180)
    renderer.GetActiveCamera().Yaw(0)
    renderer.GetActiveCamera().Elevation(0)
    renderer.SetBackground(0.1, 0.1, 0.1)
    renderer.ResetCameraClippingRange()
    renderer_window.SetSize(renderer_window.GetScreenSize());
    cam1 = renderer.GetActiveCamera()
    cam1.Zoom(1.5)
    
    # Smoother camera controls
    renderer_window_interactor.GetInteractorStyle().SetCurrentStyleToTrackballCamera();
    renderer_window_interactor.Initialize()
    renderer_window.Render()
    renderer_window.SetWindowName('Heightfield Visualizer')
    renderer_window.Render()
    renderer_window_interactor.Start()
    

def main():
    # Get file paths from cli params.
    data_file, texture_file = get_program_parameters()
    
    # Read data file.
    data = read_file(data_file)
    if(data):
        # Generate texture.
        texture = generate_texture(texture_file)        
        if(texture):      
            # Generate actor.
            actor = generate_actor(data, texture)
            # Generate GUI
            generate_gui(actor)
        else:
            print('The texture file was not found or the file provided does not match the .jpg extension.')
    else:
        print('The data file was not found or the file provided does not match neither the .vti and .vtp extension.')
    

if __name__ == '__main__':
    main()