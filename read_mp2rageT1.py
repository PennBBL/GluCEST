from read_dicom_series import read_dicom_series

# line 851-854
def read_mp2rageT1(mp2rageT1_path):
    '''Read mp2rage T1 image


    Parameters:

    mp2rageT1_path (str): path to the mp2rage T1 image


    Returns:

    mp2rageT1_info (dict): dictionary that includes <dicomhdr>, <cest_dicomhdr>,
                     <cest_path>, <cest_img>, <bias>, and <ref_img_b>

    '''

    mp2rageT1_info = {}
    [mp2rageT1_hdr, mp2rageT1_img, mp2rageT1_raw_hdr] = read_dicom_series(mp2rageT1_path)
    mp2rageT1_info.update({"mp2rageT1_hdr": mp2rageT1_hdr,
                           "mp2rageT1_img": mp2rageT1_img,
                           "mp2rageT1_raw_hdr": mp2rageT1_raw_hdr})

    return mp2rageT1_info
