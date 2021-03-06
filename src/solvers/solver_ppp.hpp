/*  
 *  Copyright 2010-2011 Anders Wallin (anders.e.e.wallin "at" gmail.com)
 * 
 *  Idea and code for point/line/arc voronoi-vertex positioning code by
 *  Andy Payne, andy "at" payne "dot" org, November, 2010
 *  see: http://www.payne.org/index.php/Calculating_Voronoi_Nodes
 * 
 *  This file is part of OpenVoronoi.
 *
 *  OpenVoronoi is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  OpenVoronoi is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with OpenVoronoi.  If not, see <http://www.gnu.org/licenses/>.
*/

#ifndef PPP_SOLVER_HPP
#define PPP_SOLVER_HPP

#include <vector>
#include <cassert>

#include "solver.hpp"
#include "common/numeric.hpp"

using namespace ovd::numeric; // sq() chop()

namespace ovd {

template<class Scalar>
struct scalar_pt {
    scalar_pt<Scalar>() : x(0), y(0) {}
    scalar_pt<Scalar>(Scalar xi, Scalar yi) : x(xi), y(yi) {}
    
    Scalar x;
    Scalar y;
    double getx() {
        return x;
    }
    double gety() {
        return y;
    }
    
    scalar_pt<Scalar> &operator=(const Point& p) {
        x = p.x;
        y = p.y;
        return *this;
    }
};

// with the qd_real number-type we need to_double() to get the solution coordinates as double type.

template<>
struct scalar_pt<qd_real> {
    scalar_pt<qd_real>() : x(qd_real(0)), y(qd_real(0)) {}
    scalar_pt<qd_real>(qd_real xi, qd_real yi) : x(xi), y(yi) {}
    
    qd_real x;
    qd_real y;
    double getx() {
        return to_double(x);
    }
    double gety() {
        return to_double(y);
    }
    scalar_pt<qd_real> &operator=(const Point& p) {
        x = p.x;
        y = p.y;
        return *this;
    }
};


/// point-point-point vertex positioner based on Sugihara & Iri paper
template<class Scalar>
class PPPSolver : public Solver {
public:

int solve( Site* s1, Site* s2, Site* s3,  std::vector<Solution>& slns ) {
    assert( s1->isPoint() && s2->isPoint() && s3->isPoint() );
    Point pi = s1->position();
    Point pj = s2->position();
    Point pk = s3->position();
    
    if ( pi.is_right(pj,pk) ) 
        std::swap(pi,pj);
    assert( !pi.is_right(pj,pk) );
    // 2) point pk should have the largest angle. largest angle is opposite longest side.
    double longest_side = (pi - pj).norm();
    while (  ((pj - pk).norm() > longest_side) || (((pi - pk).norm() > longest_side)) ) { 
        std::swap(pi,pj); // cyclic rotation of points until pk is opposite the longest side pi-pj
        std::swap(pi,pk);  
        longest_side = (pi - pj).norm();
    }
    assert( !pi.is_right(pj,pk) );
    assert( (pi - pj).norm() >=  (pj - pk).norm() );
    assert( (pi - pj).norm() >=  (pk - pi).norm() );
    
    // we now convert to a higher precision number-type to do the calculations
    scalar_pt<Scalar> spi,spj,spk;
    spi = pi;
    spj = pj;
    spk = pk;
    Scalar J2 = (spi.y-spk.y)*( sq(spj.x-spk.x)+sq(spj.y-spk.y) )/2.0 - 
                (spj.y-spk.y)*( sq(spi.x-spk.x)+sq(spi.y-spk.y) )/2.0;
    Scalar J3 = (spi.x-spk.x)*( sq(spj.x-spk.x)+sq(spj.y-spk.y) )/2.0 - 
                (spj.x-spk.x)*( sq(spi.x-spk.x)+sq(spi.y-spk.y) )/2.0;
    Scalar J4 = (spi.x-spk.x)*(spj.y-spk.y) - (spj.x-spk.x)*(spi.y-spk.y);
    assert( J4 != 0.0 );
    if (J4==0.0)
        std::cout << " PPPSolver: Warning divide-by-zero!!\n";
    scalar_pt<Scalar> pt( -J2/J4 + spk.x, J3/J4 + spk.y );
    Point sln_pt = Point( pt.getx(), pt.gety());
    double dist = (sln_pt-pi).norm();
    slns.push_back( Solution(  sln_pt , dist , +1) );
    return 1;
}

};


} // ovd
#endif
