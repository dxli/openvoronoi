/*  
 *  Copyright 2010-2011 Anders Wallin (anders.e.e.wallin "at" gmail.com)
 *  
 *  This file is part of OpenVoronoi.
 *
 *  OpenCAMlib is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  OpenCAMlib is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with OpenCAMlib.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "checker.hpp"
#include "voronoidiagram.hpp"

namespace ovd {

    
/// sanity-check for the diagram, calls other sanity-check functions
bool VoronoiDiagramChecker::is_valid() {
    return  (   all_faces_ok() && 
                vertex_degree_ok() &&
                face_count_equals_generator_count()
            );

}
    
    
    
/// check that number of faces equals the number of generators
bool VoronoiDiagramChecker::face_count_equals_generator_count() {
    // Euler formula for planar graphs
    // v - e + f = 2
    // in a half-edge diagram all edges occur twice, so:
    // f = 2-v+e
    //int vertex_count = hedi::num_vertices(vd->g);
    /*int vertex_count = 0;
    BOOST_FOREACH( HEVertex v, hedi::vertices( vd->g ) ) {
        if ( vd->g[v].type == NORMAL )
            vertex_count++;
    }
    int face_count = (vertex_count- 4)/2 + 3; // degree three graph
    //int face_count = hed.num_faces();
    if (face_count != vd->gen_count) {
        std::cout << " face_count_equals_generator_count() ERROR:\n";
        std::cout << " num_vertices = " << vertex_count << "\n";
        std::cout << " gen_count = " << vd->gen_count << "\n";
        std::cout << " face_count = " << face_count << "\n";
    }
    return ( face_count == vd->gen_count );
    * */
    return true;
}

    
    
/// the diagram should be of degree three (at least with point generators)
bool VoronoiDiagramChecker::vertex_degree_ok() {
    // the outermost init() vertices have special degree, all others == 6
    BOOST_FOREACH(HEVertex v, vd->g.vertices() ) {
        
        if ( vd->g.degree(v) != VoronoiVertex::expected_degree[ vd->g[v].type ] ) {
            std::cout << " vertex_degree_ok() ERROR\n";
            std::cout << " vertex " << vd->g[v].index << " type = " << vd->g[v].type << "\n";
            std::cout << " vertex degree = " << vd->g.degree(v) << "\n";
            std::cout << " expected degree = " << VoronoiVertex::expected_degree[ vd->g[v].type ]  << "\n";
            return false;
        }
    }
    return true;
}
    
    
/// traverse the incident faces and check next-pointers
bool VoronoiDiagramChecker::allIncidentFacesOK() {
    // all incident faces should pass the sanity-check
    BOOST_FOREACH( HEFace f, vd->incident_faces ) {
        if ( !faceVerticesConnected(  f, IN ) )
            return false; // IN vertices should be connected
        if ( !faceVerticesConnected(  f, OUT ) )  // OUT vertices should be connected
            return false;
        if ( !noUndecidedInFace( f ) )            // no UNDECIDED vertices should remain
            return false;
    }
    return true;
}
    
    
/// check that all vertices in the input vector are of type IN
bool VoronoiDiagramChecker::all_in( const VertexVector& q) {
    BOOST_FOREACH( HEVertex v, q) {
        if ( vd->g[v].status != IN )
            return false;
    }
    return true;
}

/// check that no undecided vertices remain in the face
bool  VoronoiDiagramChecker::noUndecidedInFace(  HEFace f ) {
    VertexVector face_verts = vd->g.face_vertices(f);
    BOOST_FOREACH( HEVertex v, face_verts ) {
        if ( vd->g[v].status == UNDECIDED )
            return false;
    }
    return true;
}
        
