import pydicom
import os
import numpy as np

def read_dicom_series(dcm_series_dir):
    '''
    Reads a series of dicom files in path <dcm_series_dir>


        Parameters:

            dcm_series_dir (str): path to a series of dicom files


        Returns:
            
            sum_dcm_series (list): list including a header dictionary, numpy array of images, and a pydicom object

    '''

    header = {}

    dcm_files = []

    # TODO: if the loop ends without finding a proper dcm file raise warning

    num_dcm_files = 0
    for dcm in os.listdir(dcm_series_dir):
        
        if dcm.endswith(".txt"):
            dcm_hdr_file = os.path.join(dcm_series_dir, dcm)
        
        # check if dcm is actually a dicom file
        elif not dcm.endswith(".dcm"):
            continue

        # dcm is a dicom file
        else:
            dcm_path = os.path.join(dcm_series_dir, dcm)
            dcm_files.append(dcm_path)
            num_dcm_files = num_dcm_files + 1

    # first file and extract information
    dcm = pydicom.read_file(dcm_files[0])
    # update header info
    header.update({"n1": dcm.Rows,
                   "n2": dcm.Columns,
                   "trajectory": "cartesian"})

    # TODO: Ask Abby What is this????
    # Initialize WIP values
    WIPlong = []
    WIPdbl = []
    for i in range(0, 64):
        WIPlong.append(0)
        if i < 16:
            WIPdbl.append(0)
    # update header info
    header.update({"WIPlong": WIPlong,
                   "WIPdbl": WIPdbl})
    
    # TODO: I think I should first check if the below attributes exists
    # because maybe it varies by file type. If they are returned regardless,
    # We should be able to extract explicit metadata info by passing an argument
    # in the pydicom.read_file()
    # ProtocolName
    header.update({"ProtocolName": dcm.ProtocolName})
    
    # ImagedNucleus value
    nucleus = dcm.ImagedNucleus
    if "23N" in nucleus:
        gamma = 11.2620
    elif "170" in nucleus:
        gamma = 5.7716
    elif "13C" in nucleus:
        gamma = 10.7063
    else:
        gamma = 42.5756
    
    # update header
    header.update({"Nucleus": nucleus})
    header.update({"gamma": gamma})
    
    # ImagingFrequency
    header.update({"sf": dcm.ImagingFrequency})
    
    # SliceThickness
    header.update({"slthk": dcm.SliceThickness})
    
    # NumberofPhaseEncondingSteps
    header.update({"phfov": dcm.NumberOfPhaseEncodingSteps})
    
    # Number of ReferencedImagedSequence
    header.update({"echoes": len(dcm.ReferencedImageSequence)})
    
    header.update({"ndim": 2})
    

    
    dcm_txt = open(dcm_hdr_file, "r")
    dcm_txt_line = dcm_txt.readline().strip()
    dcm_txt_line = dcm_txt_line.replace('\t', '')
    dcm_txt_line = dcm_txt_line.replace(' ', '')

    while "ASCCONVEND" not in dcm_txt_line:
        dcm_txt_line = dcm_txt.readline().strip()
        dcm_txt_line = dcm_txt_line.replace('\t', '')
        dcm_txt_line = dcm_txt_line.replace(' ', '')

        if "tSequenceFileName" in dcm_txt_line:
            tindex1 = dcm_txt_line.find('""') + 2
            tindex2 = len(dcm_txt_line) - 2
            tname = dcm_txt_line[tindex1:tindex2]
            header.update({"SeqName": tname})

#         if "tProtocolName" in dcm_txt_line:
#             tindex1 = dcm_txt_line.find('""') + 2
#             tindex2 = len(dcm_txt_line) - 2
#             tname = dcm_txt_line[tindex1:tindex2]
#             tname = tname.replace("+AF8-", "-")
#             header.update({"ProtocolName": tname})

        if ("sProtConsistencyInfo.tBaselineString" in dcm_txt_line) or \
        ("sProtConsistencyInfo.tMeasuredBaselineString" in dcm_txt_line):
            tindex1 = dcm_txt_line.find('""') + 2
            tindex2 = len(dcm_txt_line) - 2
            tname = dcm_txt_line[tindex1:tindex2]
            header.update({"swversion": tname})

