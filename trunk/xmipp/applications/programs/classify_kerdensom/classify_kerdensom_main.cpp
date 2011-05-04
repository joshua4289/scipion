/***************************************************************************
 *
 * Authors:     Alberto Pascual Montano (pascual@cnb.csic.es)
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

// To avoid problems with long template names
#pragma warning(disable:4786)

#include <fstream>

#include <data/program.h>
#include <classification/tstudent_kerdensom.h>
#include <classification/gaussian_kerdensom.h>

/* Parameters class ======================================================= */
class ProgKenderSOM: public XmippProgram
{
public:
    /* Input Parameters ======================================================== */
    FileName       fn_in;        // input file
    FileName       fn_out;       // output file
    FileName       tmpN;         // Temporary variable
    double         eps;          // Stopping criteria
    unsigned       iter;         // Iteration number
    bool           norm;         // Normalize?
    int            xdim;         // X-dimension (-->)
    int            ydim;         // Y-dimension
    double         reg0;         // Initial reg
    double         reg1;         // Final reg
    int            df;           // Degrees of freedom
    std::string    layout;       // layout (Topology)
    unsigned       annSteps;     // Deterministic Annealing steps
    bool           gaussian;     // Gaussian Kernel
    bool           tStudent;     // tStudent Kernel
public:
    // Define parameters
    void defineParams()
    {
        addUsageLine("Purpose: Kernel Density Estimator Self-Organizing Map");
        addParamsLine("  -i <file_in>                : Input data file (plain data)");
        addParamsLine(" [-o <file_out>]              : Base name for output data files");
        addParamsLine(" [--xdim <Hdimension=10>]     : Horizontal size of the map");
        addParamsLine(" [--ydim <Vdimension=5>]      : Vertical size of the map");
        addParamsLine(" [--topology <topology=RECT>] : Lattice topology");
        addParamsLine("    where <topology> RECT HEXA");
        addParamsLine(" [--steps <steps=10>]         : Deterministic annealing steps");
        addParamsLine(" [--reg0  <Initial_reg=1000>] : Initial smoothness factor");
        addParamsLine(" [--reg1  <Final_reg=100>]    : Final  smoothness factor");
        addParamsLine(" [--kernel <kernel=gaussian>] : Kernel function");
        addParamsLine("    where <kernel> gaussian tstudent");
        addParamsLine(" [--df <df=3>]                : t-Student degrees of freedom");
        addParamsLine(" [--ain <algorithmFile>]      : algorithm input file");
        addParamsLine(" [--eps <epsilon=1e-7>]       : Stopping criteria");
        addParamsLine(" [--iter <N=200>]             : Number of iterations");
        addParamsLine(" [--norm]                     : Normalize training data");
    }

    // Read parameters
    void readParams()
    {
        fn_in = getParam("-i");
        if (checkParam("-o"))
            fn_out=getParam("-o");
        ydim = getIntParam("--ydim");
        xdim = getIntParam("--xdim");
        layout = getParam("--topology");
        std::string kernel=getParam("--kernel");
        if (kernel=="gaussian")
        {
            gaussian = true;
            tStudent = false;
        }
        else if (kernel=="tstudent")
        {
            gaussian = false;
            tStudent = true;
        }
        reg0 = getDoubleParam("--reg0");
        reg1 = getDoubleParam("--reg1");
        df = getIntParam("--df");
        eps = getDoubleParam("--eps");
        iter = getIntParam("--iter");
        norm = checkParam("--norm");
        annSteps = getIntParam("--steps");

        // Some checks
        if (iter < 1)
            REPORT_ERROR(ERR_ARG_INCORRECT,"iter must be > 1");

        if ((reg0 <= reg1) && (reg0 != 0) && (annSteps > 1))
            REPORT_ERROR(ERR_ARG_INCORRECT,"reg0 must be > reg1");
        if (reg0 == 0)
            annSteps = 0;
        if (reg0 < 0)
            REPORT_ERROR(ERR_ARG_INCORRECT,"reg0 must be > 0");
        if (reg1 < 0)
            REPORT_ERROR(ERR_ARG_INCORRECT,"reg1 must be > 0");
        if (xdim < 1)
            REPORT_ERROR(ERR_ARG_INCORRECT,"xdim must be >= 1");
        if (ydim < 1)
            REPORT_ERROR(ERR_ARG_INCORRECT,"ydim must be >= 1");
        if (df < 2)
            REPORT_ERROR(ERR_ARG_INCORRECT,"df must be > 1");
    }

