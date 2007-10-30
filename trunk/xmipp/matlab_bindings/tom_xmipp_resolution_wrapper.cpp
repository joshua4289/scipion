/*=================================================================
 *
 * tom_xmipp_resolution is a wrapper to xmipp_resolution
 *
 * The calling syntax is:
 *
 *		im_out = tom_xmipp_resolution_wrapper(volume,reference,objectpixelsize)
 *
 * Electron Tomography toolbox of the
 * Max-Planck-Institute for Biochemistry
 * Dept. Molecular Structural Biology
 * 82152 Martinsried, Germany
 * http://www.biochem.mpg.de
 *
 * and
 *
 * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
 *
 *
 * created: 12/10/2007
 * by: Andreas Korinek
 *
 *=================================================================*/

/*xmipp includes */
#include "image.h"
#include "volume.h"
#include "fft.h"
#include "tom_xmipp_helpers.h"

/*Matlab includes*/
#include "mex.h"
#include "matrix.h"

void mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray*prhs[])
{
 
    Matrix1D<double> freq, frc, dpr, frc_noise;

    float sam = (float) mxGetScalar(prhs[2]);
    mwSize ndims = mxGetNumberOfDimensions(prhs[0]);
    
    if (ndims == 2)
    {
        Image img, ref;
        getMatrix2D(prhs[0],img());
        getMatrix2D(prhs[1],ref());
        fourier_ring_correlation(ref(), img(), sam, freq, frc, frc_noise);
        differential_phase_residual(ref(), img(), sam, freq, dpr);
    }
    else
    {
        Volume img, ref;
        getMatrix3D(prhs[0],img());
        getMatrix3D(prhs[1],ref());
        fourier_ring_correlation(ref(), img(), sam, freq, frc, frc_noise);
        differential_phase_residual(ref(), img(), sam, freq, dpr);
    }

    const char *field_names[] = {"freq","dpr","frc","frc_noise"};
    mwSize dims[2] = {1, 1};
    plhs[0] = mxCreateStructArray(2, dims, NUMBER_OF_FIELDS, field_names);
    
    mxArray *field1, *field2, *field3, *field4;
    setMatrix1D(freq,field1);
    mxSetField(plhs[0],0,"freq",field1);

    setMatrix1D(dpr,field2);
    mxSetField(plhs[0],0,"dpr",field2);

    setMatrix1D(frc,field3);
    mxSetField(plhs[0],0,"frc",field3);

    setMatrix1D(frc_noise,field4);
    mxSetField(plhs[0],0,"frc_noise",field4);
   
    frc.core_deallocate();
    
}