// check that for HEFace f the vertices TYPE are connected
bool VoronoiDiagramChecker::faceVerticesConnected(  HEFace f, VoronoiVertexStatus Vtype ) {
    VertexVector face_verts = vd->g.face_vertices(f);
    VertexVector type_verts;
    BOOST_FOREACH( HEVertex v, face_verts ) {
        if ( vd->g[v].status == Vtype )
            type_verts.push_back(v); // build a vector of all Vtype vertices
    }
    assert( !type_verts.empty() );
    if (type_verts.size()==1) // set of 1 is allways connected
        return true;
    
    // check that type_verts are connected
    HEEdge currentEdge = vd->g[f].edge;
    HEVertex endVertex = vd->g.source(currentEdge); // stop when target here
    EdgeVector startEdges;
    bool done = false;
    while (!done) { 
        HEVertex src = vd->g.source( currentEdge );
        HEVertex trg = vd->g.target( currentEdge );
        if ( vd->g[src].status != Vtype ) { // seach ?? - Vtype
            if ( vd->g[trg].status == Vtype ) {
                // we have found ?? - Vtype
                startEdges.push_back( currentEdge );
            }
        }
        currentEdge = vd->g[currentEdge].next;
        if ( trg == endVertex ) {
            done = true;
        }
    }
    assert( !startEdges.empty() );
    if ( startEdges.size() != 1 ) // when the Vtype vertices are connected, there is exactly one startEdge
        return false;
    else 
        return true;
}

// sanity check: IN-vertices for each face should be connected
bool VoronoiDiagramChecker::incidentFaceVerticesConnected( VoronoiVertexStatus  ) {    
    BOOST_FOREACH( HEFace f1, vd->incident_faces ) {
        if ( !faceVerticesConnected(  f1, IN ) ) {
            std::cout << " VoronoiDiagramChecker::incidentFaceVerticesConnected() ERROR, IN-vertices not connected.\n";
            std::cout << " printing all incident faces for debug: \n";
            BOOST_FOREACH( HEFace f2, vd->incident_faces ) {
                vd->print_face( f2 );
            } 
            return false;
        }
    }
    return true;
}

bool VoronoiDiagramChecker::in_circle_is_negative(  const Point& p, HEVertex minimalVertex ) {
    double minimumH = vd->g[minimalVertex].in_circle(p);
    
    if (!(minimumH <= 0) ) {
        std::cout << " inCircle_is_negative() WARNING\n";
        std::cout << " WARNING: searching for seed when inserting " << p << " \n";
    //    std::cout << " WARNING: closest face is " << f << " with generator " << vd->g[f].generator << " \n";
        std::cout << " WARNING: minimal vd-vertex " << vd->g[minimalVertex].index << " has inCircle= " << minimumH  << "\n";
    }
    
    return (minimumH <= 0 );
}

// check that all faces are ok
bool VoronoiDiagramChecker::all_faces_ok() {
    for(HEFace f=0;f< vd->g.num_faces() ; f++ ) {
        if (!face_ok(f)) {
            std::cout << " all_faces_ok() ERROR: f= " << f << "\n";
            vd->print_face(f);
            return false;
        }
    }
    return true;
}

bool VoronoiDiagramChecker::face_ok(HEFace f) {
    HEEdge current_edge = vd->g[f].edge;
    HEEdge start_edge= current_edge;
    double k = vd->g[current_edge].k;
    assert( (k==1) || (k==-1) );
    if ( vd->g[f].site->isPoint() ) {
        if ( !(k==1) )
            return false;
    }
    int n=0;
    do {
        if (vd->g[current_edge].k != k ) // all edges should have the same k-value
            return false;
        if ( !current_face_equals_next_face(current_edge) ) // all edges should have the same face
            return false;
        
        if ( !check_edge(current_edge) ) {
            std::cout << " VoronoiDiagramChecker::face_ok() f= " << f << " check_edge ERROR\n";
            std::cout << " edge: " << vd->g[ vd->g.source(current_edge)].index << " t=" << vd->g[ vd->g.source(current_edge)].type; 
            std::cout << " - ";
            std::cout <<  vd->g[ vd->g.target(current_edge)].index << " t=" << vd->g[ vd->g.target(current_edge) ].type << "\n"; 
            HEEdge twin = vd->g[current_edge].twin;
            std::cout << " twin: " << vd->g[ vd->g.source(twin)].index  << " t=" << vd->g[ vd->g.source(twin)].type; 
            std::cout << " - ";
            std::cout <<  vd->g[ vd->g.target(twin)].index << " t=" << vd->g[ vd->g.target(twin) ].type << "\n"; 
            //std::cout << " twin: " << vd->g[ vd->g.source(twin)].index << " - " <<  vd->g[ vd->g.target(twin)].index << "\n";
            
            std::cout << " edge-type= " << vd->g[current_edge].type << "\n";

            return false;
        }
        
        current_edge = vd->g[current_edge].next; 
        n++;
        assert( n < 10000 ); // reasonable max
    } while( current_edge != start_edge);
    //std::cout << " face ok, edges=" << n-1 << "\n";
    return true;
}

