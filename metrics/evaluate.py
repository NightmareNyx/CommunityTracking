from __future__ import division

import itertools
from collections import OrderedDict
from collections_ import Counter_

from .Bcubed import Bcubed
from .NMI import NMI
from .Omega import Omega


def unravel_tf(dynamic, tfs_len):
    """
    
    :param dynamic: 
    :param tfs_len: 
    :return: dictionary of dictionaries {timeframe:
                                                {
                                                community: [node1, node2...]}}
    """
    comms = {t: {} for t in range(tfs_len)}
    for c, dyn in dynamic.items():
        for node in dyn:
            tf = int(node.rsplit('-', 1)[1][1])
            # node = int(node.rsplit('-', 1)[0])
            node = node.rsplit('-', 1)[0]
            try:
                comms[tf][c].append(node)
            except KeyError:
                comms[tf][c] = [node]
    return remove_duplicate_coms(comms)


def remove_duplicate_coms(communities):
    """
    Removes duplicates from list of lists
    :param communities:
    :return:
    """
    new_comms = {tf: {} for tf in communities.keys()}
    for tf, comms in communities.items():
        unique_coms = [set(c) for c in comms.values()]
        unique_coms = list(comms for comms, _ in itertools.groupby(unique_coms))
        for i, com in enumerate(unique_coms):
            new_comms[tf][i] = list(com)
    return new_comms


def evaluate(ground_truth, method, name, eval, duration):
    if method == {} or method is None:
        nmi_res = 0
        omega_res = 0
        bcubed_p_res = 0
        bcubed_r_res = 0
        bcubed_f1_res = 0
    else:
        ## TEMPORARILY without NMI
        nmi = NMI(ground_truth, method).results
        nmi_res = float("{0:.4f}".format(nmi['NMI<Max>']))
        omega = Omega(ground_truth, method)
        omega_res = float("{0:.4f}".format(omega.omega_score))
        bcubed = Bcubed(ground_truth, method)
        bcubed_p_res = float("{0:.4f}".format(bcubed.precision))
        bcubed_r_res = float("{0:.4f}".format(bcubed.recall))
        bcubed_f1_res = float("{0:.4f}".format(bcubed.fscore))
    results = OrderedDict()
    results["Method"] = [name]
    results["Eval"] = [eval]
    results['NMI'] = [nmi_res]
    results['Omega'] = [omega_res]
    results['Bcubed-Precision'] = [bcubed_p_res]
    results['Bcubed-Recall'] = [bcubed_r_res]
    results['Bcubed-F1'] = [bcubed_f1_res]
    results['Duration'] = [duration]
    return results


def get_results(ground_truth, method, name, tfs_len, eval="dynamic", duration=0):
    results = None
    if eval == "dynamic":
        results = evaluate(ground_truth, method, name, eval, duration)
    elif eval == "sets":
        new_comms1 = {i: set() for i in ground_truth.keys()}
        for i, comm in ground_truth.items():
            for node in comm:
                new_comms1[i].add(node.rsplit('-', 1)[0])
        new_comms2 = {i: set() for i in method.keys()}
        for i, comm in method.items():
            for node in comm:
                new_comms2[i].add(node.rsplit('-', 1)[0])
        results = evaluate(new_comms1, new_comms2, name, eval, duration)
    elif eval == "per_tf":
        new_comms1 = unravel_tf(ground_truth, tfs_len)
        new_comms2 = unravel_tf(method, tfs_len)
        per_tf = []
        for t in range(tfs_len):
            evaluation = evaluate(new_comms1[t], new_comms2[t], name, eval, duration)
            per_tf.append(Counter_(evaluation))
        results = sum(per_tf, Counter_())
        for key in results:
            if all(isinstance(x, str) for x in results[key]):
                results[key] = [results[key][0]]
            else:
                results[key] = [float("{0:.4f}".format(sum(results[key]) / len(per_tf)))]
                # pprint.pprint(dict(f))
                # for k, v in res.iteritems():
                #     print "KEY ", k, " VALUE ", v
    return results


if __name__ == "__main__":
    comms3 = {0: ['1-t0', '2-t0', '3-t0', '4-t0', '1-t1', '2-t1', '3-t1', '4-t1', '1-t2', '2-t2', '3-t2', '4-t2'],
              1: ['11-t1', '12-t1', '13-t1'],
              2: ['5-t2', '6-t2', '7-t2', '5-t0', '6-t0', '7-t0']}
    comms4 = {1: ['1-t0', '2-t0', '3-t0', '4-t0', '1-t1', '2-t1', '3-t1', '4-t1', '1-t2', '2-t2', '3-t2', '4-t2'],
              2: ['11-t1', '12-t1', '13-t1'],
              3: ['5-t2', '6-t2', '7-t2'],
              4: ['5-t0', '6-t0', '7-t0']}
    comms5 = {5: ['5-t0', '6-t0', '7-t0'],
              1: ['1-t0', '2-t0', '3-t0', '4-t0', '1-t1', '2-t1', '3-t1', '4-t1', '1-t2', '2-t2', '3-t2', '4-t2'],
              2: ['11-t1', '12-t1', '13-t1', '5-t0', '6-t0', '7-t0'],
              3: ['5-t0', '6-t0', '7-t0', '5-t2', '6-t2', '7-t2'],
              4: ['5-t0', '7-t0', '6-t0', ]}
    all_res = []
    all_res.append(get_results(comms4, comms5, "Muturank", 3, eval="dynamic"))
    all_res.append(get_results(comms4, comms5, "Muturank", 3, eval="sets"))
    all_res.append(get_results(comms4, comms5, "Muturank", 3, eval="per_tf"))
    results = OrderedDict()
    results["Method"] = []
    results['Eval'] = []
    results['NMI'] = []
    results['Omega'] = []
    results['Bcubed-Precision'] = []
    results['Bcubed-Recall'] = []
    results['Bcubed-F1'] = []
    results['Duration'] = []

    from tabulate import tabulate

    for res in all_res:
        for k, v in res.items():
            results[k].extend(v)
    print(results)
    print(tabulate(dict(results), headers="keys", tablefmt="grid") + "\n")
