import copy
import itertools
from collections import defaultdict, deque

import numpy as np
import pandas as pd
import streamlit as st
from set18buffs import *
from set18champs import *
from set18items import *
from simulator import Simulator
import base64
import pickle

from sim_core import do_experiment_one_extra as do_experiment_one_extra_local

from champion import Champion





def getDPS(results, time):
    dpsFunc = getDPSFunction(results)
    return dpsFunc(time) / time


def dpsSplit(results):
    dps = {"physical": 0, "magical": 0, "true": 0}
    for result in results:
        dps[result[1][1]] += result[1][0]
    total = sum(dps.values(), 0.0)
    if total == 0:
        return {k: 0 for k, v in dps.items()}
    else:
        return {k: v / total for k, v in dps.items()}


def getDPSFunction(results):
    """
    results: iterable of items where
      x_i = a[0]
      y_i = a[1][0]
    Returns f(t): piecewise-linear interpolation of cumulative y vs x.
    - Works with scalars or arrays for t
    - Clamps outside [x_min, x_max] to endpoints (your old fill_value)
    - No SciPy required (np.interp)
    """
    # Extract x, cumulative y
    x = np.asarray([a[0] for a in results], dtype=float)
    y = np.cumsum([a[1][0] for a in results], dtype=float)

    # Guard rails
    if x.size == 0:
        # No data: return constant zero function
        return lambda t: np.zeros_like(np.asarray(t, dtype=float))
    # Ensure x is strictly increasing for interpolation
    order = np.argsort(x)
    x = x[order]
    y = y[order]
    # Collapse duplicate x’s by taking the last y for each x
    uniq, idx = np.unique(x, return_index=True)
    if uniq.size != x.size:
        x = uniq
        y = y[idx]

    x_min, x_max = x[0], x[-1]
    y_min, y_max = y[0], y[-1]

    def f(t):
        t = np.asarray(t, dtype=float)
        # Clamp to bounds then interpolate
        t_clamped = np.clip(t, x_min, x_max)
        out = np.interp(t_clamped, x, y, left=y_min, right=y_max)
        return out

    return f


def createDPSChart(simList):
    for sim in simList:
        print("sim:")
        print(sim)
        dps5s = getDPS(sim[3], 5)
        dps10s = getDPS(sim[3], 10)
        dps15s = getDPS(sim[3], 15)
        print(
            sim[0].name,
            [u.name for u in sim[1]],
            [u.name for u in sim[2]],
            dps5s,
            dps10s,
            dps15s,
            dpsSplit(sim[3]),
        )
        # we want DPS at 5s, DPS at 10s, DPS at 15


