# -*- coding: utf-8 -*-
"""
Created on Fri Aug 14 11:58:01 2020

@author: John Corro
@author: Cristhyan De Marchena
"""

import vtk

def get_program_parameters():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('vti_file', nargs='?', default=None, help='vti file')
    parser.add_argument('texture_file', nargs='?', default=None, help='jpg file')
    args = parser.parse_args()
    
    return args.vti_file, args.texture_file


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
    warp = vtk.vtkWarpScalar()
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
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    
    # Add the actors to the renderer, set the background and size
    ren.AddActor(actor)
    ren.ResetCamera()
    ren.GetActiveCamera().Azimuth(180)
    ren.GetActiveCamera().Roll(180)
    ren.GetActiveCamera().Yaw(0)
    ren.GetActiveCamera().Elevation(0)
    ren.SetBackground(0.1, 0.1, 0.1)
    ren.ResetCameraClippingRange()
    
    renWin.SetSize(600, 400)
    
    cam1 = ren.GetActiveCamera()
    cam1.Zoom(1.5)
    
    iren.Initialize()
    renWin.Render()
    iren.Start()

if __name__ == '__main__':
    main()