#         if "sTXSPEC.asNucleusInfo[0].tNucleus" in dcm_txt_line:
#             tindex1 = dcm_txt_line.find('""') + 2
#             tindex2 = len(dcm_txt_line) - 2
#             tname = dcm_txt_line[tindex1:tindex2]
#             header.update({"Nucleus": tname})

#             if "1H" in tname:
#                 header.update({"gamma": 42.5756})
#             elif "23N" in tname:
#                 header.update({"gamma": 11.2620})
#             elif "170" in tname:
#                 header.update({"gamma": 5.7716})
#             elif "13C" in tname:
#                 header.update({"gamma": 10.7063})
#             else:
#                 header.update({"gamma": 42.5756})

#         if "sTXSPEC.asNucleusInfo[0].lFrequency" in dcm_txt_line:
#             tindex1 = dcm_txt_line.find("=") + 1
#             tname = dcm_txt_line[tindex1:len(dcm_txt_line)]
#             header.update({"sf": float(tname) * 1.0e-6})

        if "sRXSPEC.alDwellTime[0]" in dcm_txt_line:
            tindex1 = dcm_txt_line.find("=") + 1
            tname = dcm_txt_line[tindex1:len(dcm_txt_line)]
            dwus = float(tname) * 0.001
            header.update({"dwus": dwus})
            header.update({"sw": 1.0e6 / dwus})

        if "lContrasts" in dcm_txt_line:
            tindex1 = dcm_txt_line.find("=") + 1
            tname = dcm_txt_line[tindex1:len(dcm_txt_line)]
            header.update({"contrasts": float(tname)})

        TEms = []
        for iTE in range(0,10):
            tnamestr = "alTE[%i]" % iTE
            if tnamestr in dcm_txt_line:
                tindex1 = dcm_txt_line.find("=") + 1
                tname = dcm_txt_line[tindex1:len(dcm_txt_line)]
                TEms.append(float(tname) * 0.001)
#                 header info "echoes" == len(dcm.ReferencedImageSequence)
#                 header.update({"echoes": iTE})
        header.update({"TEms": TEms})

#         if "sSliceArray.asSlice[0].dThickness" in dcm_txt_line:
#             tindex1 = dcm_txt_line.find("=") + 1
#             tname = dcm_txt_line[tindex1:len(dcm_txt_line)]
#             header.update({"slthk": float(tname)})