def createUltDamageCSV(simLists):
    # Imported here rather than at module scope: this is the only other user of
    # xlsxwriter, and keeping it local means a browser/stlite build does not
    # have to ship the wheel just to import this module.
    import xlsxwriter

    headers_arr = [
        "Champion",
        "Level",
        "Items",
        "Item 1",
        "Item 2",
        "Item 3",
        "Buff 1",
        "Buff 2",
        "Damage to Squishy",
        "Damage to Tank",
        "Damage to Supertank",
    ]
    workbook = xlsxwriter.Workbook("ult_stats.xlsx")
    dpsDict = {}
    newEntryLength = 0
    count = 0
    for simList in simLists:
        count += 1
        worksheet1 = workbook.add_worksheet(
            simList[0][0].name + str(simList[0][0].level) + str(count)
        )
        worksheet1.write_row(0, 0, headers_arr)
        worksheet1.freeze_panes(1, 0)
        worksheet1.autofilter("A1:Z9999")
        for index, sim in enumerate(simList):
            new_entry = []
            # Champion
            new_entry.append(sim[0].name)
            new_entry.append(sim[0].level)

            new_entry.append(len([x for x in sim[1] if x.name != "NoItem"]))

            # Item 1
            new_entry.append(sim[1][0].name)
            new_entry.append(sim[1][1].name)
            new_entry.append(sim[1][2].name)

            # Buff 1
            new_entry.append(sim[2][0].name)
            new_entry.append(sim[2][1].name)

            # DPS at 1s
            dpsAt1 = sim[3][0][1][0]
            dpsAt12 = sim[4][0][1][0]
            dpsAt13 = sim[5][0][1][0]
            # dpsAt1=int(getDPS(sim[3],1))
            # dpsAt12=int(getDPS(sim[4],1))
            # dpsAt13=int(getDPS(sim[5],1))
            new_entry.append(dpsAt1)
            new_entry.append(dpsAt12)
            new_entry.append(dpsAt13)

            #     # phys/magic/true
            #     dps = dpsSplit(sim[3])
            #     new_entry.append(dps['physical'])
            #     new_entry.append(dps['magical'])
            #     new_entry.append(dps['true'])

            #     dpsDict[(sim[0].name, sim[0].level, sim[1][0].name, sim[1][1].name, sim[1][2].name, sim[2][0].name, sim[2][1].name)] = dpsAt1
            worksheet1.write_row(index + 1, 0, new_entry)
        # for index, sim in enumerate(simList):
        #             mainTup = (sim[0].name, sim[0].level, sim[1][0].name, sim[1][1].name, sim[1][2].name, sim[2][0].name, sim[2][1].name)
        #             tuples0 = [(sim[0].name, sim[0].level, "NoItem", sim[1][1].name, sim[1][2].name, sim[2][0].name, sim[2][1].name),
        #                       (sim[0].name, sim[0].level, "NoItem", sim[1][2].name, sim[1][1].name, sim[2][0].name, sim[2][1].name)]
        #             tuples1 = [(sim[0].name, sim[0].level, "NoItem", sim[1][0].name, sim[1][2].name, sim[2][0].name, sim[2][1].name),
        #                       (sim[0].name, sim[0].level, "NoItem", sim[1][2].name, sim[1][0].name, sim[2][0].name, sim[2][1].name)]
        #             tuples2 = [(sim[0].name, sim[0].level, "NoItem", sim[1][0].name, sim[1][1].name, sim[2][0].name, sim[2][1].name),
        #                       (sim[0].name, sim[0].level, "NoItem", sim[1][1].name, sim[1][0].name, sim[2][0].name, sim[2][1].name)]
        #             tuples3 = [(sim[0].name, sim[0].level, sim[1][0].name, sim[1][1].name, sim[1][2].name, "NoItem", sim[2][1].name),
        #                       (sim[0].name, sim[0].level, sim[1][0].name, sim[1][1].name, sim[1][2].name, sim[2][1].name, "NoItem")]
        #             # tuples4 = [(sim[0].name, sim[0].level, sim[1][0].name, sim[1][1].name, sim[1][2].name, sim[2][0].name, "NoItem"),
        #             #            (sim[0].name, sim[0].level, sim[1][0].name, sim[1][1].name, sim[1][2].name, "NoItem", sim[2][0].name)]
        #             for tup in tuples0:
        #                 if tup in dpsDict:
        #                     worksheet1.write(index+1, len(new_entry), round(dpsDict[mainTup] / dpsDict[tup], 2))
        #             for tup in tuples1:
        #                 if tup in dpsDict:
        #                     worksheet1.write(index+1, len(new_entry)+1, round(dpsDict[mainTup] / dpsDict[tup], 2))
        #             for tup in tuples2:
        #                 if tup in dpsDict:
        #                     worksheet1.write(index+1, len(new_entry)+2, round(dpsDict[mainTup] / dpsDict[tup], 2))
        #             for tup in tuples3:
        #                 if tup in dpsDict:
        #                     worksheet1.write(index+1, len(new_entry)+3, round(dpsDict[mainTup] / dpsDict[tup], 2))
        #             # for tup in tuples4:
        #             #     if tup in dpsDict:
        #             #         worksheet1.write(index+1, len(new_entry)+4, round(dpsDict[mainTup] / dpsDict[tup], 2))
    workbook.close()


def addSimListToDF(data_frame, simLists):
    # COLUMNS: for DF we can actually be much less noob about it
    # champion
    # level
    # items 1-3
    # buffs 1-2 (note: we eventually want support for the whole buff tree)
    # isHeadliner
    # % physical/magical/true
    # # casts
    # item 1-3 dps increase
    # headliner dps increase
    # TODO: just modify createdpscsv to use this
    for simList in simLists:
        for index, sim in enumerate(simList):
            new_entry = {}
            new_entry["Name"] = sim[0].name
            new_entry["Level"] = sim[0].level
            new_entry["Num items"] = len([x for x in sim[1] if x.name != "NoItem"])
            new_entry["Item 1"] = sim[1][0].name
            new_entry["Item 2"] = sim[1][1].name
            new_entry["Item 3"] = sim[1][2].name
            new_entry["Buff 1"] = sim[2][0].name
            new_entry["Buff 2"] = sim[2][1].name
            new_entry["DPS at 5s"] = int(getDPS(sim[3], 5))
            new_entry["DPS at 10s"] = int(getDPS(sim[3], 10))
            new_entry["DPS at 15s"] = int(getDPS(sim[3], 15))
            new_entry["DPS at 20s"] = int(getDPS(sim[3], 20))

            dps = dpsSplit(sim[3])
            new_entry["% physical"] = dps["physical"]
            new_entry["% magical"] = dps["magical"]
            new_entry["% true"] = dps["true"]

            new_entry["# Attacks"] = sim[0].numAttacks
            new_entry["# Casts"] = sim[0].numCasts
    return 0


