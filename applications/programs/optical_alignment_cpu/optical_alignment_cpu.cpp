/***************************************************************************
 * Authors:     Vahid Abrishami (vabrishami@cnb.csic.es)
 *
 *
 * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
 * 02111-1307  USA
 *
 *  All comments concerning this program package may be sent to the
 *  e-mail address 'xmipp@cnb.csic.es'
 ***************************************************************************/

#include <vector>
#include <sstream>
#include <fstream>
#include <time.h>

#include "opencv2/core/core.hpp"
#include "opencv2/highgui/highgui.hpp"
#include "opencv2/video/video.hpp"
#include "opencv2/gpu/gpu.hpp"

#include <data/multidim_array.h>
#include <data/xmipp_image.h>
#include <data/normalize.h>
#include <data/xmipp_fftw.h>


using namespace std;
using namespace cv;
#ifdef GPU
using namespace cv::gpu;
#endif
class ProgOpticalAligment: public XmippProgram
{

public:
    FileName fname, foname;

    int winSize, gpuDevice, fstFrame, lstFrame;
    bool doAverage, psd;

    void defineParams()
    {
        addUsageLine ("Align moviews using optical flow");
        addParamsLine("     -i <inMoviewFnName>          : input movie File Name");
        addParamsLine("     -o <outAverageMoviewFnName>  : output aligned micrograhp File Name");
        addParamsLine("     [--nst <int=0>]     : first frame used in alignment (0 = first frame in the movie");
        addParamsLine("     [--ned <int=0>]     : last frame used in alignment (0 = last frame in the movie ");
        addParamsLine("     [--winSize <int=150>]     : window size for optical flow algorithm");
        addParamsLine("     [--simpleAverage]: if we want to just compute the simple average");
        addParamsLine("     [--psd]             : save raw PSD and corrected PSD");
#ifdef GPU

        addParamsLine("     [--gpu <int=0>]         : GPU device to be used");
#endif

    }
    void readParams()
    {
        fname     = getParam("-i");
        foname    = getParam("-o");
        fstFrame  = getIntParam("--nst");
        lstFrame  = getIntParam("--ned");
        winSize   = getIntParam("--winSize");
        doAverage = checkParam("--simpleAverage");
        psd = checkParam("--psd");
#ifdef GPU

        gpuDevice = getIntParam("--gpu");
#endif

    }
    void run()
    {
        main2();
    }

    // Save a matrix which is generated by OpenCV
    int saveMat( const string& filename, const Mat& M)
    {
        if (M.empty())
        {
            return 0;
        }
        ofstream out(filename.c_str(), ios::out|ios::binary);
        if (!out)
            return 0;

        int cols = M.cols;
        int rows = M.rows;
        int chan = M.channels();
        int eSiz = (M.dataend-M.datastart)/(cols*rows*chan);

        // Write header
        out.write((char*)&cols,sizeof(cols));
        out.write((char*)&rows,sizeof(rows));
        out.write((char*)&chan,sizeof(chan));
        out.write((char*)&eSiz,sizeof(eSiz));

        // Write data.
        if (M.isContinuous())
        {
            out.write((char *)M.data,cols*rows*chan*eSiz);
        }
        else
        {
            return 0;
        }
        out.close();
        return 1;
    }

    // Load a matrix which is generated by saveMat
    int readMat( const string& filename, Mat& M)
    {
        ifstream in(filename.c_str(), ios::in|ios::binary);
        if (!in)
        {
            //M = NULL_MATRIX;
            return 0;
        }
        int cols;
        int rows;
        int chan;
        int eSiz;

        // Read header
        in.read((char*)&cols,sizeof(cols));
        in.read((char*)&rows,sizeof(rows));
        in.read((char*)&chan,sizeof(chan));
        in.read((char*)&eSiz,sizeof(eSiz));

        // Determine type of the matrix
        int type = 0;
        switch (eSiz)
        {
        case sizeof(char):
                        type = CV_8UC(chan);
            break;
        case sizeof(float):
                        type = CV_32FC(chan);
            break;
        case sizeof(double):
                        type = CV_64FC(chan);
            break;
        }

        // Alocate Matrix.
        M = Mat(rows,cols,type,Scalar(1));

        // Read data.
        if (M.isContinuous())
{
            in.read((char *)M.data,cols*rows*chan*eSiz);
        }
        else
        {
            return 0;
        }
        in.close();
        return 1;
    }

