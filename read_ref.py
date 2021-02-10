import numpy as np
import anisotropic_diffusion as ad
from read_dicom_series import read_dicom_series

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
    
