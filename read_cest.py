import numpy as np
import anisotropic_diffusion as ad
from read_dicom_series import read_dicom_series

# function pushbutton4_Callback: line 683 - 805
def read_cest(cest_path):
    '''Read cest image.


    Parameters:

    cest_path (str): path to the CEST image


    Returns:

    cest_info (dict): dictionary that includes <dicomhdr>, <cest_dicomhdr>,
                     <cest_path>, <cest_img>, <bias>, and <ref_img_b>

    '''

    # cest info dictionary to be returned
    cest_info = {}

    [cest_hdr, cest_img, dcm_hdr] = read_dicom_series(cest_path)

    nfreq = cest_hdr["reps"] / 2
    nfiles = cest_hdr["reps"]

    # handles.refpath
    cest_info.update({"CEST_path": cest_path})

    seq_name = cest_hdr["SeqName"]

    if "swversion" not in cest_hdr.keys():
        # TODO: throw error...??
        return

    swversion = cest_hdr["swversion"]

    # "swversion" is a key in cest_hdr:
    if "VD13A" in swversion:
        wip_ppm_index = 3
        prep_mode_index = 1
        cestz2_value = 5
        CEST_pw = cest_hdr["WIPlong"][10]
        CEST_pw1 = cest_hdr["WIPlong"][12]
        CEST_b1 = cest_hdr["WIPlong"][13]
        CEST_dc = cest_hdr["WIPlong"][0]
#         cest_info.update({"CESTpw": hd1.WIPlong[10]})
#         cest_info.update({"CESTpw1": hd1.WIPlong[12]})
#         cest_info.update({"CESTb1": hd1.WIPlong[13]})
#         cest_info.update({"CESTdc": hd1.WIPdbl[0]})

    elif "VD13D" in swversion:
        wip_ppm_index = 2
        prep_mode_index = 2
        cestz2_value = 3
        CEST_pw = 0.001 * cest_hdr["WIPlong"][12]
        CEST_pw1 = 0.001* cest_hdr["WIPlong"][13]
        CEST_b1 = cest_hdr["WIPlong"][15]
        CEST_dc = cest_hdr["WIPlong"][0]

    # TODO: line 710 to 770 truncated because it doesn't apply to our data
    elif "prep_moco" in seq_name:
        wip_ppm_index = 2
        prep_mode_index = 2
        cestz2_value = 3

        if cest_hdr["WIPlong"][18] >= 170:
            CEST_pw = cest_hdr["WIPlong"][9]
            CEST_pw1 = cest_hdr["WIPlong"][12]
            CEST_b1 = cest_hdr["WIPlong"][10]
            CEST_dc = cest_hdr["WIPlong"][0]

            # TODO: throw missing info error??? (b1 value, pulse duration, pulse width1, and dutycycle??)

    # line 722
    if "VE11U" in swversion:
        wip_ppm_index = 2
        prepmodeindex = 2
        if "tlf" in seq_name:
            cestz2_value = 4
        else:
            cestz2_value = 3
        CEST_pw = cest_hdr["WIPlong"][12]
        CEST_pw1 = cest_hdr["WIPlong"][13]
        CEST_b1 = cest_hdr["WIPlong"][15]
        CEST_dc = cest_hdr["WIPlong"][0]

    # line 770 we always have just 1 CEST image
    h_index = 0
    ppm_index = 0

    hdr = [None] * nfiles
    hdd = [None] * nfiles
    hdd[0] = cest_hdr

    CEST_ppm_list = np.zeros(10)
    pos_img = np.zeros(cest_img.shape)
    neg_img = np.zeros(cest_img.shape)


    for i in range(1, nfiles + 1, 2):
        j = int((i + 1)/2 - 1)
        i = i - 1

        hdr[i] = hdd[0]
        hdr[i + 1] = hdd[0]
        pos_img[j + ppm_index] = cest_img[i]
        neg_img[j + ppm_index] = cest_img[i + 1]

        if hdr[i]["WIPlong"][prep_mode_index - 1] == cestz2_value:
            ppm_begin = hdr[i]["WIPdbl"][wip_ppm_index]
            ppm_end = hdr[i]["WIPdbl"][wip_ppm_index + 1]
            ppm_step = hdr[i]["WIPdbl"][wip_ppm_index + 2]

            if ppm_begin > ppm_end:
                ppm_step = -ppmstep

            CEST_ppm_list[j + ppm_index - 1] = ppm_begin + (j - 1) * ppm_step
        else:
            CEST_ppm_list[j + ppm_index - 1] = hdr[i]["WIPdbl"][wip_ppm_index - 1]


    cest_info.update({"CEST_ppm_list": CEST_ppm_list})
#     There's only 1 nfreq
#     cest_info.update({"nCEST_ppm": nfreq})
    cest_info.update({"nCEST_ppm": nfreq})
    cest_info.update({"CEST_pos_images": pos_img})
    cest_info.update({"CEST_neg_images": neg_img})
    cest_info.update({"CEST_hdr": hdr})
    cest_info.update({"CEST_pw": CEST_pw})
    cest_info.update({"CEST_pw1": CEST_pw1})
    cest_info.update({"CEST_b1": CEST_b1})
    cest_info.update({"CEST_dc": CEST_dc})
    
    # line 807-861 truncated because our data is always NSELIR
    return cest_info