def createDPScsv(simLists):
    """Creates the DPS csv dps_stats.xlsx: This keeps a record of all the different dps combos for a champion.

    Args:
        simLists (List): list of simulation results
    """
    import xlsxwriter

    headers_arr = [
        "Champion",
        "Level",
        "Items",
        "Item 1",
        "Item 2",
        "Item 3",
        "Buff 1",
        "Buff 2",
        "DPS at 5s",
        "DPS at 10s",
        "DPS at 15s",
        "DPS at 20s",
        "% physical",
        "% magical",
        "% true",
        "# Attacks",
        "# Casts",
        "Item 1 DPS Increase",
        "Item 2 DPS Increase",
        "Item 3 DPS Increase",
        "Buff DPS Increase",
    ]
    workbook = xlsxwriter.Workbook("dps_stats.xlsx")
    dpsDict = {}
    newEntryLength = 0
    count = 0
    for simList in simLists:
        worksheet1 = workbook.add_worksheet(
            simList[0][0].name + str(simList[0][0].level)
        )
        worksheet1.write_row(0, 0, headers_arr)
        worksheet1.freeze_panes(1, 0)
        worksheet1.autofilter("A1:Z9999")
        for index, sim in enumerate(simList):
            new_entry = []
            # Champion
            new_entry.append(sim[0].name)
            new_entry.append(sim[0].level)

            new_entry.append(len([x for x in sim[1] if x.name != "NoItem"]))

            # Item 1
            new_entry.append(sim[1][0].name)
            new_entry.append(sim[1][1].name)
            new_entry.append(sim[1][2].name)

            # Buff 1
            new_entry.append(sim[2][0].name)
            new_entry.append(sim[2][1].name)

            # DPS at 5s
            dpsAt5 = int(getDPS(sim[3], 5))
            dpsAt10 = int(getDPS(sim[3], 10))
            dpsAt15 = int(getDPS(sim[3], 15))
            dpsAt20 = int(getDPS(sim[3], 20))
            new_entry.append(dpsAt5)
            new_entry.append(dpsAt10)
            new_entry.append(dpsAt15)
            new_entry.append(dpsAt20)

            # % Physical
            dps = dpsSplit(sim[3])
            # print(dps)
            new_entry.append(dps["physical"])
            new_entry.append(dps["magical"])
            new_entry.append(dps["true"])

            # # Attacks
            new_entry.append(sim[0].numAttacks)
            new_entry.append(sim[0].numCasts)
            newEntryLength = len(new_entry)
            # item1 formula
            # formula = '=J{0} / INDEX(J:J,MATCH(1,(A{0}=A:A)*("NoItem"=D:D)*(G{0}=G:G)*((E{0}=E:E)*(F{0}=F:F)+(E{0}=F:F)*(F{0}=E:E)),0))'.format(index+2)
            # print(formula)

            dpsDict[
                (
                    sim[0].name,
                    sim[0].level,
                    sim[1][0].name,
                    sim[1][1].name,
                    sim[1][2].name,
                    sim[2][0].name,
                    sim[2][1].name,
                )
            ] = dpsAt20
            # if sim[2][0].name == "NoItem":
            #    continue
            worksheet1.write_row(index + 1, 0, new_entry)

        for index, sim in enumerate(simList):
            mainTup = (
                sim[0].name,
                sim[0].level,
                sim[1][0].name,
                sim[1][1].name,
                sim[1][2].name,
                sim[2][0].name,
                sim[2][1].name,
            )
            tuples0 = [
                (
                    sim[0].name,
                    sim[0].level,
                    "NoItem",
                    sim[1][1].name,
                    sim[1][2].name,
                    sim[2][0].name,
                    sim[2][1].name,
                ),
                (
                    sim[0].name,
                    sim[0].level,
                    "NoItem",
                    sim[1][2].name,
                    sim[1][1].name,
                    sim[2][0].name,
                    sim[2][1].name,
                ),
            ]
            tuples1 = [
                (
                    sim[0].name,
                    sim[0].level,
                    "NoItem",
                    sim[1][0].name,
                    sim[1][2].name,
                    sim[2][0].name,
                    sim[2][1].name,
                ),
                (
                    sim[0].name,
                    sim[0].level,
                    "NoItem",
                    sim[1][2].name,
                    sim[1][0].name,
                    sim[2][0].name,
                    sim[2][1].name,
                ),
            ]
            tuples2 = [
                (
                    sim[0].name,
                    sim[0].level,
                    "NoItem",
                    sim[1][0].name,
                    sim[1][1].name,
                    sim[2][0].name,
                    sim[2][1].name,
                ),
                (
                    sim[0].name,
                    sim[0].level,
                    "NoItem",
                    sim[1][1].name,
                    sim[1][0].name,
                    sim[2][0].name,
                    sim[2][1].name,
                ),
            ]
            tuples3 = [
                (
                    sim[0].name,
                    sim[0].level,
                    sim[1][0].name,
                    sim[1][1].name,
                    sim[1][2].name,
                    "NoItem",
                    sim[2][1].name,
                ),
                (
                    sim[0].name,
                    sim[0].level,
                    sim[1][0].name,
                    sim[1][1].name,
                    sim[1][2].name,
                    sim[2][1].name,
                    "NoItem",
                ),
            ]
            tuples4 = [
                (
                    sim[0].name,
                    sim[0].level,
                    sim[1][0].name,
                    sim[1][1].name,
                    sim[1][2].name,
                    sim[2][0].name,
                    "NoItem",
                ),
                (
                    sim[0].name,
                    sim[0].level,
                    sim[1][0].name,
                    sim[1][1].name,
                    sim[1][2].name,
                    "NoItem",
                    sim[2][0].name,
                ),
            ]
            for tup in tuples0:
                if tup in dpsDict:
                    worksheet1.write(
                        index + 1,
                        len(new_entry),
                        round(dpsDict[mainTup] / dpsDict[tup], 2),
                    )
            for tup in tuples1:
                if tup in dpsDict:
                    worksheet1.write(
                        index + 1,
                        len(new_entry) + 1,
                        round(dpsDict[mainTup] / dpsDict[tup], 2),
                    )
            for tup in tuples2:
                if tup in dpsDict:
                    worksheet1.write(
                        index + 1,
                        len(new_entry) + 2,
                        round(dpsDict[mainTup] / dpsDict[tup], 2),
                    )
            for tup in tuples3:
                if tup in dpsDict:
                    worksheet1.write(
                        index + 1,
                        len(new_entry) + 3,
                        round(dpsDict[mainTup] / dpsDict[tup], 2),
                    )
            for tup in tuples4:
                if tup in dpsDict:
                    worksheet1.write(
                        index + 1,
                        len(new_entry) + 4,
                        round(dpsDict[mainTup] / dpsDict[tup], 2),
                    )
    workbook.close()