    // Converts a XMIPP MultidimArray to OpenCV matrix
    void xmipp2Opencv(const MultidimArray<double> &xmippArray, Mat &opencvMat)
    {
        int h = YSIZE(xmippArray);
        int w = XSIZE(xmippArray);
        opencvMat = cv::Mat::zeros(h, w,CV_32FC1);
        FOR_ALL_DIRECT_ELEMENTS_IN_ARRAY2D(xmippArray)
        opencvMat.at<float>(i,j) = DIRECT_A2D_ELEM(xmippArray,i,j);
    }

    // Converts an OpenCV matrix to XMIPP MultidimArray
    void opencv2Xmipp(const Mat &opencvMat, MultidimArray<double> &xmippArray)
    {
        int h = opencvMat.rows;
        int w = opencvMat.cols;
        xmippArray.initZeros(h, w);
        FOR_ALL_DIRECT_ELEMENTS_IN_ARRAY2D(xmippArray)
        DIRECT_A2D_ELEM(xmippArray,i,j) = opencvMat.at<float>(i,j);
    }

    // Converts an OpenCV float matrix to an OpenCV Uint8 matrix
    void convert2Uint8(Mat opencvDoubleMat, Mat &opencvUintMat)
    {
        Point minLoc,maxLoc;
        double min,max;
        cv::minMaxLoc(opencvDoubleMat, &min, &max, &minLoc, &maxLoc, noArray());
        opencvDoubleMat.convertTo(opencvUintMat, CV_8U, 255.0/(max - min), -min * 255.0/(max - min));
    }

    // Computes the average of a number of frames in movies
    void computeAvg(const FileName &movieFile, int begin, int end, MultidimArray<double> &avgImg)
    {

        int N = (end-begin)+1;
        ImageGeneric movieStack;
        MultidimArray<double> imgNormal, sumImg;

        movieStack.readMapped(movieFile,begin);
        movieStack().getImage(imgNormal);
        sumImg=imgNormal;

        for (int i=begin;i<end;i++)
        {
            movieStack.readMapped(movieFile,i+1);
            movieStack().getImage(imgNormal);
            sumImg += imgNormal;
        }
        avgImg = sumImg/double(N);
    }