#         if "sSliceArray.asSlice[0].dPhaseFOV" in dcm_txt_line:
#             tindex1 = dcm_txt_line.find("=") + 1
#             tname = dcm_txt_line[tindex1:len(dcm_txt_line)]
#             header.update({"phfov": float(tname)})

        if "sSliceArray.asSlice[0].dReadoutFOV" in dcm_txt_line:
            tindex1 = dcm_txt_line.find("=") + 1
            tname = dcm_txt_line[tindex1:len(dcm_txt_line)]
            header.update({"rdfov": float(tname)})

        if "sSliceArray.lSize" in dcm_txt_line:
            tindex1 = dcm_txt_line.find("=") + 1
            tname = dcm_txt_line[tindex1:len(dcm_txt_line)]
            header.update({"nslices": float(tname)})

        if "sKSpace.lBaseResolution" in dcm_txt_line:
            tindex1 = dcm_txt_line.find("=") + 1
            tname = dcm_txt_line[tindex1:len(dcm_txt_line)]
            header.update({"nx": float(tname)})

        if "sKSpace.lPhaseEncodingLines" in dcm_txt_line:
            tindex1 = dcm_txt_line.find("=") + 1
            tname = dcm_txt_line[tindex1:len(dcm_txt_line)]
            header.update({"ny": float(tname)})

        if "sKSpace.lImagesPerSlab" in dcm_txt_line:
            tindex1 = dcm_txt_line.find("=") + 1
            tname = dcm_txt_line[tindex1:len(dcm_txt_line)]
            header.update({"nz": float(tname)})

        if "sKSpace.lRadialViews" in dcm_txt_line:
            tindex1 = dcm_txt_line.find("=") + 1
            tname = dcm_txt_line[tindex1:len(dcm_txt_line)]
            header.update({"nrad": float(tname)})

        header.update({"ndim": 2})

        if "sKSpace.ucDimension" in dcm_txt_line:
            tindex1 = dcm_txt_line.find("=") + 1
            tname = dcm_txt_line[tindex1:len(dcm_txt_line)]

            if "0x" in tname:
                tname1 = tname[3:len(tname)]
                ndimflag = float(tname1, 16)
                ndim = 1

                while(ndimflag > 1):
                    ndim = ndim + 1
                    ndimflag = ndimflag/2
                header.update({"ndim": ndim})

            else:
                header.update({"ndim": float(tname)})

        if "sKSpace.ucTrajectory" in dcm_txt_line:
            tindex1 = dcm_txt_line.find("=") + 1
            tname = dcm_txt_line[tindex1:len(dcm_txt_line)]

            if "0x" in tname:
                tname1 = tname[3:len(tname)]
                traj = float(tname1, 16)
            else:
                traj = float(tname)
            if traj < 2:
                header.update({"trajectory": "cartesian"})
            else:
                header.update({"trajectory": "radial"})

        if "lAverages" in dcm_txt_line:
            tindex1 = dcm_txt_line.find("=") + 1
            tname = dcm_txt_line[tindex1:len(dcm_txt_line)]
            header.update({"averages": float(tname)})

        if "lRepetitions" in dcm_txt_line:
            if "alRepetitions" not in dcm_txt_line:
                tindex1 = dcm_txt_line.find("=") + 1
                tname = dcm_txt_line[tindex1:len(dcm_txt_line)]
                header.update({"reps": int(float(tname)) + 1})

        if "sWiPMemBlock.alFree" in dcm_txt_line:
            for ilong in range(0,64):
                tnamestr = "sWiPMemBlock.alFree[%i]" % ilong
                if tnamestr in dcm_txt_line:
                    tindex1 = dcm_txt_line.find("=") + 1
                    tname = dcm_txt_line[tindex1:len(dcm_txt_line)]
                    value = float(tname)
                    header["WIPlong"][ilong] = value

        if "sWiPMemBlock.adFree" in dcm_txt_line:
            for idbl in range(0,16):
                tnamestr = "sWiPMemBlock.adFree[%i]" % idbl
                if tnamestr in dcm_txt_line:
                    tindex1 = dcm_txt_line.find("=") + 1
                    tname = dcm_txt_line[tindex1:len(dcm_txt_line)]
                    value = float(tname)
                    header["WIPdbl"][idbl] = value

        if "sWipMemBlock.alFree" in dcm_txt_line:
            for idbl in range(0,16):
                tnamestr = "sWipMemBlock.alFree[%i]" % idbl
                if tnamestr in dcm_txt_line:
                    tindex1 = dcm_txt_line.find("=") + 1
                    tname = dcm_txt_line[tindex1:len(dcm_txt_line)]
                    value = float(tname)
                    header["WIPlong"][idbl] = value

        if "sWipMemBlock.adFree" in dcm_txt_line:
            for idbl in range(0,16):
                tnamestr = "sWipMemBlock.adFree[%i]" % idbl
                if tnamestr in dcm_txt_line:
                    tindex1 = dcm_txt_line.find("=") + 1
                    tname = dcm_txt_line[tindex1:len(dcm_txt_line)]
                    value = float(tname)
                    header["WIPdbl"][idbl] = value


    # while ASCCONV
    dcm_txt.close()

    if "echoes" not in header.keys():
        header.update({"echoes": 1})

    header.update({"nTE": header["echoes"]})

    if "radi" in header["trajectory"]:
        header.update({"nrad": 0})
    
    if header["ndim"] < 3:
        header.update({"nz": 1})

    if "reps" not in header.keys():
        header.update({"reps": 1})

    dcm_images = np.zeros((header["reps"], header["n1"], header["n2"]))
    
    # hwaitbar = waitbar( 0,sprintf('Reading %i image files ...',nfiles) );
    for rep in range(0, header["reps"]):
        # waitbar(ind1/nfiles):
        dcm = pydicom.read_file(dcm_files[rep])
        dcm_images[rep] = dcm.pixel_array

    
    sum_dcm_series = [header, dcm_images, pydicom.dcmread(dcm_files[0], stop_before_pixels = True)]
    return sum_dcm_series

    