def doExperiment(champion, opponent, itemList, buffList, t):
    simulator = Simulator()
    simList = []
    for itemCombo in itemList:
        for buffCombo in buffList:
            champ = copy.deepcopy(champion)
            items = copy.deepcopy(itemCombo)
            buffs = copy.deepcopy(buffCombo)
            results1 = simulator.simulate(
                items,
                buffs,
                champ,
                [
                    copy.deepcopy(opponent),
                    copy.deepcopy(opponent),
                    copy.deepcopy(opponent),
                    copy.deepcopy(opponent),
                ],
                t,
            )
            simList.append(
                {"Champ": champ, "Items": items, "Buffs": buffs, "Results": results1}
            )
    print("Finished simulation on {}".format(champion.name))
    return simList


def doExperimentGivenItems(champions, opponent, itemCombo, buffs, t):
    simulator = Simulator()
    simList = []
    for champ in champions:
        champ = copy.deepcopy(champ)
        results1 = simulator.simulate(
            copy.deepcopy(itemCombo),
            copy.deepcopy(buffs),
            champ,
            [copy.deepcopy(opponent) for i in range(8)],
            t,
        )
        simList.append((champ, itemCombo, [buffs], results1))
    return simList
    # return simList


def radiantRefactor(champions, opponent, itemList, t):
    simulator = Simulator()
    simList = []
    # for champ in champions:
    # for item in itemlist
    # to get the radiants
    return 0