    int main2()
    {
        // XMIPP structures are defined here
        MultidimArray<double> preImg, avgCurr, avgStep, mappedImg;
        ImageGeneric movieStack, movieStackNormalize;
        Image<double> II;
        MetaData MD; // To save plot information
        FileName motionInfFile, correctedPSDFile, rawPSDFile;
        ArrayDim aDim;

        // For measuring times (both for whole process and for each level of the pyramid)
        clock_t tStart, tStart2;

#ifdef GPU
        // Matrix that we required in GPU part
        GpuMat d_flowx, d_flowy, d_dest;
        GpuMat d_avgcurr, d_preimg, d_mapx, d_mapy;
#endif

        // Matrix required by Opencv
        Mat flowx, flowy, mapx, mapy, flow,dest;
        Mat flowxPre, flowyPre, flowxInBet, flowyInBet;// Using for computing the plot information
        Mat avgcurr, avgstep, preimg, preimg8, avgcurr8;
        Mat planes[] = {flowx, flowy};
        Scalar meanx, meany;
        Scalar stddevx, stddevy;

        int imagenum, cnt = 2, div = 0;
        int h, w, idx, levelNum, levelCounter = 1;

        motionInfFile = foname.replaceExtension("xmd");
        movieStack.read(fname,HEADER);
        movieStack.getDimensions(aDim);
        imagenum = aDim.ndim;
        h = aDim.ydim;
        w = aDim.xdim;


#ifdef GPU

        // Object for optical flow
        FarnebackOpticalFlow d_calc;
        gpu::setDevice(gpuDevice);

        // Initialize the parameters for optical flow structure
        d_calc.numLevels=6;
        d_calc.pyrScale=0.5;
        d_calc.fastPyramids=true;
        d_calc.winSize=winSize;
        d_calc.numIters=1;
        d_calc.polyN=5;
        d_calc.polySigma=1.1;
        d_calc.flags=0;
#endif
        // Initialize variables with zero
        mapx=cv::Mat::zeros(h, w,CV_32FC1);
        mapy=cv::Mat::zeros(h, w,CV_32FC1);

        tStart2=clock();

        // Compute the average of the whole stack
        fstFrame++; // Just to adapt to Li algorithm
        lstFrame++; // Just to adapt to Li algorithm
        if (lstFrame>=imagenum || lstFrame==1)
            lstFrame = imagenum;
        imagenum -= (imagenum-lstFrame) + (fstFrame-1);
        levelNum = sqrt(double(imagenum));
        computeAvg(fname, fstFrame, lstFrame, avgCurr);
        // if the user want to save the PSD
        if (psd)
        {
            II() = avgCurr;
            II.write(foname);
            rawPSDFile = fname.removeAllExtensions()+"_raw";
            String args=formatString("--micrograph %s --oroot %s --dont_estimate_ctf --pieceDim 400 --overlap 0.7",
                                     foname.c_str(), rawPSDFile.c_str());
            String cmd=(String)" xmipp_ctf_estimate_from_micrograph "+args;
            std::cerr<<"Computing the raw FFT"<<std::endl;
            if (system(cmd.c_str())==-1)
                REPORT_ERROR(ERR_UNCLASSIFIED,"Cannot open shell");
            foname.deleteFile();
        }
        if(doAverage)
        {
            II() = avgCurr;
            II.write(foname);
            return 0;
        }
        cout<<"Frames "<<fstFrame<<" to "<<lstFrame<<" under processing ..."<<std::endl;

        while (div!=1)
        {
            div = int(imagenum/cnt);
            // avgStep to hold the sum of aligned frames of each group at each step
            avgStep.initZeros(h, w);
            cout<<"Level "<<levelCounter<<"/"<<levelNum<<" of the pyramid is under processing"<<std::endl;
            // Compute time for each level
            tStart = clock();
            idx = 0;

            // Check if we are in the final step
            if (div==1)
                cnt = imagenum;

            for (int i=0;i<cnt;i++)
            {
                //Just compute the average in the last step
                if (div==1)
                {
                    movieStack.readMapped(fname,i+1);
                    movieStack().getImage(preImg);
                }
                else
                {
                    if (i==cnt-1)
                        computeAvg(fname, i*div+fstFrame, lstFrame, preImg);
                    else
                        computeAvg(fname, i*div+fstFrame, (i+1)*div+fstFrame-1, preImg);
                }

                xmipp2Opencv(avgCurr, avgcurr);
                xmipp2Opencv(preImg, preimg);

                // Note: we should use the OpenCV conversion to use it in optical flow
                convert2Uint8(avgcurr,avgcurr8);
                convert2Uint8(preimg,preimg8);
#ifdef GPU

                d_avgcurr.upload(avgcurr8);
                d_preimg.upload(preimg8);

                d_calc(d_avgcurr, d_preimg, d_flowx, d_flowy);
                d_flowx.download(flowx);
                d_flowy.download(flowy);

                d_avgcurr.release();
                d_preimg.release();
                d_flowx.release();
                d_flowy.release();
#else

                calcOpticalFlowFarneback(avgcurr8, preimg8, flow, 0.5, 6, winSize, 1, 5, 1.1, 0);
                split(flow, planes);
                flowx = planes[0];
                flowy = planes[1];
#endif

                // Save the flows if we are in the last step
                if (div==1)
                {
                    if (i > 0)
                    {
                        flowxInBet = flowx - flowxPre;
                        flowyInBet = flowy - flowyPre;
                        cv::meanStdDev(flowxInBet,meanx,stddevx);
                        cv::meanStdDev(flowyInBet,meany,stddevy);
                        size_t id=MD.addObject();
                        MD.setValue(MDL_OPTICALFLOW_MEANX, double(meanx.val[0]), id);
                        MD.setValue(MDL_OPTICALFLOW_MEANY, double(meany.val[0]), id);
                        MD.setValue(MDL_OPTICALFLOW_STDX, double(stddevx.val[0]), id);
                        MD.setValue(MDL_OPTICALFLOW_STDY, double(stddevy.val[0]), id);
                        MD.write(motionInfFile, MD_APPEND);
                    }
                    flowxPre = flowx.clone();
                    flowyPre = flowy.clone();
                }

                flowx.convertTo(mapx, CV_32FC1);
                flowy.convertTo(mapy, CV_32FC1);

                for( int row = 0; row < mapx.rows; row++ )
                    for( int col = 0; col < mapx.cols; col++ )
                    {
                        mapx.at<float>(row,col) += (float)col;
                        mapy.at<float>(row,col) += (float)row;

                    }
#ifdef GPU

                {
                    d_mapx.upload(mapx);
                    d_mapy.upload(mapy);
                    d_preimg.upload(preimg);
                    gpu::remap(d_preimg,d_dest,d_mapx,d_mapy,INTER_CUBIC);
                    d_dest.download(dest);

                    d_dest.release();
                    d_preimg.release();
                    d_mapx.release();
                    d_mapy.release();
                }
#else
                remap(preimg, dest, mapx, mapy, INTER_CUBIC);
#endif

                opencv2Xmipp(dest, mappedImg);
                avgStep += mappedImg;
            }
            avgCurr =  avgStep/cnt;

            cout<<"Processing level "<<levelCounter<<"/"<<levelNum<<" has been finished"<<std::endl;
            printf("Processing time: %.2fs\n", (double)(clock() - tStart)/CLOCKS_PER_SEC);
            cnt = cnt * 2;
            levelCounter ++;
        }
        II() = avgCurr;
        II.write(foname);
        printf("Total Processing time: %.2fs\n", (double)(clock() - tStart2)/CLOCKS_PER_SEC);
        if (psd)
        {
            Image<double> psdCorr, psdRaw;
            MultidimArray<double> psdCorrArr, psdRawArr;
            correctedPSDFile = fname.removeAllExtensions()+"_corrected";
            String args=formatString("--micrograph %s --oroot %s --dont_estimate_ctf --pieceDim 400 --overlap 0.7",
                                     foname.c_str(), correctedPSDFile.c_str());
            String cmd=(String)" xmipp_ctf_estimate_from_micrograph "+args;
            std::cerr<<"Computing the corrected FFT"<<std::endl;
            if (system(cmd.c_str())==-1)
                REPORT_ERROR(ERR_UNCLASSIFIED,"Cannot open shell");
            psdRaw.read(rawPSDFile+".psd");
            psdCorr.read(correctedPSDFile+".psd");
            psdCorrArr=psdCorr();
            psdRawArr=psdRaw();
            for (size_t i=0;i<400;i++)
            	for (size_t j=0;j<200;j++)
            		DIRECT_A2D_ELEM(psdCorrArr,i,j)=DIRECT_A2D_ELEM(psdRawArr,i,j);
            psdCorr()=psdCorrArr;
            psdCorr.write(correctedPSDFile+".psd");
            //rawPSDFile.deleteFile();
        }
        return 0;
    }
};

int main(int argc, char *argv[])
{
    ProgOpticalAligment prm;
    prm.read(argc,argv);
    return prm.tryRun();
}
