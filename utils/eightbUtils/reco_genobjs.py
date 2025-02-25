import vector
import awkward as ak

from ..hepUtils import *

mass_list = [
    "MX_700_MY_300",
    "MX_800_MY_300",
    "MX_800_MY_350",
    "MX_900_MY_300",
    "MX_900_MY_400",
    "MX_1000_MY_300",
    "MX_1000_MY_450",
    "MX_1200_MY_500"
]

quarklist = [
    f'{h}{y}_{b}'
    for y in ('Y1','Y2')
    for h in ('H1','H2')
    for b in ('b1','b2')
]

higgslist = [
    f'{h}{y}'
    for y in ('Y1','Y2')
    for h in ('H1','H2')
]

ylist = [
    f'{y}'
    for y in ('Y1','Y2')
]

scalarlist = ['X'] + ylist + higgslist
esmlist = ['X'] + ylist

def reco_genH(tree, higgs, use_regressed=True):
    b1_p4 = build_p4(tree, prefix=f'{higgs}_b1_recojet', use_regressed=use_regressed)
    b2_p4 = build_p4(tree, prefix=f'{higgs}_b2_recojet', use_regressed=use_regressed)
    h_p4 = b1_p4 + b2_p4
    h_dr = calc_dr_p4(b1_p4, b2_p4)

    matched = (tree[f'{higgs}_b1_recojet_pt'] > 0) & (tree[f'{higgs}_b2_recojet_pt'] > 0)

    return dict(
        **{
            f'{higgs}_reco_{var}': matched*getattr(h_p4, var) + (~matched)*(-999)
            for var in ('pt', 'eta', 'phi', 'm')
        },
        **{
            f'{higgs}_reco_dr': matched*h_dr + (~matched)*(-999)
        },
        **{
            f'{higgs}_reco_matched': matched
        }
    )


def reco_genY(tree, y):
    h1_p4 = build_p4(tree, prefix=f'{y.replace("gen_","gen_H1")}_reco')
    h2_p4 = build_p4(tree, prefix=f'{y.replace("gen_","gen_H2")}_reco')
    y_p4 = h1_p4 + h2_p4
    y_dr = calc_dr_p4(h1_p4, h2_p4)
    matched = (tree[f'{y.replace("gen_","gen_H1")}_reco_matched'] & tree[f'{y.replace("gen_","gen_H2")}_reco_matched'])
    return dict(
        **{
            f'{y}_reco_{var}': matched*getattr(y_p4, var) + (~matched)*(-999)
            for var in ('pt', 'eta', 'phi', 'm')
        },
        **{
            f'{y}_reco_dr': matched*y_dr + (~matched)*(-999)
        },
        **{
            f'{y}_reco_matched': matched
        }
    )


def reco_genX(tree):
    y1_p4 = build_p4(tree, prefix='gen_Y1_reco')
    y2_p4 = build_p4(tree, prefix='gen_Y2_reco')
    x_p4 = y1_p4 + y2_p4
    x_dr = calc_dr_p4(y1_p4, y2_p4)
    matched = (tree[f'gen_Y1_reco_matched'] & tree[f'gen_Y2_reco_matched'])
    return dict(
        **{
            f'gen_X_reco_{var}': matched*getattr(x_p4, var) + (~matched)*(-999)
            for var in ('pt', 'eta', 'phi', 'm')
        },
        **{
            f'gen_X_reco_dr': matched*x_dr + (~matched)*(-999)
        },
        **{
            'gen_X_reco_matched': matched
        }
    )


def reco_all(tree,use_regressed=True):
    higgslist = [
        f'gen_{h}{y}'
        for y in ('Y1', 'Y2')
        for h in ('H1', 'H2')
    ]
    for higgs in higgslist:
        tree.extend(**reco_genH(tree, higgs,use_regressed))
    ylist = [
        f'gen_{y}'
        for y in ('Y1', 'Y2')
    ]
    for y in ylist:
        tree.extend(**reco_genY(tree, y))
    tree.extend(**reco_genX(tree))
    return dict()