# max_entries bounds this: without it, entries only age out after ttl, so a
# burst of distinct configs (different champs/items/buffs/stages) from any
# number of concurrent visitors -- this cache is process-wide, not
# per-session -- can pile up unbounded within that hour.
#
# 10, not 100: the only thing this cache has to hold is "the slices the
# ChampionSelector is currently showing", so that clicking between radio
# options doesn't recompute. Stale entries past that are worth nothing, and
# under stlite this lives in the visitor's browser tab, where memory is the
# scarce resource -- 100 entries was a ceiling in the hundreds of MB on
# hardware that may not have it.
#
# The floor is the number of radio options (8 with Blackthorn fielded).
# ChampionSelector's WARM_OTHER_SLICES loop writes one entry per slice after
# each render, so anything below that count would evict the slice on screen
# and make every click a fresh sweep. 10 leaves a little headroom; measured,
# all 8 slices for one champion total ~0.5MB.
@st.cache_data(ttl=3600, max_entries=10)
def doExperimentOneExtraWrapped(
    champion_pickle: str,
    opponent_pickle: str,
    item_list_pickle: str,
    buff_list_pickle: str,
    t: float,
    frameRate: int,
    run_blackthorn: bool = True,
):
    # The arguments arrive pickled because that is what makes them hashable
    # for st.cache_data, not because they are going anywhere: unpickle and run.
    champion_obj = pickle.loads(base64.b64decode(champion_pickle))
    opponent_obj = pickle.loads(base64.b64decode(opponent_pickle))
    _itemList = pickle.loads(base64.b64decode(item_list_pickle))
    _buffList = pickle.loads(base64.b64decode(buff_list_pickle))

    return do_experiment_one_extra_local(
        champion_obj, opponent_obj, _itemList, _buffList, t, frameRate,
        run_blackthorn=run_blackthorn,
    )


# @st.cache_data(hash_funcs={Champion: hash_func})
def doExperimentOneExtra(
    champion: Champion,
    opponent: Champion,
    itemList,
    buffList,
    t,
    frameRate=30,
    run_blackthorn=True,
):
    # Serialize before calling cached function
    champion_pickle = base64.b64encode(pickle.dumps(champion)).decode("utf-8")
    opponent_pickle = base64.b64encode(pickle.dumps(opponent)).decode("utf-8")
    item_list_pickle = base64.b64encode(pickle.dumps(itemList)).decode("utf-8")
    buff_list_pickle = base64.b64encode(pickle.dumps(buffList)).decode("utf-8")

    return doExperimentOneExtraWrapped(
        champion_pickle,
        opponent_pickle,
        item_list_pickle,
        buff_list_pickle,
        t,
        frameRate,
        run_blackthorn,
    )
    # this is done with champ already with a set of items
    # simulator = Simulator()
    # simList = []

    # for item in itemList:
    #   champ = copy.deepcopy(champion)
    #   results = simulator.simulate([copy.deepcopy(item)], [], champ,
    #     [copy.deepcopy(opponent) for i in range(8)], t)
    #   simList.append({"Champ": champ, "Extra": item, "Results": results})
    # for buff in buffList:
    #   champ = copy.deepcopy(champion)
    #   equal_buffs = [champ_buff for champ_buff in champ.items if champ_buff.name.split(" ")[0] == buff.name.split(" ")[0]]
    #   for equal_buff in equal_buffs:
    #     champ.items.remove(equal_buff)
    #   results = simulator.simulate([], [copy.deepcopy(buff)], champ,
    #                                [copy.deepcopy(opponent) for i in range(8)], t)
    #   simList.append({"Champ": champ, "Extra": buff, "Results": results})

    # return simList