    void show()
    {
        std::cout << "Input data file : " << fn_in << std::endl;
        std::cout << "Output file name : " << fn_out << std::endl;
        std::cout << "Horizontal dimension (Xdim) = " << xdim << std::endl;
        std::cout << "Vertical dimension (Ydim) = " << ydim << std::endl;
        if (layout == "HEXA")
            std::cout << "Hexagonal topology " << std::endl;
        else
            std::cout << "Rectangular topology " << std::endl;
        std::cout << "Initial smoothness factor (reg0) = " << reg0 << std::endl;
        std::cout << "Final smoothness factor (reg1) = " << reg1 << std::endl;
        if (gaussian)
            std::cout << "Gaussian Kernel function " << std::endl;
        else
        {
            std::cout << "t-Student Kernel function" << std::endl;
            std::cout << "Degrees of freedom (df) = " << df << std::endl;
        }
        std::cout << "Deterministic annealing steps = " << annSteps << std::endl;
        std::cout << "Total number of iterations = " << iter << std::endl;
        std::cout << "Stopping criteria (eps) = " << eps << std::endl;
        if (norm)
            std::cout << "Normalize input data" << std::endl;
        else
            std::cout << "Do not normalize input data " << std::endl;
    }

    // Run
    void run()
    {
        /* Open training vector ================================================= */
        ClassicTrainingVectors ts(0, true);
        std::cout << std::endl << "Reading input data file " << fn_in << "....." << std::endl;
        ts.read(fn_in);

        /* Real stuff ============================================================== */
        if (norm)
        {
            std::cout << "Normalizing....." << std::endl;
            ts.normalize();        // Normalize input data
        }

        FuzzyMap *myMap = new FuzzyMap(layout, xdim, ydim, ts);

        KerDenSOM *thisSOM;
        if (gaussian)
            thisSOM = new GaussianKerDenSOM(reg0, reg1, annSteps, eps, iter);        // Creates KerDenSOM Algorithm
        else
            thisSOM = new TStudentKerDenSOM(reg0, reg1, annSteps, eps, iter, df);    // Creates KerDenSOM Algorithm

        TextualListener myListener;       // Define the listener class
        myListener.setVerbosity() = verbose;       // Set verbosity level
        thisSOM->setListener(&myListener);         // Set Listener
        thisSOM->train(*myMap, ts, fn_out);        // Train algorithm

        // Test algorithm
        double dist = thisSOM->test(*myMap, ts);
        std::cout << std::endl << "Quantization error : " <<  dist << std::endl;

        // Classifying
        std::cout << "Classifying....." << std::endl;
        myMap->classify(&ts);

        // Calibrating
        std::cout << "Calibrating....." << std::endl;
        myMap->calibrate(ts);

        /*******************************************************
            Saving all kind of Information
        *******************************************************/
        // Save map size
        MetaData MDkerdensom;
        size_t id=MDkerdensom.addObject();
        MDkerdensom.setValue(MDL_XSIZE,xdim,id);
        MDkerdensom.setValue(MDL_YSIZE,ydim,id);
        MDkerdensom.setValue(MDL_MAPTOPOLOGY,layout,id);
        MDkerdensom.write(formatString("KerDenSOM_Layout@%s",fn_out.c_str()),MD_APPEND);

        // save intracluster distance and number of vectors in each cluster
        MetaData MDsummary;
        for (unsigned i = 0; i < myMap->size(); i++)
        {
        	id=MDsummary.addObject();
        	MDsummary.setValue(MDL_REF,(int)i,id);
        	MDsummary.setValue(MDL_CLASSIFICATION_INTRACLASS_DISTANCE,myMap->aveDistances[i],id);
        	MDsummary.setValue(MDL_COUNT,myMap->classifSizeAt(i),id);
        }
        MDsummary.write(formatString("KerDenSOM_Cluster_Summary@%s",fn_out.c_str()),MD_APPEND);

        // assign data to clusters according to fuzzy threshold
        std::cout << "Saving neurons assigments ....." << std::endl;
        MetaData vectorContentIn;
        vectorContentIn.read(formatString("vectorContent@%s",fn_in.c_str()));
        FileName fn;
        std::vector<size_t> objIds;
        vectorContentIn.findObjects(objIds);
        for (unsigned i = 0; i < myMap->size(); i++)
        {
        	MetaData MD;
            for (int j = 0; j < myMap->classifAt(i).size(); j++)
            {
            	size_t order=myMap->classifAt(i)[j];
            	vectorContentIn.getValue(MDL_IMAGE,fn,objIds[order]);
            	MD.setValue(MDL_IMAGE,fn,MD.addObject());
            }
            if (MD.size()>0)
            	MD.write(formatString("cluster%06d@%s",i,fn_out.c_str()),MD_APPEND);
        }

        // Save code vectors
        if (norm)
        {
            std::cout << "Denormalizing code vectors....." << std::endl;
            myMap->unNormalize(ts.getNormalizationInfo()); // de-normalize codevectors
        }
        MetaData vectorHeaderIn, vectorHeaderOut, vectorContentOut;
        vectorHeaderIn.read(formatString("vectorHeader@%s",fn_in.c_str()));
        vectorHeaderOut.setColumnFormat(false);
        int size, vectorSize;
        size_t idIn=vectorHeaderIn.firstObject();
        size_t idOut=vectorHeaderOut.addObject();
        vectorHeaderIn.getValue(MDL_XSIZE,size,idIn);
        vectorHeaderOut.setValue(MDL_XSIZE,size,idOut);
        vectorHeaderIn.getValue(MDL_YSIZE,size,idIn);
        vectorHeaderOut.setValue(MDL_YSIZE,size,idOut);
        vectorHeaderIn.getValue(MDL_ZSIZE,size,idIn);
        vectorHeaderOut.setValue(MDL_ZSIZE,size,idOut);
        vectorHeaderOut.setValue(MDL_COUNT,myMap->size(),idOut);
        vectorHeaderIn.getValue(MDL_CLASSIFICATION_DATA_SIZE,vectorSize,idIn);
        vectorHeaderOut.setValue(MDL_CLASSIFICATION_DATA_SIZE,vectorSize,idOut);
        vectorHeaderOut.write(formatString("vectorHeader@%s",fn_out.c_str()),MD_APPEND);
        FileName fnOutRaw=fn_out+".raw";
        std::ofstream fhOutRaw(fnOutRaw.c_str(),std::ios::binary);
        if (!fhOutRaw)
            REPORT_ERROR(ERR_IO_NOWRITE,fnOutRaw);
        for (size_t i = 0; i < myMap->size(); i++)
        {
        	id=vectorContentOut.addObject();
        	vectorContentOut.setValue(MDL_IMAGE,formatString("cluster%06lu",i),id);
        	vectorContentOut.setValue(MDL_ORDER,i,id);
        	fhOutRaw.write((char*)&(myMap->theItems[i][0]),vectorSize*sizeof(float));
        }
        fhOutRaw.close();
        vectorContentOut.write(formatString("vectorContent@%s",fn_out.c_str()),MD_APPEND);

        std::cout << std::endl;

        delete myMap;
        delete thisSOM;
    }
};

/* Main function -============================================================= */
int main(int argc, char** argv)
{
    ProgKenderSOM prm;
    prm.read(argc,argv);
    return prm.tryRun();
}
