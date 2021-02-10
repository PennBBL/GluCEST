from read_dicom_series import read_dicom_series
from math import pi

# line 370-434
def read_B1(B1_path):
    '''Read B1 image


    Parameters:

    B1_path (str): path to the B1 image


    Returns:

    B1_info (dict): dictionary that includes <B1_img1>, <B1_img2>,
                     <B1_img3>, <alpha>, <B1_hdr>

    '''
    # line 370-384 truncated
    B1_info = {}

    # There is always 1 directory of B1 dicom images to read
    # line 392-408 truncated

    [B1_hdr, B1_img, B1_raw_hdr] = read_dicom_series(B1_path)
    [nreps, nrows, ncols] = B1_img.shape
    B1_info.update({"B1_img1": B1_img[0],
                    "B2_img2": B1_img[1]})

    if nreps == 3:
        B1_info.update({"B1_img3": B1_img[2]})

    # line 417-425 because our file is moco

    B1_info.update({"alpha": pi * B1_hdr["WIPdbl"][1] / 180.0,
                    "B1_hdr": B1_hdr})

    return(B1_info)