def createUnitDPSTable(simLists):
    entries = []
    dpsDict = {}
    # for simList in simLists:
    for index, sim in enumerate(simLists):
        new_entry = {}
        new_entry["Name"] = sim["Champ"].name
        new_entry["Level"] = sim["Champ"].level
        new_entry["# ltems"] = len([x for x in sim["Items"] if x.name != "NoItem"])
        sorted_items = sorted([item.name for item in sim["Items"]])
        sorted_buffs = sorted([buff.name for buff in sim["Buffs"]])
        for index, item in enumerate(sorted_items):
            new_entry["Item {}".format(index + 1)] = item
        for index, buff in enumerate(sorted_buffs):
            new_entry["Buff {}".format(index + 1)] = buff
        # st.write(sim[2])
        # for i in range(len(sim[2])):
        #   new_entry['Buff{}'.format(i)].append(sim[2][i].name)

        # DPS at 5s
        for t in [5, 10, 15, 20, 25]:
            new_entry["DPS at {}".format(t)] = int(getDPS(sim["Results"], t))

        # dps split
        dps = dpsSplit(sim["Results"])

        # new_entry['% Physical'] = dps['physical']
        # new_entry['% Magical'] = dps['magical']
        # new_entry['% True'] = dps['true']
        entries.append(new_entry)
        dict_key = (
            (new_entry["Name"], new_entry["Level"])
            + tuple(item for item in sorted_items)
            + tuple(buff for buff in sorted_buffs)
        )
        dpsDict[dict_key] = new_entry["DPS at 25"]

    for entry in entries:
        items = [entry[col] for col in list(entry.keys()) if "Item" in col]
        buffs = [entry[col] for col in list(entry.keys()) if "Buff" in col]
        for index, item in enumerate(items):
            noitem = sorted(items[0:index] + ["NoItem"] + items[index + 1 :])
            noitem_key = (entry["Name"], entry["Level"]) + tuple(noitem) + tuple(buffs)
            item_key = (entry["Name"], entry["Level"]) + tuple(items) + tuple(buffs)
            entry["Item {} DPS".format(index + 1)] = round(
                (
                    dpsDict[item_key] / dpsDict[noitem_key]
                    if dpsDict[noitem_key] != 0
                    else 0
                ),
                2,
            )

        # should condense this somehow
        for index, buff in enumerate(buffs):
            nobuff = sorted(buffs[0:index] + ["NoItem"] + buffs[index + 1 :])
            nobuff_key = (entry["Name"], entry["Level"]) + tuple(items) + tuple(nobuff)
            buff_key = (entry["Name"], entry["Level"]) + tuple(items) + tuple(buffs)
            entry["Buff {} DPS".format(index + 1)] = round(
                (
                    dpsDict[buff_key] / dpsDict[nobuff_key]
                    if dpsDict[nobuff_key] != 0
                    else 0
                ),
                2,
            )

    df = pd.DataFrame(entries)
    return df


def createSelectorDPSTable(simLists):
    entries = []
    dpsDict = {}
    # for simList in simLists:
    for index, sim in enumerate(simLists):

        new_entry = {}
        new_entry["Name"] = sim["Champ"].name
        new_entry["Level"] = sim["Champ"].level

        # sorted_items = sorted([item.name for item in sim['Items']])
        # sorted_buffs = sorted([buff.name for buff in sim['Buffs']])

        # for index, item in enumerate(sorted_items):
        new_entry["Extra"] = sim["Extra"].name
        # print(new_entry["Extra"])
        new_entry["Extra class name"] = type(sim["Extra"]).__name__
        # Blackthorn rows carry the sacrifice broken out into its own columns;
        # the ChampionSelector shows those in place of "Extra". Rows from any
        # other sweep leave them blank.
        for column, value in sim.get("Blackthorn", {}).items():
            new_entry[column] = value
        # DPS at 5s
        for t in [5, 10, 15, 20, 25]:
            res = getDPS(sim["Results"], t)
            if res > 10:
                res = int(res)
            new_entry["DPS at {}".format(t)] = res

        # dps split
        dps = dpsSplit(sim["Results"])

        # new_entry['% Physical'] = dps['physical']
        # new_entry['% Magical'] = dps['magical']
        # new_entry['% True'] = dps['true']
        entries.append(new_entry)
        dict_key = (new_entry["Name"], new_entry["Level"], new_entry["Extra"])
        dpsDict[dict_key] = {}
        for i in [5, 10, 15, 20, 25]:
            dpsDict[dict_key][i] = new_entry["DPS at {}".format(i)]

    for entry in entries:
        items = [entry["Extra"]]
        for index, item in enumerate(items):

            noitem_key = (entry["Name"], entry["Level"], "NoItem")
            nobuff_key = (entry["Name"], entry["Level"], "NoItem")
            item_key = (entry["Name"], entry["Level"], entry["Extra"])
            for i in [5, 10, 15, 20, 25]:
                entry["Extra DPS ({}s)".format(i)] = 0
                if item_key in dpsDict and noitem_key in dpsDict:
                    entry["Extra DPS ({}s)".format(i)] = round(
                        (
                            dpsDict[item_key][i] / dpsDict[noitem_key][i]
                            if dpsDict[noitem_key][i] != 0
                            else 0
                        ),
                        2,
                    )
                elif item_key in dpsDict and nobuff_key in dpsDict:
                    entry["Extra DPS ({}s)".format(i)] = round(
                        (
                            dpsDict[item_key][i] / dpsDict[noitem_key][i]
                            if dpsDict[noitem_key][i] != 0
                            else 0
                        ),
                        2,
                    )

    df = pd.DataFrame(entries)
    df = df.sort_values(by=["Extra DPS (25s)"], ascending=False)
    return df


