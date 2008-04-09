/*
 * Copyright (c) 2003, 2006 Matteo Frigo
 * Copyright (c) 2003, 2006 Massachusetts Institute of Technology
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
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 */

/* This file was automatically generated --- DO NOT EDIT */
/* Generated on Sun Jul  2 16:15:30 EDT 2006 */

#include "codelet-rdft.h"

#ifdef HAVE_FMA

/* Generated by: ../../../genfft/gen_hc2r -fma -reorder-insns -schedule-for-pipeline -compact -variables 4 -pipeline-latency 4 -sign 1 -n 8 -name hc2r_8 -include hc2r.h */

/*
 * This function contains 20 FP additions, 12 FP multiplications,
 * (or, 8 additions, 0 multiplications, 12 fused multiply/add),
 * 19 stack variables, and 16 memory accesses
 */
/*
 * Generator Id's : 
 * $Id: algsimp.ml,v 1.9 2006-02-12 23:34:12 athena Exp $
 * $Id: fft.ml,v 1.4 2006-01-05 03:04:27 stevenj Exp $
 * $Id: gen_hc2r.ml,v 1.19 2006-02-12 23:34:12 athena Exp $
 */

#include "hc2r.h"

static void hc2r_8(const R *ri, const R *ii, R *O, stride ris, stride iis, stride os, INT v, INT ivs, INT ovs)
{
     DK(KP1_414213562, +1.414213562373095048801688724209698078569671875);
     DK(KP2_000000000, +2.000000000000000000000000000000000000000000000);
     INT i;
     for (i = v; i > 0; i = i - 1, ri = ri + ivs, ii = ii + ivs, O = O + ovs, MAKE_VOLATILE_STRIDE(ris), MAKE_VOLATILE_STRIDE(iis), MAKE_VOLATILE_STRIDE(os)) {
	  E Th, Tb, Tg, Ti;
	  {
	       E T4, Ta, Td, T9, T3, Tc, T8, Te;
	       T4 = ri[WS(ris, 2)];
	       Ta = ii[WS(iis, 2)];
	       {
		    E T1, T2, T6, T7;
		    T1 = ri[0];
		    T2 = ri[WS(ris, 4)];
		    T6 = ri[WS(ris, 1)];
		    T7 = ri[WS(ris, 3)];
		    Td = ii[WS(iis, 1)];
		    T9 = T1 - T2;
		    T3 = T1 + T2;
		    Tc = T6 - T7;
		    T8 = T6 + T7;
		    Te = ii[WS(iis, 3)];
	       }
	       {
		    E Tj, T5, Tk, Tf;
		    Tj = FNMS(KP2_000000000, T4, T3);
		    T5 = FMA(KP2_000000000, T4, T3);
		    Th = FMA(KP2_000000000, Ta, T9);
		    Tb = FNMS(KP2_000000000, Ta, T9);
		    Tk = Td - Te;
		    Tf = Td + Te;
		    O[0] = FMA(KP2_000000000, T8, T5);
		    O[WS(os, 4)] = FNMS(KP2_000000000, T8, T5);
		    O[WS(os, 6)] = FMA(KP2_000000000, Tk, Tj);
		    O[WS(os, 2)] = FNMS(KP2_000000000, Tk, Tj);
		    Tg = Tc - Tf;
		    Ti = Tc + Tf;
	       }
	  }
	  O[WS(os, 1)] = FMA(KP1_414213562, Tg, Tb);
	  O[WS(os, 5)] = FNMS(KP1_414213562, Tg, Tb);
	  O[WS(os, 7)] = FMA(KP1_414213562, Ti, Th);
	  O[WS(os, 3)] = FNMS(KP1_414213562, Ti, Th);
     }
}

static const khc2r_desc desc = { 8, "hc2r_8", {8, 0, 12, 0}, &GENUS, 0, 0, 0, 0, 0 };

void X(codelet_hc2r_8) (planner *p) {
     X(khc2r_register) (p, hc2r_8, &desc);
}

#else				/* HAVE_FMA */

/* Generated by: ../../../genfft/gen_hc2r -compact -variables 4 -pipeline-latency 4 -sign 1 -n 8 -name hc2r_8 -include hc2r.h */

/*
 * This function contains 20 FP additions, 6 FP multiplications,
 * (or, 20 additions, 6 multiplications, 0 fused multiply/add),
 * 21 stack variables, and 16 memory accesses
 */
/*
 * Generator Id's : 
 * $Id: algsimp.ml,v 1.9 2006-02-12 23:34:12 athena Exp $
 * $Id: fft.ml,v 1.4 2006-01-05 03:04:27 stevenj Exp $
 * $Id: gen_hc2r.ml,v 1.19 2006-02-12 23:34:12 athena Exp $
 */

#include "hc2r.h"

static void hc2r_8(const R *ri, const R *ii, R *O, stride ris, stride iis, stride os, INT v, INT ivs, INT ovs)
{
     DK(KP1_414213562, +1.414213562373095048801688724209698078569671875);
     DK(KP2_000000000, +2.000000000000000000000000000000000000000000000);
     INT i;
     for (i = v; i > 0; i = i - 1, ri = ri + ivs, ii = ii + ivs, O = O + ovs, MAKE_VOLATILE_STRIDE(ris), MAKE_VOLATILE_STRIDE(iis), MAKE_VOLATILE_STRIDE(os)) {
	  E T5, Tg, T3, Te, T9, Ti, Td, Tj, T6, Ta;
	  {
	       E T4, Tf, T1, T2;
	       T4 = ri[WS(ris, 2)];
	       T5 = KP2_000000000 * T4;
	       Tf = ii[WS(iis, 2)];
	       Tg = KP2_000000000 * Tf;
	       T1 = ri[0];
	       T2 = ri[WS(ris, 4)];
	       T3 = T1 + T2;
	       Te = T1 - T2;
	       {
		    E T7, T8, Tb, Tc;
		    T7 = ri[WS(ris, 1)];
		    T8 = ri[WS(ris, 3)];
		    T9 = KP2_000000000 * (T7 + T8);
		    Ti = T7 - T8;
		    Tb = ii[WS(iis, 1)];
		    Tc = ii[WS(iis, 3)];
		    Td = KP2_000000000 * (Tb - Tc);
		    Tj = Tb + Tc;
	       }
	  }
	  T6 = T3 + T5;
	  O[WS(os, 4)] = T6 - T9;
	  O[0] = T6 + T9;
	  Ta = T3 - T5;
	  O[WS(os, 2)] = Ta - Td;
	  O[WS(os, 6)] = Ta + Td;
	  {
	       E Th, Tk, Tl, Tm;
	       Th = Te - Tg;
	       Tk = KP1_414213562 * (Ti - Tj);
	       O[WS(os, 5)] = Th - Tk;
	       O[WS(os, 1)] = Th + Tk;
	       Tl = Te + Tg;
	       Tm = KP1_414213562 * (Ti + Tj);
	       O[WS(os, 3)] = Tl - Tm;
	       O[WS(os, 7)] = Tl + Tm;
	  }
     }
}

static const khc2r_desc desc = { 8, "hc2r_8", {20, 6, 0, 0}, &GENUS, 0, 0, 0, 0, 0 };

void X(codelet_hc2r_8) (planner *p) {
     X(khc2r_register) (p, hc2r_8, &desc);
}

#endif				/* HAVE_FMA */