bool VoronoiDiagramChecker::current_face_equals_next_face( HEEdge e) {
    if ( vd->g[e].face !=  vd->g[ vd->g[e].next ].face) {
        std::cout << " current_face_equals_next_face() ERROR.\n";
        std::cout << "   current.face = " << vd->g[e].face << " IS NOT next_face = " << vd->g[ vd->g[e].next ].face << std::endl;
        HEVertex c_trg = vd->g.target( e );
        HEVertex c_src = vd->g.source( e );
        HEVertex n_trg = vd->g.target( vd->g[e].next );
        HEVertex n_src = vd->g.source( vd->g[e].next );
        
        std::cout << "   current_edge = " << vd->g[c_src].index << " - " << vd->g[c_trg].index << " type=" << vd->g[e].type << " face=" << vd->g[e].face  <<"\n";
        std::cout << "   next_edge = " << vd->g[n_src].index << " - " << vd->g[n_trg].index << " type=" << vd->g[ vd->g[e].next ].type << " face="<< vd->g[ vd->g[e].next ].face << "\n";
        
        vd->print_face( vd->g[e].face );
        vd->print_face( vd->g[ vd->g[e].next ].face );
        
        std::cout << " printing all incident faces for debug: \n";
        BOOST_FOREACH( HEFace f, vd->incident_faces ) {
            vd->print_face( f );
        } 
        return false;
    }
    return true;
}

bool VoronoiDiagramChecker::check_edge(HEEdge e) const {
    HEVertex src = vd->g.source(e);
    HEVertex trg = vd->g.target(e);
    HEEdge twine = vd->g[e].twin;

    if (twine == HEEdge() ) {
        return true;
    } else if ( !( e == vd->g[twine].twin ) ) {
        std::cout << " VoronoiDiagramChecker::check_edge() twinning error!\n";
        return false;
    }
    
    HEVertex tw_src = vd->g.source(twine);
    HEVertex tw_trg = vd->g.target(twine);
    //std::cout << (src==tw_trg) << " && " << (trg==tw_src) << "\n";
    if ( !((src==tw_trg) && (trg==tw_src)) ) {
        std::cout << "VoronoiDiagramChecker::check_edge() ERROR: \n";
        std::cout << "      edge: " << vd->g[src].index << "("<< vd->g[src].type << ")";
        std::cout << " - " << vd->g[trg].index << "("<< vd->g[trg].type << ")" << "\n";
        //std::cout << "      twin: " << vd->g[tw_src].index << " - " << vd->g[tw_src].index << "\n";
        std::cout << "      edge: " << e << "\n";
        std::cout << "      twin: " << twine << "\n";
        std::cout << "      edge: " << src << " - " << trg << "\n";
        std::cout << "      twin: " << tw_src << " - " << tw_trg << "\n";

    }
    return ( (src==tw_trg) && (trg==tw_src) );
}
                 
/* OLD CODE NOT USED ANYMORE
int VoronoiDiagram::outVertexCount(HEFace f) {
    int outCount = 0;
    VertexVector face_verts = hedi::face_vertices(f, g);
    BOOST_FOREACH( HEVertex v, face_verts ) {
        if (g[v].status == OUT )
            ++outCount;
    }
    return outCount;
}*/


} // end namespace