def createDPSTable(simLists):
    entries = []
    # for simList in simLists:
    for index, sim in enumerate(simLists):

        new_entry = {}
        new_entry["Name"] = sim[0].name
        new_entry["Level"] = sim[0].level

        # DPS at 5s
        for t in [5, 10, 15, 20, 25]:
            new_entry["DPS at {}".format(t)] = int(getDPS(sim[3], t))

        # dps split
        dps = dpsSplit(sim[3])

        new_entry["% Physical"] = dps["physical"]
        new_entry["% Magical"] = dps["magical"]
        new_entry["% True"] = dps["true"]
        entries.append(new_entry)
    df = pd.DataFrame(entries)

    return df


def items_list(items):
    col1, col2, col3 = st.columns(3)
    with col1:
        item1 = st.selectbox("Item 1", items)
    with col2:
        item2 = st.selectbox("Item 2", items)
    with col3:
        item3 = st.selectbox("Item 3", items)
    return item1, item2, item3


def getComboList(items, comboSize, replace=True):
    if replace:
        itemComboList = itertools.combinations_with_replacement(items, comboSize)
    else:
        itemComboList = itertools.combinations(items, comboSize)
        itemComboList = itertools.chain(
            itemComboList, iter([[buffs.NoBuff(0, []), buffs.NoBuff(0, [])]])
        )
    return [list(a) for a in itemComboList]


def enemy_list(key):
    col1, col2, col3 = st.columns(3)
    with col1:
        hp = st.number_input(
            "Enemy HP", min_value=1, max_value=99999, value=1800, key=key + "1"
        )
    with col2:
        armor = st.number_input(
            "Enemy Armor", min_value=0, max_value=99999, value=100, key=key + "2"
        )
    with col3:
        mr = st.number_input(
            "Enemy MR", min_value=0, max_value=99999, value=100, key=key + "3"
        )
    return hp, armor, mr


def sniperTab():
    sniper_items = [
        "NoItem",
        "Rageblade",
        "IE",
        "HoJ",
        "GS",
        "RH",
        "LW",
        "Shojin",
        "DB",
        "Nashors",
        "Guardbreaker",
    ]
    senna_buffs = ["Sniper", "ASBuff", "NoBuff"]

    ashe_buffs = ["Porcelain", "NoBuff"]

    st.header("Items")

    item1, item2, item3 = items_list(sniper_items)

    # Global Buffs
    st.header("Global Buffs")
    item_cols = st.columns([5, 1])
    num_buffs = st.slider("Number of Buffs", min_value=1, max_value=4)

    buffs = []
    for n in range(num_buffs):
        with item_cols[0]:
            buff1 = st.selectbox(
                "Buff {}".format(n + 1), senna_buffs, key="Buff {}".format(n)
            )
        with item_cols[1]:
            buff1level = st.selectbox(
                "Level", globals()[buff1].levels, key="Buff lvl {}".format(n)
            )
        buffs.append((buff1, buff1level))

    st.header("Senna")

    senna_targets = st.slider("number of targets", min_value=1, max_value=3)
    # given a set of items and buffs
    # do it on these champions
    sennas = [Senna(i) for i in range(1, 4)]
    for senna in sennas:
        senna.num_targets = senna_targets

    st.header("Ashe")

    enemy = DummyTank(1)

    st.header("Enemy")

    hp, armor, mr = enemy_list("Snipers")

    enemy.hp.base = hp
    enemy.armor.base = armor
    enemy.mr.base = mr

    kogs = [Kogmaw(i) for i in range(1, 4)]
    aphelioses = [Aphelios(i) for i in range(1, 4)]
    ashes = [Ashe(i) for i in range(1, 3)]
    champs = kogs + sennas + aphelioses + ashes

    # Add in global buffs
    for champ in champs:
        for buff, level in buffs:
            champ.items.append(globals()[buff](level, []))

    # st.write("asdf")
    # st.write(buffs)

    simLists = doExperimentGivenItems(
        champs,
        enemy,
        [globals()[item1](), globals()[item2](), globals()[item3]()],
        [globals()[buff](level) for buff, level in buffs],
        30,
    )
    # df.write(simLists)
    df = createDPSTable(simLists)
    st.write(df)


