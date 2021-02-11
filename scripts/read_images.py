from read_dicom_series import read_dicom_series
from math import pi, ceil, exp
import numpy as np
import anisotropic_diffusion as ad


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


# function pushbutton4_Callback: line 683 - 805
def read_cest(cest_path):
    '''Read cest image.


    Parameters:

    cest_path (str): path to the CEST image


    Returns:

    cest_info (dict): dictionary that includes <CEST_path>, <CEST_ppm_list>,
                     <nCEST_ppm>, <nCEST_ppm>, <CEST_pos_images>,
                     <CEST_neg_images>, <CEST_hdr>, <CEST_pw>, <CEST_pw1>,
                     <CEST_b1>, <CEST_dc>

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

# line 851-854
def read_mp2rageT1(mp2rageT1_path):
    '''Read mp2rage T1 image


    Parameters:

    mp2rageT1_path (str): path to the mp2rage T1 image


    Returns:

    mp2rageT1_info (dict): dictionary that includes <mp2rageT1_hdr>, <
                           <mp2rageT1-img>, <mp2rageT1_raw_hdr>

    '''

    mp2rageT1_info = {}
    [mp2rageT1_hdr, mp2rageT1_img, mp2rageT1_raw_hdr] = read_dicom_series(mp2rageT1_path)
    mp2rageT1_info.update({"mp2rageT1_hdr": mp2rageT1_hdr,
                           "mp2rageT1_img": mp2rageT1_img,
                           "mp2rageT1_raw_hdr": mp2rageT1_raw_hdr})

    return mp2rageT1_info


# line 206-360
def read_wassr(wassr_path):
    '''Read wassr image


    Parameters:

    wassr_path (str): path to the wassr image


    Returns:

    wassr_info (dict): dictionary that includes <WASSR_pw>, <WASSR_pw1>,
                       <WASSR_b1>, <WASSR_dc>, <WASSR_ppm_list>, <nWASSR_ppm>,
                       <WASSR_pos_img>, <WASSR_neg_img>, <WASSR_hdr>

    '''

    wassr_info = {}


    wassr_info.update({"b0type": "WASSR"})

    # line 209-233 because we have siemens data and only 1 wassr dcm dir
    [wassr_hdr, wassr_img, wassr_raw_hdr] = read_dicom_series(wassr_path)
    nfreq = wassr_hdr["reps"]/2
    nfiles = wassr_hdr["reps"]
#     hdd = hdr
    seqname = wassr_hdr["SeqName"]
    swversion = wassr_hdr["swversion"]

    # line 245-262 truncated because our wassr data has swversion "VE11U"
    wip_ppm_index = 2
    prep_mode_index = 2
    cestz2_val = 3

    wassr_info.update({"WASSR_pw": wassr_hdr["WIPlong"][12],
                       "WASSR_pw1": wassr_hdr["WIPlong"][13],
                       "WASSR_b1": wassr_hdr["WIPlong"][15],
                       "WASSR_dc": wassr_hdr["WIPdbl"][0]})

    # line 275-318 truncated
    hd_index = 0
    ppm_index = 0

    hdr = [None] * (nfiles + hd_index)
    pos_img = [None] * (nfiles / 2 + ppm_index)
    neg_img = [None] * (nfiles / 2 + ppm_index)
    WASSR_ppm_list = [None] * ceil(nfiles / 2)

    for i in range(1, nfiles + 1, 2):
        j = (i + 1)/2
        hdr[i + hd_index - 1] = hdd
        hdr[i + hd_index] = hdd
        pos_img[j + ppm_index - 1] = wassr_img[i - 1]
        neg_img[j + ppm_index - 1] = wassr_img[i]

        if hdr[i + hd_index - 1]["WIPlong"][prep_mode_index - 1] == cestz2_val:
            ppm_begin = hdr[i + hd_index - 1]["WIPdbl"][wip_ppm_index]
            ppm_end = hdr[i + hd_index - 1]["WIPdbl"][wip_ppm_index + 1]
            ppm_step = hdr[i + hd_index - 1]["WIPdbl"][wip_ppm_index + 2]

            if ppm_begin > ppm_end:
                ppm_step = -ppmstep

            WASSR_ppm_list[j + ppm_index - 1] = ppm_begin + (j - 1) * ppm_step

        else:
            WASSR_ppm_list[j + ppm_index - 1] = hdr[i + hd_index - 1]["WIPdbl"][wip_ppm_index]


    wassr_info.update({"WASSR_ppm_list": WASSR_ppm_list,
                       "nWASSR_ppm": len(WASSR_ppm_list),
                       "WASSR_pos_img": pos_img,
                       "WASSR_neg_img": neg_img,
                       "WASSR_hdr": hdr})


    return(wassr_info)


# function pushbutton4_Callback: line 437 - 491
def read_ref(ref_path):
    '''Read reference image.


    Parameters:

    ref_path (str): path to the reference image


    Returns:

    ref_info (dict): dictionary that includes <dicomhdr>, <ref_dicomhdr>,
                     <ref_path>, <ref_img>, <bias>, and <ref_img_b>

    '''
    ref_info = {}

    [header, ref_img, dicomhdr] = read_dicom_series(ref_path)
    # ref_img is a 3D image with dim (1, 224, 224) so convert into 2D
    ref_img = ref_img[0]
    ref_info.update({"dicomhdr": dicomhdr, # WHY AFTER PARSING THROUGH THE DICOM
                                           # HEADER FILE TO OBTAIN <HEADER>, IS IT NOT USED?!?!?!?!?!?!?
                     "ref_dicomhdr": dicomhdr,
                     "ref_path": ref_path,
                     "ref_img": ref_img})


    [nrows, ncols] = ref_img.shape
    ref_info.update({"ref_img_dim": [nrows, ncols]})
    ref_img_scaled = 2000.0 * (ref_img / ref_img.max())
    noise = ref_img_scaled[ref_img_scaled < 100]
    noise_std = np.std(noise)
    threshold = 8 * noise_std

    bias_img = ad.anisodiff(ref_img, 10, 10000, 0.25, 1)

    mask = np.zeros((nrows, ncols))

    ref_max_val = ref_img.max()
    mask[ref_img_scaled > threshold] = 1.0

    bias_max_val = bias_img.max()
    bias_scale = ref_max_val / (bias_img + 0.01)
    bias_scale[mask == 0] = 1.0
    bias_scale[bias_scale < 0] = 1.0
    bias_scale[bias_scale > 30] - 1.0
    # ref_scaled_masked_biased
    rsmb = (ref_img_scaled * mask) * bias_scale

    bias_scale[rsmb > ref_max_val] = bias_scale[rsmb > ref_max_val] * (ref_max_val / rsmb[rsmb > ref_max_val])

    # bias_display = 2000.0 * bias_scale/bias_scale.max()
    ref_img_b = ref_img_scaled * bias_scale
    ref_img_b = 2000,0 * ref_img_scaled/ref_img_b.max()
    # displayimages(handles.refimage, biasdisplay,'Refimage and Biasscale',0,2000 );

    ref_info.update({"bias": bias_scale})
    ref_info.update({"ref_img_b": ref_img_b})

    return ref_info
