import parmed as pmd
import unyt as u

from topology.core.topology import Topology
from topology.core.site import Site
from topology.core.atom_type import AtomType
from topology.core.box import Box

def from_parmed(structure):
    msg = ("Provided argument that is not a Parmed Structure")
    assert isinstance(structure, pmd.Structure), msg

    top = Topology(name=structure.title)
    map = dict()
    for atom in structure.atoms:
        atom_type = AtomType(name=atom.atom_type.name, 
                charge=atom.atom_type.charge * u.elementary_charge, 
                parameters={'sigma': atom.sigma * u.angstrom, 
                    'epsilon': atom.epsilon * 1000 * u.calorie / u.mol})
        site = Site(name=atom.name, 
                charge=atom.charge * u.elementary_charge,
                position=[atom.xx, atom.xy, atom.xz]*u.angstrom,
                atom_type=atom_type)
        map[atom] = site
        top.add_site(site)

    if structure.box:
        # This is if we choose for topology to have abox
        top.box = Box(structure.box[0:3]*u.angstrom, angles=structure.box[4:7])

    for bond in structure.bonds:
        bond_params = {'k': bond.type.k * 1000 * u.calorie / (u.angstrom**2 * u.mol),
                        'req': bond.type.req * u.angstrom}
        # Need to modify `Connection` to have knowledge of bond parameters
        if map[bond.atom2] not in map[bond.atom1].connections:
            map[bond.atom1].add_connection(map[bond.atom2])
        if map[bond.atom1] not in map[bond.atom2].connections:
            map[bond.atom2].add_connection(map[bond.atom1])

        

    # TODO: Angles
    # TODO: Dihedrals

    top.update_connection_list()

    return top