def fatedTab():
    fated_items = [
        "NoItem",
        "Rageblade",
        "IE",
        "HoJ",
        "GS",
        "Rab",
        "Guardbreaker",
        "Shojin",
        "Archangels",
        "Nashors",
        "JG",
        "Blue",
        "Shiv",
    ]
    fated_buffs = ["Fated Ahri", "Fated Syndra", "Fated Kindred", "Baboom", "NoBuff"]
    kindred_buffs = ["Dryad", "Reaper", "NoBuff"]

    with st.sidebar:
        st.header("Items")
        item1, item2, item3 = items_list(fated_items)

        # Global Buffs
        st.header("Global Buffs")
        item_cols = st.columns([5, 1])
        num_buffs = st.slider(
            "Number of Buffs", min_value=1, max_value=4, key="Fated Slider", value=2
        )

        buffs = []
        for n in range(num_buffs):
            with item_cols[0]:
                buff1 = st.selectbox(
                    "Buff {}".format(n + 1), fated_buffs, key="Fated Buff {}".format(n)
                )
                buff_name = "Fated" if "Fated" in buff1 else buff1
            with item_cols[1]:
                buff1level = st.selectbox(
                    "Level",
                    globals()[buff_name].levels,
                    key="Fated Buff lvl {}".format(n),
                )
            buffs.append((buff1, buff1level))

        enemy = DummyTank(1)

        st.header("Kindred")
        item_cols = st.columns([5, 1])
        num_kindred_buffs = st.slider(
            "Number of Buffs", min_value=1, max_value=4, key="Kindred Slider", value=2
        )

        buffs_for_kindred = []
        for n in range(num_kindred_buffs):
            with item_cols[0]:
                buff1 = st.selectbox(
                    "Buff {}".format(n + 1),
                    kindred_buffs,
                    key="Kindred Buff {}".format(n),
                )
            with item_cols[1]:
                buff1level = st.selectbox(
                    "Level",
                    globals()[buff1].levels,
                    key="Kindred Buff lvl {}".format(n),
                )
            buffs_for_kindred.append((buff1, buff1level))

        st.header("Enemy")

        hp, armor, mr = enemy_list("Fated")

    enemy.hp.base = hp
    enemy.armor.base = armor
    enemy.mr.base = mr

    ahris = [Ahri(i) for i in range(1, 4)]
    kindreds = [Kindred(i) for i in range(1, 4)]

    for kindred in kindreds:
        for buff, level in buffs_for_kindred:
            kindred.items.append(globals()[buff](level, []))

    syndras = [Syndra(i) for i in range(1, 3)]

    champs = ahris + kindreds + syndras
    # Add in global buffs
    for champ in champs:
        for buff, level in buffs:
            param = buff.split(" ")[1] if "Fated" in buff else None
            champ.items.append(globals()[buff.split(" ")[0]](level, [param]))

    simLists = doExperimentGivenItems(
        champs,
        enemy,
        [globals()[item1](), globals()[item2](), globals()[item3]()],
        [globals()[buff](level) for buff, level in buffs],
        30,
    )
    # df.write(simLists)

    # Items
    st.write("Item 1: {}".format(item1))
    st.write("Item 2: {}".format(item2))
    st.write("Item 3: {}".format(item3))

    df = createDPSTable(simLists)
    st.write(df)
    return 0


def constructCSV():
    t = 30

    tab1, tab2, tab3 = st.tabs(["Snipers", "Fated", "Ashe"])

    with tab1:
        sniperTab()
    with tab2:
        fatedTab()
    with tab3:
        asheTab()


if __name__ == "__main__":
    st.set_page_config(layout="wide")

    constructCSV()
    # constructGraph()
    # ultCSV()