def resolution(reco, gen):
    res = reco/gen
    return res


def reco_res_all(tree, varlist=('pt', 'eta', 'phi', 'm'), use_regressed=False):
    jetlist = [
        f'gen_{h}{y}_{b}'
        for y in ('Y1', 'Y2')
        for h in ('H1', 'H2')
        for b in ('b1', 'b2')
    ]

    def get_reco_var(jet, var):
        if var == 'pt' and use_regressed:
            var = 'ptRegressed'
        return f'{jet}_recojet_{var}'

    for jet in jetlist:
        tree.extend(
            **{
                f'{jet}_{var}_res': resolution(tree[get_reco_var(jet, var)], tree[f'{jet}_genjet_{var}'])
                for var in varlist
            }
        )
    higgslist = [
        f'gen_{h}{y}'
        for y in ('Y1', 'Y2')
        for h in ('H1', 'H2')
    ]
    for higgs in higgslist:
        tree.extend(
            **{
                f'{higgs}_{var}_res': resolution(tree[f'{higgs}_reco_{var}'], tree[f'{higgs}_{var}'])
                for var in varlist
            }
        )
    ylist = [
        f'gen_{y}'
        for y in ('Y1', 'Y2')
    ]
    for y in ylist:
        tree.extend(
            **{
                f'{y}_{var}_res': resolution(tree[f'{y}_reco_{var}'], tree[f'{y}_{var}'])
                for var in varlist
            }
        )

    tree.extend(
        **{
            f'gen_X_{var}_res': resolution(tree[f'gen_X_reco_{var}'], tree[f'gen_X_{var}'])
            for var in varlist
        }
    )
    return dict()


def make_genjet_variables(tree):
    quarklist = [
        f'gen_{h}{y}_{b}'
        for y in ('Y1', 'Y2')
        for h in ('H1', 'H2')
        for b in ('b1', 'b2')
    ]
    genjets = ak.zip({
        var: ak.concatenate([tree[f'{quark}_genjet_{var}'][:, None]
                            for quark in quarklist], axis=-1)
        for var in ('pt', 'eta', 'phi', 'm')
    })

    recojets = ak.zip({
        var: ak.concatenate([tree[f'{quark}_recojet_{var}'][:, None]
                            for quark in quarklist], axis=-1)
        for var in ('pt', 'eta', 'phi', 'm')
    })

    genjet_genjet_dr = calc_dr(
        genjets.eta[:, :, None], genjets.phi[:, :, None], genjets.eta[:, None], genjets.phi[:, None])
    min_genjet_dr = ak.min(genjet_genjet_dr[genjet_genjet_dr != 0], axis=-1)

    genjet_recojet_dr = calc_dr(
        genjets.eta[:, :, None], genjets.phi[:, :, None], recojets.eta[:, None], recojets.phi[:, None])
    min_recojet_dr = ak.min(genjet_recojet_dr, axis=-1)

    quark_matched = 1*(genjets.pt > 0)
    recojet_matched = 1*(recojets.pt > 0)

    return dict(
        **{
            f'{quark}_genjet_quark_matched': quark_matched[:, i]
            for i, quark in enumerate(quarklist)
        },
        **{
            f'{quark}_genjet_min_genjet_dr': min_genjet_dr[:, i]
            for i, quark in enumerate(quarklist)
        },
        **{
            f'{quark}_genjet_recojet_matched': recojet_matched[:, i]
            for i, quark in enumerate(quarklist)
        },
        **{
            f'{quark}_genjet_min_recojet_dr': min_recojet_dr[:, i]
            for i, quark in enumerate(quarklist)
        },
        **{
            f'n_unmatched_genjet': ak.sum((recojet_matched == 0)[quark_matched == 1], axis=-1),
            f'n_unmatched_genjet_dr4': ak.sum(((recojet_matched == 0) & (min_recojet_dr > 0.4))[quark_matched == 1], axis=-1),
        }
    )
