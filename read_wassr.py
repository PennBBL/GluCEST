from read_dicom_series import read_dicom_series
from math import ceil, pi

# line 206-360
def read_wassr(wassr_path):
    '''Read wassr image


    Parameters:

    wassr_path (str): path to the wassr image


    Returns:

    wassr_info (dict): dictionary that includes <B1_img1>, <B1_img2>,
                     <B1_img3>, <alpha>, <B1_hdr>

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
